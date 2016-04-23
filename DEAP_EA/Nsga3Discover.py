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
from FeatureModel.ftmodel import FTModel
from DEAP_EA.DEAP_tools.EADiscover import EADiscover
from DEAP_EA.DEAP_tools import Nsga3Selc
import DEAP_tools.stat_parts as stat_parts
import random
import pdb


class Nsga3Discover(EADiscover):
    def __init__(self, feature_model):
        super(Nsga3Discover, self).__init__(feature_model)

        self.toolbox.register(
            "mate",
            tools.cxTwoPoint)

        self.toolbox.register(
            "mutate",
            self.bit_flip_mutate,
            mutate_rate=0.15)

        self.toolbox.register("select", Nsga3Selc.sel_nsga_iii)

    def run(self):
        toolbox = self.toolbox
        logbook = self.logbook
        stats = self.stats

        NGEN = 50
        MU = 1000
        CXPB = 0.9

        pop = toolbox.population(n=MU)

        _, evals = self.evaluate_pop(pop)  # Evaluate the pop with an invalid fitness

        ideal_point = Nsga3Selc.find_ideal_point(pop)
        extremes = Nsga3Selc.find_extreme_points(pop)
        intercepts = Nsga3Selc.construct_hyperplane(pop, extremes)
        Nsga3Selc.normalize_objectives(pop, intercepts, ideal_point)

        # rps = Nsga3Selc.generate_reference_points(self.ft.objNum)
        rps = Nsga3Selc.generate_reference_points(self.ft.objNum, newref=True)
        Nsga3Selc.associate(pop, rps)

        record = stats.compile(pop)
        logbook.record(gen=0, evals=evals, **record)
        print(logbook.stream)

        for gen in range(1, NGEN):
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

            _, evals = self.evaluate_pop(offspring)  # Evaluate the offspring with an invalid fitness

            # Select the next generation population
            pop = toolbox.select(pop + offspring, MU)
            record = stats.compile(pop)
            logbook.record(gen=gen, evals=evals, **record)
            print(logbook.stream)

        stat_parts.pickle_results(self.ft.name, 'NSGA3', pop, logbook)

        return pop, logbook


def demo():
    ed = Nsga3Discover(FTModel('webportal'))
    pop, logbook = ed.run()

    pdb.set_trace()

if __name__ == '__main__':
    demo()
