"""
!/usr/bin/env python3
-*- coding: utf-8 -*-

----------------------------------------------------------------------
Copyright 2021 CFS Engineering

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
----------------------------------------------------------------------

Author: Aidan Jungo

"""

import os

import pytest
from pytest import approx

from cpacspy.cpacspy import CPACS

CPACS_PATH = 'examples/D150_simple.xml'
CSV_PATH = 'examples/aeromap.csv'


def test_main_attrib():

    """ Test main attributes of the CPACS class """

    # Load the CPACS file and all AeroMap in it
    cpacs = CPACS(CPACS_PATH)

    assert cpacs.ac_name == 'D150'
    assert cpacs.nb_aeromaps == 4

    # Raise error for an invalid CPACS path
    # with pytest.raises(Tixi3Exception):
    # tixi_handle = open_tixi('invalid_CPACS_path')


def test_get_aeromap_uid_list():

    cpacs = CPACS(CPACS_PATH)

    # Get the list of aeromap uid on the CPACS file
    assert cpacs.get_aeromap_uid_list() == ['aeromap_test1', 'aeromap_test2', 'extended_aeromap', 'aeromap_test_dampder']


def test_get_aeromap_by_uid():

    cpacs = CPACS(CPACS_PATH)

    # Raise error aeromap did not exist
    with pytest.raises(ValueError):
        cpacs.get_aeromap_by_uid('not_an_aeromap')

    # Get aeromap from its uid
    assert cpacs.get_aeromap_by_uid('aeromap_test1').uid == 'aeromap_test1'


def test_create_aeromap():

    cpacs = CPACS(CPACS_PATH)

    # Raise error when uid contains sapce
    with pytest.raises(ValueError):
        cpacs.create_aeromap('not valid uid')

    # Raise error when uid already exist
    with pytest.raises(ValueError):
        cpacs.create_aeromap('aeromap_test1')

    # Create a new aeromap
    cpacs.create_aeromap('new_aeromap')
    assert cpacs.get_aeromap_by_uid('new_aeromap').uid == 'new_aeromap'
    assert cpacs.nb_aeromaps == 5


def test_create_aeromap_from_csv():

    cpacs = CPACS(CPACS_PATH)

    # Raise error when uid already exist
    with pytest.raises(ValueError):
        cpacs.create_aeromap_from_csv('/not/exiting/path.csv')

    # Create a new aeromap from a CSV file
    cpacs.create_aeromap_from_csv(CSV_PATH)
    assert cpacs.get_aeromap_by_uid('aeromap').uid == 'aeromap'
    assert cpacs.nb_aeromaps == 5


def test_duplicate_aeromap():

    cpacs = CPACS(CPACS_PATH)

    # Raise error when aeromap to duplicate did not exist
    with pytest.raises(ValueError):
        cpacs.duplicate_aeromap('not_existing_aeromap', 'duplicated_aeromap')

    # Raise error when uid already exist
    with pytest.raises(ValueError):
        cpacs.duplicate_aeromap('aeromap_test1', 'aeromap_test2')

    # Duplicate an aeroomap
    cpacs.duplicate_aeromap('aeromap_test1', 'duplicated_aeromap')
    assert cpacs.get_aeromap_by_uid('duplicated_aeromap').uid == 'duplicated_aeromap'
    assert cpacs.nb_aeromaps == 5


def test_delete_aeromap():

    cpacs = CPACS(CPACS_PATH)

    # Test if raise error when not valid name
    with pytest.raises(ValueError):
        cpacs.delete_aeromap('aeromap with spaces')

    # Test if raise error when aeromap to delete did not exist
    with pytest.raises(ValueError):
        cpacs.delete_aeromap('not_existing_aeromap')

    # Test if aeromap is deleted
    assert cpacs.get_aeromap_uid_list() == ['aeromap_test1', 'aeromap_test2', 'extended_aeromap', 'aeromap_test_dampder']
    cpacs.delete_aeromap('aeromap_test1')
    assert cpacs.get_aeromap_uid_list() == ['aeromap_test2', 'extended_aeromap', 'aeromap_test_dampder']
    assert cpacs.nb_aeromaps == 3

    # Test to delete all aeromaps
    for aeromap_uid in ['aeromap_test2', 'extended_aeromap', 'aeromap_test_dampder']:
        print(aeromap_uid)
        cpacs.delete_aeromap(aeromap_uid)

    assert cpacs.get_aeromap_uid_list() == []
    assert cpacs.nb_aeromaps == 0


def test_save_cpacs():

    test_path = 'tests/output.xml'
    test_path_1 = 'tests/output_1.xml'

    cpacs = CPACS(CPACS_PATH)

    # Raise error when tring to save a not xml file
    with pytest.raises(ValueError):
        cpacs.save_cpacs('tests/output.txt')

    # Delete test file from a past run (could be still there if an error occurs)
    if os.path.exists(test_path):
        os.remove(test_path)

    if os.path.exists(test_path_1):
        os.remove(test_path_1)

    # Save CPACS file
    cpacs.save_cpacs(test_path, True)
    assert os.path.exists(test_path)

    # Save CPACS file with already existing name (no overwrite)
    cpacs.save_cpacs(test_path, False)
    assert os.path.exists(test_path)

    # Delete test file
    if os.path.exists(test_path):
        os.remove(test_path)

    if os.path.exists(test_path_1):
        os.remove(test_path_1)
