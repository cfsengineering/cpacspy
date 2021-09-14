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
CPACS_TEST_PATH = 'tests/D150_test.xml'


def test_aeromap_class():

    # Load the CPACS file and 'aeromap_test1'
    my_cpacs = CPACS(CPACS_PATH)
    aeromap_1 = my_cpacs.get_aeromap_by_uid('aeromap_test1')

    assert aeromap_1.uid == 'aeromap_test1'
    assert aeromap_1.name == 'aeromap_test1'
    assert aeromap_1.description == 'Common default aeroMap'
    assert aeromap_1.atmospheric_model == 'ISA'
    assert set(aeromap_1.df.columns) == set(['altitude','machNumber','angleOfSideslip','angleOfAttack','cd','cl','cs','cmd','cml','cms'])
    assert aeromap_1.df.altitude.size == 1 

def test_get():

    # Load the CPACS file and 'aeromap_test2'
    my_cpacs = CPACS(CPACS_PATH)
    aeromap_2 = my_cpacs.get_aeromap_by_uid('aeromap_test2')

    assert aeromap_2.get('cl',alt=11000.0,mach=0.4) == np.array([1.111])
    assert aeromap_2.get('cd',aoa=2.0,aos=0.0) == np.array([0.13])


def test_add_values_and_save():
    ''' Both function "add_value" and "save" are tested toghether because they are generally used in the same time '''

    # Load the CPACS file and 'aeromap_test2'
    my_cpacs = CPACS(CPACS_PATH)
    aeromap_3 = my_cpacs.create_aeromap('aeromap_test3')
    aeromap_3.add_values(alt=10000,mach=0.3,aoa=2.0,aos=0.0,cl=0.5,cs=0.5,cmd=0.5,cml=0.5,cms=0.555)
    aeromap_3.add_values(alt=10000,mach=0.3,aoa=3.0,aos=0.0,cl=0.6,cs=0.6,cmd=0.6,cml=0.6,cms=0.666)
    aeromap_3.add_values(alt=10000,mach=0.3,aoa=4.0,aos=0.0,cl=0.7)
    
    # Check value before it is saved
    assert (aeromap_3.get('cl',alt=10000,mach=0.3) == np.array([0.5,0.6,0.7])).all()
    assert (aeromap_3.get('cms',alt=10000,mach=0.3) == np.array([0.555,0.666])).all()

    # Modify name and description
    aeromap_3.name = 'aeromap_new_name'
    aeromap_3.description = 'This is a new description'

    # Save the modified CPACS file
    aeromap_3.save()
    my_cpacs.save_cpacs(CPACS_TEST_PATH,overwrite=True)

    # Check value after it has been saved
    my_cpacs_test = CPACS(CPACS_TEST_PATH)
    aeromap_3_test = my_cpacs_test.get_aeromap_by_uid('aeromap_test3')
        
    assert (aeromap_3_test.get('cl',alt=10000,mach=0.3) == np.array([0.5,0.6,0.7])).all()
    
    # "/cms" should not be witten in the CPACS file because it contains a NaN
    xpath = my_cpacs_test.tixi.uIDGetXPath('aeromap_test3') + '/aeroPerformanceMap/cms'
    assert not my_cpacs_test.tixi.checkElement(xpath) 

    # Check if name and description has been saved correctly
    assert aeromap_3_test.name == 'aeromap_new_name'
    assert aeromap_3_test.description == 'This is a new description'


def test_get_cd0_oswald():
    '''TODO: create the test when the function is finalized!'''
    pass

def test_get_forces():
    '''TODO: create the test when the function is finalized!'''
    pass