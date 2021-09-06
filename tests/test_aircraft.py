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

sys.path.append('../src/')
from cpacspy.cpacspy import CPACS

CPACS_PATH = 'examples/D150_simple.xml'


def test_main_attrib():

    """ Test main attributes of the CPACS class """

    # Load the CPACS file and all AeroMap in it
    my_cpacs = CPACS(CPACS_PATH)

    # Check that reference value are saved
    assert my_cpacs.aircraft.ref_lenght == 4.193
    assert my_cpacs.aircraft.ref_area == 122.4
    assert my_cpacs.aircraft.ref_point_x == 0
    assert my_cpacs.aircraft.ref_point_y == 0
    assert my_cpacs.aircraft.ref_point_z == 0

    # Check value for wing index 1 (default)
    assert my_cpacs.aircraft.wing_span == approx(16.95,2)
    assert my_cpacs.aircraft.wing_area == approx(130.5,2)
    
    ### TODO: uncomment when Tigl function "get_aspect_ratio" is fixed
    #assert my_cpacs.aircraft.wing_ar == approx(9.4,2)   

    # Check value for wing index 3
    my_cpacs.aircraft.ref_wing_idx = 3
    assert my_cpacs.aircraft.wing_span == approx(5.87,2)
    assert my_cpacs.aircraft.wing_area == approx(46.59,2)
    assert my_cpacs.aircraft.wing_ar == approx(3.2,2)   
