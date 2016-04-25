#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2016, Jianfeng Chen <jchen37@ncsu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.


from __future__ import division

import copy
import logging
import pdb
import time
from operator import itemgetter

import universe

import pre_surrogate
from FeatureModel.discoverer import Discoverer
from FeatureModel.ftmodel import FTModel
from __init__ import *
from model import candidate
from tools import pareto


class ConstraintConflict(Exception):
    def __init__(self, node, cant_set):
        self.node = node
        self.cant_set = cant_set

    def __str__(self):
        return repr(self.node)


class PreCanVar(object):
    def __init__(self, var):
        self.var = var

    def __eq__(self, other):
        others = other if type(other) is list else other.var
        for i, j in zip(self.var, others):
            if i == -1 or j == -1:
                continue
            if i != j:
                return False
        return True

    def is_compatible(self, other):
        return self == other

    def __repr__(self):
        return str(self.var)

    def __getitem__(self, item):
        return self.var[item]

    def __setitem__(self, i, v):
        self.var[i] = v

    def __iter__(self):
        return iter(self.var)

    def __hash__(self):
        return hash(tuple(self.var))

    def tolist(self):
        return self.var


class MutateSurrogateEngine3(Discoverer):
    def __init__(self, feature_model, regenerate_init=False):
        time_init = time.time()
        # load the model
        self.ft_model = feature_model
        self.ft_tree = self.ft_model.ft
        self.name = self.ft_model.name
        logging.info("model %s load successfully." % self.name)

        if regenerate_init:
            '''We are using V2 engine here!! (guarantee valid)'''
            pre_surrogate.write_random_individuals(self.name, 100, contain_non_leaf=True)

        # fetch pre_cans
        with open(project_path+'/surrogate_data/'+self.name+'.raw', 'r') as f:
            raw_data = f.read().splitlines()[1:]
            raw_data = map(lambda x:x.split(','), raw_data)

            def _str2num(x): return int(x) if x.isdigit() else float(x)

            for r_i, r in enumerate(raw_data):
                raw_data[r_i] = map(_str2num, r)

            var_num = self.ft_tree.featureNum
            var_table = [PreCanVar(r[:var_num]) for r in raw_data]
            obj_table = [r[var_num:] for r in raw_data]

        self.pre_cans = zip(var_table, obj_table)
        logging.info("carts preparation for model %s load successfully.\nTIME CONSUMING: %d\n" %
                     (self.name, time.time() - time_init))

    @staticmethod
    def non_dominate_sort(obj_table):
        """
        :param obj_table:
        :return: list of list list [[layer0],[layer1],...]
        """
        # TODO using fast non-dominated sort in NSGA2 or import from the escpy
        obj = copy.deepcopy(obj_table)
        result = []
        while obj:
            ps = pareto.eps_sort(obj)
            layer = [i for i, p in enumerate(obj_table) if p in ps]
            result.append(layer)
            obj = [o for o in obj if o not in ps]
        return result

    def _can_set(self, after_set_filled_list):
        # checking basing on the feature constraints
        for constraint in self.ft_tree.con:
            if constraint.is_violated(self.ft_tree, after_set_filled_list):
                return False
        return True

    @staticmethod
    def sorted_by_frequency(lst):
        """
        group and sort the list by frequency
        :param lst:
        :return: sorted list. each element format by: e, frequency
        """
        hist = [(i, lst.count(i)) for i in set(lst)]
        return sorted(hist, key=lambda x: x[1], reverse=True)

    def best_attr_setting(self, curious_indices, filled_list):
        """
        which setting should be chosen basing on the curring filled_list?
        :param curious_indices:
        :param filled_list:
        :return: the best setting
        """
        to_check_objs, correspond_settings = [], []
        for settings, objs in self.pre_cans:
            if settings.is_compatible(filled_list):
                to_check_objs.append(objs)
                correspond_settings.append(settings)

        indicates = self.non_dominate_sort(to_check_objs)

        for rank_group in indicates:
            # TODO yield order?!
            samples_all = itemgetter(*rank_group)(correspond_settings)
            samples_part = map(lambda x: itemgetter(*curious_indices)(x), samples_all)

            for sp in self.sorted_by_frequency(samples_part):
                settings, frequency = list(sp[0]), sp[1]
                yield settings

    @staticmethod
    def _mutable_parent(node):
        parent = node.parent
        while parent:
            if parent.node_type is 'o':
                return parent
            parent = parent.parent

    def bfs(self, filled_list):
        visited, queue = [], [self.ft_tree.root]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                try:
                    filled_list, children = self.mutate_node(vertex, filled_list)
                    visited.append(vertex)
                    queue.extend(children)
                except ConstraintConflict as cc:
                    mutate_again_node = self._mutable_parent(cc.node).parent
                    index1 = visited.index(mutate_again_node)
                    index2 = visited.index(mutate_again_node.children[0])

                    queue = visited[index1:index2+1]
                    visited = visited[:index1]
                    print 'we are in trouble'
                    cc.cant_set
            # print visited
        return filled_list

    def mutate_node(self, node, filled_list, trap_dict=dict()):
        node_loc = self.ft_tree.find_fea_index(node)
        node_type = node.node_type
        node_value = filled_list[node_loc]

        if node_value == 0:
            # pdb.set_trace()
            self.ft_tree.fill_subtree_0(node, filled_list)
            if not self._can_set(filled_list):
                raise ConstraintConflict(node, cant_set=0)
            return filled_list, []

        '''otherwise, current node is required, then assign the value of its children'''
        m_child = [c for c in node.children if c.node_type in ['r', 'm', 'g']]
        g_child = [c for c in node.children if c.node_type == '']
        o_child = [c for c in node.children if c.node_type == 'o']
        filled_list_copy = [fl for fl in filled_list]  # make a duplicate

        '''
        children setting sorting
        using decision tree technique. Train data from the valid candidates
        '''
        if node_type is 'g':
            g_u, g_d = node.g_u, node.g_d
        else:
            g_u = g_d = 0

        if o_child or g_child:
            curious_indices = map(self.ft_tree.find_fea_index, o_child+g_child)
            best_gen = self.best_attr_setting(curious_indices, filled_list)

        # TODO all possible ?
        while True:
            filled_list = [flc for flc in filled_list_copy]  # recover

            for m in m_child:
                m_i = self.ft_tree.find_fea_index(m)
                filled_list[m_i] = 1

            # we have flexible choices here
            if o_child or g_child:
                # TODO support for both o_child and g_child...
                try:
                    correct = False
                    while not correct:
                        bit_setting = best_gen.next()
                        for ci, bs in zip(curious_indices, bit_setting):
                            if ci in trap_dict and trap_dict[ci] == bs:
                                pass
                            else:
                                correct = True
                                break
                except Exception:
                    raise ConstraintConflict(node, cant_set=1)

                for index, bit in zip(curious_indices, bit_setting):
                    filled_list[index] = bit

            if self._can_set(filled_list):
                return filled_list, m_child + g_child + o_child

    def _fetch_leaves(self, fulfill):
        r = []
        for x in self.ft_tree.leaves:
            index = self.ft_tree.features.index(x)
            r.append(fulfill[index])
        return r

    def gen_valid_one(self):
        filled_list = [-1] * self.ft_tree.featureNum
        filled_list[0] = 1  # let root be 1
        filled_list = self.bfs(filled_list)
        leaves = self._fetch_leaves(filled_list)

        can = candidate(decs=leaves)
        can.fulfill = filled_list
        return can


def test_one_model(model):
    universe.FT_EVAL_COUNTER = 0
    while True:
        engine = MutateSurrogateEngine3(FTModel(model, setConVioAsObj=False), regenerate_init=False)
        alpha = engine.gen_valid_one()
        engine.ft_model.eval(alpha)
        print alpha

    pdb.set_trace()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        to_test_models = [
            # 'simple',
            # 'webportal',
            # 'cellphone',
            'eshop',
            # 'eis',
        ]
        for model in to_test_models:
            test_one_model(model)
    except:
        type, value, tb = sys.exc_info()
        # traceback.print_exc()
        # pdb.post_mortem(tb)
