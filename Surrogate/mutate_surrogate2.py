from __future__ import division
from __init__ import *
from random import choice, randint, shuffle
from os import sys
from FeatureModel.discoverer import Discoverer
from FeatureModel.ftmodel import FTModel
import itertools
import copy
import learner
import pareto
import logging
import pdb
import traceback
import time
import UNIVERSE


__author__ = "Jianfeng Chen"
__copyright__ = "Copyright (C) 2016 Jianfeng Chen"
__license__ = "MIT"
__version__ = "1.4"
__email__ = "jchen37@ncsu.edu"


class ConstraintConflict(Exception):
    def __init__(self, node, cant_set):
        self.node = node
        self.cant_set = cant_set

    def __str__(self):
        return repr(self.node)


class MutateSurrogateEngine2(Discoverer):
    def __init__(self, feature_model):
        time_init = time.time()
        # load the model
        self.ft_model = feature_model
        self.ft_tree = self.ft_model.ft
        self.name = self.ft_model.name
        self.var_rank_dict = dict()
        logging.info("model %s load successfully." % self.name)

        '''We are using V2 engine here!! (guarantee valid)'''
        # TODO Turn off here when testing
        # pre_surrogate.write_random_individuals(self.name, 100, contain_non_leaf=True)

        logging.info("carts preparation for model %s load successfully.\nTIME CONSUMING: %d\n" %
                     (self.name, time.time() - time_init))

    def _can_set(self, after_set_filled_list):
        # checking basing on the feature constraints
        for constraint in self.ft_tree.con:
            if constraint.is_violated(self.ft_tree, after_set_filled_list):
                return False
        return True

    def best_attr_setting(self, curious_indices, g_d=0, g_u=0, rebuild=False):

        """
        what is the best settings for a flexible clusters? Answer this using the CART learner
        :param curious_indices: indices of the flexible cluster
        :param g_d: for groups only
        :param g_u: for groups only
        :param rebuild: build the learner again?
        :return: a generator
        """
        sn = hash(tuple(curious_indices))

        def _get_clf4_one_obj(obj_index):
            return learner.get_cart(self.name, obj_index, curious_indices)

        def _dec2bin_list(decimal, total_bits):
            return map(int, '{0:b}'.format(decimal).zfill(total_bits))

        if rebuild:
            self.var_rank_dict.pop(sn, None)

        if sn not in self.var_rank_dict:
            clfs = map(_get_clf4_one_obj, range(self.ft_model.objNum))
            self.var_rank_dict[sn] = dict()

            # TODO how to rank this? -- using pareto first. then using the second layer...
            n = len(curious_indices)
            all_possibilities = []
            if g_d == 0 and g_u == 0:  # not group clusters
                for decimal in range(2 ** n):  # enumerate all possibilities TODO for the groups handing more here
                    instance = [0] * self.ft_tree.featureNum
                    trying = _dec2bin_list(decimal, n)
                    for ts, t in zip(trying, curious_indices):
                        instance[t] = ts
                    all_possibilities.append(instance)
            else:
                # flexible group
                bit_indicator = range(len(curious_indices))
                for select_bit_len in range(g_d, g_u+1):
                    for select_bit in itertools.combinations(bit_indicator, select_bit_len):
                        instance = [0] * self.ft_tree.featureNum
                        for bit in select_bit:
                            instance[curious_indices[bit]] = 1
                        all_possibilities.append(instance)

            predict_os = []
            for clf in clfs:
                predict_os.append(map(lambda x: round(x, 1), clf.predict(all_possibilities).tolist()))  # FORCE TRUNK

            predict_os = map(list, zip(*predict_os))
            non_dominated = pareto.eps_sort(predict_os)
            self.var_rank_dict[sn]['all_os'] = predict_os
            self.var_rank_dict[sn]['all_os_copy'] = copy.deepcopy(predict_os)
            self.var_rank_dict[sn]['nd'] = non_dominated
            self.var_rank_dict[sn]['used'] = []

        if sn in self.var_rank_dict:
            while True:
                nd = self.var_rank_dict[sn]['nd']
                all_os = self.var_rank_dict[sn]['all_os']
                if nd[0] not in all_os:
                    del nd[0]
                if not nd:
                    assert self.var_rank_dict[sn]['all_os'], "ERROR: no more candidates available :("
                    self.var_rank_dict[sn]['nd'] = pareto.eps_sort(self.var_rank_dict[sn]['all_os'])
                    nd = self.var_rank_dict[sn]['nd']
                indices = [i for i,x in enumerate(self.var_rank_dict[sn]['all_os_copy']) if x == nd[0]]
                for index in indices:
                    all_os.remove(nd[0])
                    yield _dec2bin_list(index, len(curious_indices))

    def bfs(self, filled_list):
        visited, queue = set(), [self.ft_tree.root]
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                try:
                    filled_list, childs = self.mutate_node(vertex, filled_list)
                except ConstraintConflict as bb:
                    pdb.set_trace()
                queue.extend(childs)
        return filled_list

    def mutate_node(self, node, filled_list):
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
            best_gen = self.best_attr_setting(curious_indices, g_d, g_u)

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
                    bit_setting = best_gen.next()
                except Exception:
                    raise ConstraintConflict(node, cant_set=1)

                for index, bit in zip(curious_indices, bit_setting):
                    filled_list[index] = bit

            if self._can_set(filled_list):
                return filled_list, m_child + g_child + o_child

    def gen_valid_one(self):
        filled_list = [-1] * self.ft_tree.featureNum
        filled_list[0] = 1  # let root be 1
        self.bfs(filled_list)
        # self.mutate_node(self.ft_tree.root, filled_list)
        return filled_list
        # pdb.set_trace()


def test_one_model(model):
    UNIVERSE.FT_EVAL_COUNTER = 0
    engine = MutateSurrogateEngine2(FTModel(model, setConVioAsObj=False))
    alpha = engine.gen_valid_one()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        to_test_models = [
            # 'simple',
            'webportal',
            # 'cellphone',
            # 'eshop',
            # 'eis',
        ]
        for model in to_test_models:
            test_one_model(model)
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)