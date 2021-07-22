#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# Copyright 2021 CFS Engineering
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------

# Author: Aidan Jungo

import sys

import numpy as np

import pytest
from pytest import approx

from tixi3.tixi3wrapper import Tixi3Exception
from tigl3.tigl3wrapper import Tigl3Exception

sys.path.append('../src/')
from cpacspy.cpacspy import CPACS

CPACS_PATH = 'examples/D150_simple.xml'


def test_aeromap_class():

    # Load the CPACS file and 'aeromap_test1'
    my_cpacs = CPACS(CPACS_PATH)
    aeromap_1 = my_cpacs.get_aeromap_by_uid('aeromap_test1')

    assert aeromap_1.uid == 'aeromap_test1'
    assert aeromap_1.name == 'aeromap_test1'
    assert aeromap_1.description == 'Common default aeroMap'
    print(aeromap_1.df.columns)
    assert set(aeromap_1.df.columns) == set(['altitude','machNumber','angleOfSideslip','angleOfAttack','cd','cl','cs','cmd','cml','cms'])
    assert aeromap_1.df.altitude.size == 1 

def test_get():

    # Load the CPACS file and 'aeromap_test2'
    my_cpacs = CPACS(CPACS_PATH)
    aeromap_2 = my_cpacs.get_aeromap_by_uid('aeromap_test2')

    assert aeromap_2.get('cl',alt=11000.0,mach=0.4) == np.array([1.111])
    assert aeromap_2.get('cd',aoa=2.0,aos=0.0) == np.array([0.13])


# TODO
#def test_add_values():

    # Load the CPACS file and 'aeromap_test2'
    #my_cpacs = CPACS(CPACS_PATH)
    #aeromap_2 = my_cpacs.get_aeromap_by_uid('aeromap_test2')
    #aeromap_2.add_values(alt=10000,mach=0.3,aoa=1.0,aoa=0.0)
