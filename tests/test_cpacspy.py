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

import os
import sys

import pytest
from pytest import approx

from tixi3.tixi3wrapper import Tixi3Exception
from tigl3.tigl3wrapper import Tigl3Exception

sys.path.append('../src/')
from cpacspy.cpacspy import CPACS


CPACS_PATH = 'examples/D150_simple.xml'
CSV_PATH = 'examples/aeromap.csv'


def test_main_attrib():

    """ Test main attributes of the CPACS class """

    # Load the CPACS file and all AeroMap in it
    my_cpacs = CPACS(CPACS_PATH)

    assert my_cpacs.ac_name == 'D150'

    #assert my_cpacs.aeromap == []
    assert my_cpacs.nb_aeromap == 3

    # Raise error for an invalid CPACS path
    #with pytest.raises(Tixi3Exception):
     #   tixi_handle = open_tixi('invalid_CPACS_path')


def test_get_uid_list():

    my_cpacs = CPACS(CPACS_PATH)

    # Get the list of aeromap uid on the CPACS file
    assert my_cpacs.get_uid_list() == ['aeromap_test1','aeromap_test2','extended_aeromap']


def test_get_aeromap_by_uid():

    my_cpacs = CPACS(CPACS_PATH)

    # Raise error aeromap did not exist
    with pytest.raises(ValueError):
        my_cpacs.get_aeromap_by_uid('not_an_aeromap')

    # Get aeromap from its uid
    assert my_cpacs.get_aeromap_by_uid('aeromap_test1').uid == 'aeromap_test1'


def test_create_aeromap():

    my_cpacs = CPACS(CPACS_PATH)

    # Raise error when uid contains sapce
    with pytest.raises(ValueError):
        my_cpacs.create_aeromap('not valid uid')

    # Raise error when uid already exist
    with pytest.raises(ValueError):
        my_cpacs.create_aeromap('aeromap_test1')

    # Create a new aeromap
    my_cpacs.create_aeromap('new_aeromap')
    assert my_cpacs.get_aeromap_by_uid('new_aeromap').uid == 'new_aeromap'
    assert my_cpacs.nb_aeromap == 4


def test_create_aeromap_from_csv():

    my_cpacs = CPACS(CPACS_PATH)

    # Raise error when uid already exist
    with pytest.raises(ValueError):
        my_cpacs.create_aeromap_from_csv('/not/exiting/path.csv')

    # Create a new aeromap from a CSV file
    my_cpacs.create_aeromap_from_csv(CSV_PATH)
    assert my_cpacs.get_aeromap_by_uid('aeromap').uid == 'aeromap'
    assert my_cpacs.nb_aeromap == 4


def test_duplicate_aeromap():

    my_cpacs = CPACS(CPACS_PATH)

    # Raise error when aeromap to duplicate did not exist
    with pytest.raises(ValueError):
        my_cpacs.duplicate_aeromap('not_existing_aeromap','duplicated_aeromap')

    # Raise error when uid already exist
    with pytest.raises(ValueError):
        my_cpacs.duplicate_aeromap('aeromap_test1','aeromap_test2')

    # Duplicate an aeroomap
    my_cpacs.duplicate_aeromap('aeromap_test1','duplicated_aeromap')
    assert my_cpacs.get_aeromap_by_uid('duplicated_aeromap').uid == 'duplicated_aeromap'
    assert my_cpacs.nb_aeromap == 4


def test_save_cpacs():

    test_path = 'tests/output.xml'
    test_path_1 = 'tests/output_1.xml'

    my_cpacs = CPACS(CPACS_PATH)

    # Raise error when tring to save a not xml file
    with pytest.raises(ValueError):
        my_cpacs.save_cpacs('tests/output.txt')

    # Delete test file from a past run (could be still there if an error occurs)
    if os.path.exists(test_path):
        os.remove(test_path)

    if os.path.exists(test_path_1):
        os.remove(test_path_1.xml)

    # Save CPACS file 
    my_cpacs.save_cpacs(test_path,True)
    assert os.path.exists(test_path)

    # Save CPACS file with already existing name (no overwrite)
    my_cpacs.save_cpacs(test_path,False)
    assert os.path.exists(test_path)
    
    # Delete test file
    if os.path.exists(test_path):
        os.remove(test_path)

    if os.path.exists(test_path_1):
        os.remove(test_path_1)
