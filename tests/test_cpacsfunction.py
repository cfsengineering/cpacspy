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

import pytest
from pytest import approx

from tixi3.tixi3wrapper import Tixi3Exception
from tigl3.tigl3wrapper import Tigl3Exception

sys.path.append('../src/')
from cpacspy.cpacsfunctions import (add_float_vector, create_branch,
                                    get_float_vector, get_tigl_aircraft,
                                    get_value, get_xpath_parent, open_tigl,
                                    open_tixi, get_value_or_default)

CPACS_IN_PATH = 'examples/D150_simple.xml'

def test_open_tixi():

    """Test the function 'open_tixi'"""

    # Create TIXI handles for a valid CPACS file
    tixi_handle = open_tixi(CPACS_IN_PATH)

    assert tixi_handle

    # Raise error for an invalid CPACS path
    with pytest.raises(Tixi3Exception):
        tixi_handle = open_tixi('invalid_CPACS_path')


def test_open_tigl():
    """Test the function 'open_tigl'"""

    # Create TIGL handle for a valid TIXI handles
    tixi_handle = open_tixi(CPACS_IN_PATH)
    tigl_handle = open_tigl(tixi_handle)

    assert tigl_handle

    # Raise error for an invalid TIXI handles
    with pytest.raises(AttributeError):
        tixi_handle = open_tigl('invalid_TIGL_handle')

def test_get_tigl_aircraft():

    tixi_handle = open_tixi(CPACS_IN_PATH)
    tigl_handle = open_tigl(tixi_handle)
    assert get_tigl_aircraft(tigl_handle)

def test_get_value():

    tixi = open_tixi(CPACS_IN_PATH)

    # Raise ValueError with not existing xpath
    xpath = '/cpacs/vehicles/aircraft/model/reference/notARealPath'
    with pytest.raises(ValueError):
        get_value(tixi, xpath)

    # Return Float 
    xpath = '/cpacs/vehicles/aircraft/model/reference/area'
    assert get_value(tixi, xpath) == 122.4

    # Return String 
    xpath = '/cpacs/header/name'
    assert get_value(tixi, xpath) == 'D150'

    # Return Boolean
    xpath = '/cpacs/toolspecific/pytest/aTrueBoolean'
    assert get_value(tixi, xpath) == True

    xpath = '/cpacs/toolspecific/pytest/aFalseBoolean'
    assert get_value(tixi, xpath) == False


def test_get_value_or_default():

    assert 1 == 1

def test_get_float_vector():

    assert 1 == 1

def test_add_float_vector():

    assert 1 == 1

def test_get_xpath_parent():

    xpath = '/cpacs/vehicles/aircraft/model/analyses/aeroPerformance/aeroMap[3]/aeroPerformanceMap'

    # Not an xpath
    with pytest.raises(ValueError):
        get_xpath_parent('NotAnXpath')

    with pytest.raises(ValueError):
        get_xpath_parent(xpath,8)

    assert get_xpath_parent(xpath,7) == '/cpacs'

    assert get_xpath_parent(xpath,5) == '/cpacs/vehicles/aircraft'

def test_create_branch():

    assert 1 == 1



   



    
