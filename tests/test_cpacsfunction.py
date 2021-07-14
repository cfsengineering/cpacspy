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


sys.path.append('../src/')
from cpacspy.cpacsfunctions import (get_xpath_parent)



def test_open_tixi():

    assert 1==1


def test_open_tigl():

    assert 1==1

def test_get_tigl_aircraft():

    assert 1 == 1

def test_get_value():

    assert 1 == 1

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



   



    
