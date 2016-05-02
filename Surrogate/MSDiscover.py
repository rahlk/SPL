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

import os.path
import sys

sys.dont_write_btyecode = True
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spl_address = [i for i in sys.path if i.endswith('/SPL')][0]

from deap import base, creator, tools
from FeatureModel.ftmodel import FTModel
from FeatureModel.discoverer import Discoverer
from model import *
import DEAP_EA.DEAP_tools.stat_parts as stat_parts
import time
import random
import pickle


class MSDiscover(Discoverer):
    def __init__(self, feature_model):
        # check whether 'conVio' set as an objective
        if 'conVio' not in [o.name for o in feature_model.obj]:
            name = feature_model.name
            self.ft = FTModel(name, num_of_attached_objs=len(feature_model) - 2, setConVioAsObj=True)
        else:
            self.ft = feature_model

        creator.create("FitnessMin", base.Fitness, weights=[-1.0] * self.ft.objNum)
        creator.create("Individual", list, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()

        toolbox.register("evaluate", self.eval_func)

        stats = tools.Statistics(lambda ind: ind)

        """load the optimal in theory (including the not valid individuals)"""
        with open('{0}/input/hof_ibea/{1}.hof'.format(spl_address, self.ft.name), 'r') as f:
            optimal_in_theory = pickle.load(f)
            optimal_in_theory = [o.fitness.values for o in optimal_in_theory]
        stats.register("hv|spread|igd|frontier#|valid#",
                       stat_parts.stat_basing_on_pop,
                       optimal_in_theory=optimal_in_theory)

        stats.register("timestamp", stat_parts.timestamp, t=time.time())

        logbook = tools.Logbook()
        logbook.header = "gen", "evals", "hv|spread|igd|frontier#|valid#", "timestamp"

        self.toolbox = toolbox
        self.stats = stats
        self.logbook = logbook

        self.ms_configurations = {
            'NGEN': 5000,
            'MU': 100,
            'CXPB': 0.9,
            'MutateRate': 0.05,
            'MatingThreshold': 0.15,
        }

    def gen_valid_one(self):
        assert False, "Do not use this function. Function not provided at this time."
        pass

    def eval_func(self, dec_l, NeedCheckTreeStructure=False):
        can = o(decs=dec_l)
        self.ft.eval(can)
        if not NeedCheckTreeStructure:
            can.correct_ft = True
        is_valid_ind = self.ft.ok(can)
        return tuple(can.fitness), is_valid_ind

    @staticmethod
    def bit_flip_mutate(individual, mutate_rate):
        for i in xrange(len(individual)):
            if random.random() < mutate_rate:
                individual[i] = 1 - individual[i]
                del individual.fitness.values
        return individual,

    def evaluate_pop(self, pop):
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in pop if not ind.fitness.valid]
        fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values, ind.fitness.correct = fit
            ind.fitness.correct_ft = True
        return pop, len(invalid_ind)

    def run(self):
        raise NotImplementedError