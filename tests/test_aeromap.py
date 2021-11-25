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

import numpy as np

import pytest
from pytest import approx

# from tixi3.tixi3wrapper import Tixi3Exception
# from tigl3.tigl3wrapper import Tigl3Exception

from cpacspy.cpacspy import CPACS

CPACS_PATH = 'examples/D150_simple.xml'
CPACS_TEST_PATH = 'tests/D150_test_tmp.xml'
CSV_IN_FILE = os.path.join('tests', 'aeromap_test.csv')
CSV_OUT_FILE = os.path.join('tests', 'aeromap_test_export.csv')


def test_aeromap_class():

    # Load the CPACS file and 'aeromap_test1'
    cpacs = CPACS(CPACS_PATH)
    aeromap_1 = cpacs.get_aeromap_by_uid('aeromap_test1')

    assert aeromap_1.uid == 'aeromap_test1'
    assert aeromap_1.name == 'aeromap_test1'
    assert aeromap_1.description == 'Common default aeroMap'
    assert aeromap_1.atmospheric_model == 'ISA'
    assert set(aeromap_1.df.columns) == set(['altitude', 'machNumber', 'angleOfSideslip', 'angleOfAttack', 'cd', 'cl', 'cs', 'cmd', 'cml', 'cms'])
    assert aeromap_1.df.altitude.size == 1

    # Test if damping derivatives coefficients are correctly loaded
    aeromap_dampder = cpacs.get_aeromap_by_uid('aeromap_test_dampder')
    assert aeromap_dampder.df['dampingDerivatives_negativeRates_dcddpStar'].tolist()[0] == 0.00111
    # Only nan in it
    assert 'dampingDerivatives_negativeRates_dcsdrStar' in aeromap_dampder.df.columns
    # One nan in it
    assert 'dampingDerivatives_negativeRates_dcsdqStar' in aeromap_dampder.df.columns
    # No field in the aeromap
    assert 'dampingDerivatives_positiveRates_dcsdrStar' not in aeromap_dampder.df.columns


def test_get():

    # Load the CPACS file and 'aeromap_test2'
    cpacs = CPACS(CPACS_PATH)
    aeromap_2 = cpacs.get_aeromap_by_uid('aeromap_test2')

    assert aeromap_2.get('cl', alt=11000.0, mach=0.4) == np.array([1.111])
    assert aeromap_2.get('cd', aoa=2.0, aos=0.0) == np.array([0.13])


def test_get_damping_derivatives():

    # Load the CPACS file and 'aeromap_test_dampder'
    cpacs = CPACS(CPACS_PATH)
    aeromap_dampder = cpacs.get_aeromap_by_uid('aeromap_test_dampder')

    # Test if wrong damping derivatives coefficients raises ValueError
    with pytest.raises(ValueError):
        aeromap_dampder.get_damping_derivatives('cxx', 'dp', 'neg')

    # Test if wrong damping derivatives axis raises ValueError
    with pytest.raises(ValueError):
        aeromap_dampder.get_damping_derivatives('cl', 'dd', 'neg')

    # Test if wrong damping derivatives rate raises ValueError
    with pytest.raises(ValueError):
        aeromap_dampder.get_damping_derivatives('cl', 'dd', 'should_be_pos_or_neg')

    # Test all possible keyword for rates
    for rate in ['posivitive', 'pos', 'p', 'negative', 'neg', 'n']:
        assert aeromap_dampder.get_damping_derivatives('cl', 'dp', rate)[1] == 0.00112

    # Test to get one value
    assert aeromap_dampder.get_damping_derivatives('cl', 'dp', 'neg', alt=15000.0, mach=0.555, aos=0.0, aoa=7.0)[0] == 0.00118

    # Test if non existing parameter gives a vector of lenght 0
    assert len(aeromap_dampder.get_damping_derivatives('cl', 'dp', 'neg', alt=11111.0, mach=0.555, aos=0.0, aoa=7.0)) == 0


