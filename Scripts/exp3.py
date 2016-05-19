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


"""
Experiment 1 on May 10
Model: all
Objectives dimension: 5
Algorithms: idea0
Repeat: 30
"""

from FeatureModel.FeatureModel import FeatureModel
from FeatureModel.SPLOT_dict import first_argv_name, splot_dict
from DEAP_EA import IbeaDiscover, Nsga2Discover, Spea2Discover, RandomTreeDiscover
from universe import PROJECT_PATH
import pickle

LOGBOOK = dict()
discovers = [RandomTreeDiscover.RandomTreeDiscover]


def exp3(name, repeat_id=1):
    LOGBOOK.clear()
    for dis in discovers:
        dis_ins = dis(FeatureModel(name))
        _, logbook = dis_ins.run()
        LOGBOOK[str(dis_ins.alg_name)] = logbook

        # saving
        with open('{0}/Records/exp3/{1}.{2}.logbooks'.format(PROJECT_PATH, name, repeat_id), 'w') as f:
            pickle.dump(LOGBOOK, f)

for i in range(9):
    name = splot_dict[i]
    exp3(name=name, repeat_id=int(sys.argv[1]))