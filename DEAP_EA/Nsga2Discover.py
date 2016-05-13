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

from deap import tools
from FeatureModel.FeatureModel import FeatureModel, FTModelNovelRep
from DEAP_EA.DEAP_tools.EADiscover import EADiscover
import DEAP_tools.stat_parts as stat_parts
import random
import pdb


class Nsga2Discover(EADiscover):
    def __init__(self, feature_model):
        super(Nsga2Discover, self).__init__(feature_model)

        self.toolbox.register(
            "mate",
            tools.cxTwoPoint)

        self.toolbox.register(
            "mutate",
            self.bit_flip_mutate,
            mutate_rate=self.ea_configurations['MutateRate'])

        self.toolbox.register("select", tools.selNSGA2)

        self.alg_name = 'NSGA2'

    def run(self, record_hof=False, one_puls_n=False):
        toolbox = self.toolbox

        NGEN = self.ea_configurations['NGEN']
        MU = self.ea_configurations['MU']
        CXPB = self.ea_configurations['CXPB']

        pop = toolbox.population(n=MU)
        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness
        self.record(pop, 0, evals, record_hof)

        for gen in range(1, NGEN):
            # print gen

            # vary the population
            tools.emo.assignCrowdingDist(pop)
            offspring = tools.selTournamentDCD(pop, len(pop))
            offspring = [toolbox.clone(ind) for ind in offspring]

            for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
                if random.random() <= CXPB:
                    toolbox.mate(ind1, ind2)

                toolbox.mutate(ind1)
                toolbox.mutate(ind2)
                del ind1.fitness.values, ind2.fitness.values

            _, evals = self.evaluate_pop(offspring)   # Evaluate the offspring with an invalid fitness

            # Select the next generation population
            # Select the next generation parents
            if one_puls_n:
                pop[:] = self.one_plus_n_engine(pop + offspring, MU, toolbox.select)
            else:
                pop[:] = toolbox.select(pop + offspring, MU)

            self.record(pop, gen, evals, record_hof)

        stat_parts.pickle_results(self.ft.name, self.alg_name, pop, self.logbook)

        return pop, self.logbook


class Nsga2DiscoverSIP(Nsga2Discover):
    def __init__(self, feature_model):
        if type(feature_model) is not FTModelNovelRep:
            feature_model = FTModelNovelRep(feature_model.name)
        super(Nsga2DiscoverSIP, self).__init__(feature_model)

    def run(self, record_hof=False, one_puls_n=True):
        super(Nsga2DiscoverSIP, self).run(record_hof, one_puls_n=True)


def experiment():
    from FeatureModel.SPLOT_dict import splot_dict
    name = splot_dict[int(sys.argv[1])]
    ed = Nsga2Discover(FTModelNovelRep(name,4))

    pop, logbook = ed.run(one_puls_n=True)

if __name__ == '__main__':
    import debug
    experiment()