def test_add_row():
    """ Test the function 'add_row'. """

    # Load the CPACS file and 'aeromap_test1'
    cpacs = CPACS(CPACS_PATH)
    aeromap_1 = cpacs.get_aeromap_by_uid('aeromap_test1')

    # Test if missing parameters raises TypeError
    with pytest.raises(TypeError):
        aeromap_1.add_row(alt=11000.0)

    # Add a rows
    aeromap_1.add_row(alt=11000.0, mach=0.44, aos=0.0, aoa=0.0)
    aeromap_1.add_row(alt=11000.0, mach=0.44, aos=0.0, aoa=2.0, cl=1.111, cd=0.13)

    # Check if the new rows are correctly added
    assert np.isnan(aeromap_1.df['angleOfAttack'].tolist()[-2]) == 0.0
    assert np.isnan(aeromap_1.df['cl'].tolist()[-2])
    assert np.isnan(aeromap_1.df['cd'].tolist()[-2])
    assert aeromap_1.df['altitude'].tolist()[-1] == 11000.0
    assert aeromap_1.df['machNumber'].tolist()[-1] == 0.44
    assert aeromap_1.df['angleOfSideslip'].tolist()[-1] == 0.0
    assert aeromap_1.df['angleOfAttack'].tolist()[-1] == 2.0
    assert aeromap_1.df['cd'].tolist()[-1] == 0.13
    assert aeromap_1.df['cl'].tolist()[-1] == 1.111
    assert np.isnan(aeromap_1.df['cs'].tolist()[-1])

    # Test is adding row with existing parameters raises ValueError
    with pytest.raises(ValueError):
        aeromap_1.add_row(alt=11000.0, mach=0.44, aos=0.0, aoa=0.0)


def test_remove_row():
    """ Test the function 'remove_row'. """

    # Load the CPACS file and 'aeromap_test1'
    cpacs = CPACS(CPACS_PATH)
    aeromap_2 = cpacs.get_aeromap_by_uid('aeromap_test2')

    # Test if missing parameters raises ValeError
    with pytest.raises(ValueError):
        aeromap_2.remove_row(alt=1111.0, mach=0.2, aos=0.0, aoa=0.0)

    aeromap_2.remove_row(alt=0.0, mach=0.2, aos=0.0, aoa=0.0)
    aeromap_2.remove_row(alt=11000.0, mach=0.4, aos=2.0, aoa=2.0)
    aeromap_2.save()

    assert aeromap_2.df['angleOfAttack'].tolist()[0] == 2.0
    assert aeromap_2.df['angleOfAttack'].tolist()[-1] == 6.0
    assert len(aeromap_2.get('cd')) == 3


def test_add_coefficients():
    """ Test the function 'add_coefficients'. """

    # Load the CPACS file and 'aeromap_test1'
    cpacs = CPACS(CPACS_PATH)
    aeromap_1 = cpacs.get_aeromap_by_uid('aeromap_test1')

    # Test if not existing set of parameters raises ValueError
    with pytest.raises(ValueError):
        aeromap_1.add_coefficients(alt=11000.0, mach=0.33, aos=0.0, aoa=0.0, cl=1.33)

    # Test normal use of add_coefficients
    aeromap_1.add_coefficients(alt=0.0, mach=0.3, aos=0.0, aoa=0.0, cl=1.33)
    assert aeromap_1.df['cl'].tolist()[-1] == 1.33
    assert np.isnan(aeromap_1.df['cs'].tolist()[-1])

    # Test if adding again coefficients replace the previous ones
    aeromap_1.add_coefficients(alt=0.0, mach=0.3, aos=0.0, aoa=0.0, cd=0.33, cs=0.0033, cml=0.0033, cmd=0.0033, cms=0.0033)
    assert aeromap_1.df['cd'].tolist()[-1] == 0.33
    assert np.isnan(aeromap_1.df['cl'].tolist()[-1])


def test_add_damping_derivatives_and_save():
    """ Test 'add_damping_derivatives' function """

    cpacs = CPACS(CPACS_PATH)
    aeromap_dampder = cpacs.get_aeromap_by_uid('aeromap_test_dampder')

    # Test if raise Value Error for non-existing damping coefficient
    with pytest.raises(ValueError):
        aeromap_dampder.add_damping_derivatives(alt=15000, mach=0.555, aos=0, aoa=1.0, coef='cw', axis='dr', value=0.0555, rate=0)

    # Test if raise Value Error for non-existing axis
    with pytest.raises(ValueError):
        aeromap_dampder.add_damping_derivatives(alt=15000, mach=0.555, aos=0, aoa=1.0, coef='cs', axis='dz', value=0.0555, rate=0)

    # Test if raise Value Error for rate = 0
    with pytest.raises(ValueError):
        aeromap_dampder.add_damping_derivatives(alt=15000, mach=0.555, aos=0, aoa=1.0, coef='cs', axis='dr', value=0.0555, rate=0)

    # Test if raise Value Error for non-existing set of parameters
    with pytest.raises(ValueError):
        aeromap_dampder.add_damping_derivatives(alt=15000, mach=0.555, aos=0, aoa=22.0, coef='cs', axis='dr', value=0.0555, rate=1.0)

    # Test if coefficients are correctly added
    aeromap_dampder.add_damping_derivatives(alt=15000.0, mach=0.555, aos=0.0, aoa=0.0, coef='cs', axis='dr', value=0.0555, rate=1.0)
    assert 'dampingDerivatives_positiveRates_dcsdrStar' in aeromap_dampder.df.columns

    # Save the modified CPACS file
    aeromap_dampder.save()
    cpacs.save_cpacs(CPACS_TEST_PATH, overwrite=True)

    # Check value after it has been saved
    cpacs_test = CPACS(CPACS_TEST_PATH)
    aeromap_dampder_test = cpacs_test.get_aeromap_by_uid('aeromap_test_dampder')

    assert aeromap_dampder_test.get('dampingDerivatives_positiveRates_dcsdrStar', alt=15000, mach=0.555)[0] == 0.0555
    assert np.isnan(aeromap_dampder_test.get('dampingDerivatives_positiveRates_dcsdrStar', alt=15000, mach=0.555)[11])

    assert aeromap_dampder_test.get('dampingDerivatives_negativeRates_dcmldpStar', alt=15000, mach=0.555)[0] == 0.00111
    assert aeromap_dampder_test.get('dampingDerivatives_negativeRates_dcmldpStar', alt=15000, mach=0.555)[6] == 0.00117


