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
import sys
import pickle
import sys
sys.path.insert(0, "/share/jchen37/SPL")
from ProductLine.DIMACS_EA.IbeaDiscover import IbeaDiscover
from ProductLine.DimacsModel import DimacsModel
from universe import PROJECT_PATH
sys.dont_write_btyecode = True

"""
exp3
date: 05-31-16
eshop model 50M evaluations
"""


def exp3(repeat_id=1):
    name = "eshop"
    model = DimacsModel(name, reducedDec=True)
    ed = IbeaDiscover(model)
    ed.set_ea_gen(500000)
    pop, logbook = ed.run

    with open('{0}/Records/exp3/eshop_IBEA_50M.{2}.logbook'.format(PROJECT_PATH, name, repeat_id), 'w') as f:
        pickle.dump(logbook, f)

    with open('{0}/Records/exp3/eshop_IBEA_50M.{2}.pop'.format(PROJECT_PATH, name, repeat_id), 'w') as f:
        pickle.dump(pop, f)

exp3(repeat_id=int(sys.argv[1]))