def test_save():
    """ Test 'save' function. Some other function must be used test this one. """

    # Load the CPACS file and 'aeromap_test2'
    cpacs = CPACS(CPACS_PATH)
    aeromap_3 = cpacs.create_aeromap('aeromap_test3')
    aeromap_3.add_row(alt=10000, mach=0.3, aoa=2.0, aos=0.0, cl=0.5, cs=0.5, cmd=0.5, cml=0.5, cms=0.555)
    aeromap_3.add_row(alt=10000, mach=0.3, aoa=3.0, aos=0.0, cl=0.6, cs=0.6, cmd=0.6, cml=0.6, cms=0.666)
    aeromap_3.add_row(alt=10000, mach=0.3, aoa=4.0, aos=0.0)
    aeromap_3.add_coefficients(alt=10000, mach=0.3, aoa=4.0, aos=0.0, cl=0.7)

    # Check value before it is saved
    assert (aeromap_3.get('cl', alt=10000, mach=0.3) == np.array([0.5, 0.6, 0.7])).all()
    assert aeromap_3.get('cms', alt=10000, mach=0.3)[0] == 0.555
    assert aeromap_3.get('cms', alt=10000, mach=0.3)[1] == 0.666
    assert np.isnan(aeromap_3.get('cms', alt=10000, mach=0.3)[2])

    # Modify name and description
    aeromap_3.name = 'aeromap_new_name'
    aeromap_3.description = 'This is a new description'

    # Save the modified CPACS file
    aeromap_3.save()
    cpacs.save_cpacs(CPACS_TEST_PATH, overwrite=True)

    # Check value after it has been saved and reopened
    cpacs_test = CPACS(CPACS_TEST_PATH)
    aeromap_3_test = cpacs_test.get_aeromap_by_uid('aeromap_test3')

    assert (aeromap_3_test.get('cl', alt=10000, mach=0.3) == np.array([0.5, 0.6, 0.7])).all()
    assert aeromap_3_test.get('cms', alt=10000, mach=0.3)[0] == 0.555
    assert aeromap_3_test.get('cms', alt=10000, mach=0.3)[1] == 0.666
    assert np.isnan(aeromap_3_test.get('cms', alt=10000, mach=0.3)[2])

    # "/cd" should not be witten in the CPACS because no value was saved in it
    xpath = cpacs_test.tixi.uIDGetXPath('aeromap_test3') + '/aeroPerformanceMap/cd'
    assert not cpacs_test.tixi.checkElement(xpath)

    # Check if name and description has been saved correctly
    assert aeromap_3_test.name == 'aeromap_new_name'
    assert aeromap_3_test.description == 'This is a new description'


def test_csv():
    """ Test 'create_aeromap_from_csv' (from cpacspy.py) and
    'export_csv' function (with damping derivatives coefficients in the aeroMap) """

    cpacs = CPACS(CPACS_PATH)
    aeromap_dampder_csv = cpacs.create_aeromap_from_csv(CSV_IN_FILE)
    # TODO: maybe save and reopen the CPACS file inbetween the import and export?
    aeromap_dampder_csv.export_csv(CSV_OUT_FILE)

    # Check if file has been created
    with open(CSV_IN_FILE, 'r') as t1, open(CSV_OUT_FILE, 'r') as t2:
        csv_in = t1.readlines()
        csv_export = t2.readlines()

    assert csv_in == csv_export

    # Delete test file from a past run
    if os.path.exists(CSV_OUT_FILE):
        os.remove(CSV_OUT_FILE)


def test_get_cd0_oswald():
    '''TODO: create the test when the function is finalized!'''
    pass


def test_calcuate_forces():
    '''TODO: create the test when the function is finalized!'''
    pass
