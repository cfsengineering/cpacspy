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

from pytest import approx

from cpacspy.cpacspy import CPACS
from cpacspy.utils import D150_TESTS_PATH


def test_main_attrib():
    """Test main attributes of the CPACS class"""

    # Load the CPACS file and all AeroMap in it
    cpacs = CPACS(D150_TESTS_PATH)

    # Check that reference value are saved
    assert cpacs.aircraft.ref_length == 4.193
    assert cpacs.aircraft.ref_area == 122.4
    assert cpacs.aircraft.ref_point_x == 0
    assert cpacs.aircraft.ref_point_y == 0
    assert cpacs.aircraft.ref_point_z == 0

    # Check value for wing index 1 (default)
    assert cpacs.aircraft.ref_wing_uid == "Wing1"
    assert cpacs.aircraft.wing_span == approx(33.91, rel=1e-2)
    assert cpacs.aircraft.wing_area == approx(130.5, rel=1e-2)
    assert cpacs.aircraft.wing_ar == approx(9.402, rel=1e-2)

    # Check value for wing index 3
    cpacs.aircraft.ref_wing_idx = 2
    assert cpacs.aircraft.ref_wing_uid == "Wing2H"
    assert cpacs.aircraft.wing_span == approx(12.45, rel=1e-2)
    assert cpacs.aircraft.wing_area == approx(32.76, rel=1e-2)
    assert cpacs.aircraft.wing_ar == approx(5.00, rel=1e-2)

    # Check value for wing index 3
    cpacs.aircraft.ref_wing_idx = 3
    assert cpacs.aircraft.ref_wing_uid == "Wing3V"
    assert cpacs.aircraft.wing_span == approx(5.87, rel=1e-2)
    assert cpacs.aircraft.wing_area == approx(46.59, rel=1e-2)
    assert cpacs.aircraft.wing_ar == approx(3.21, rel=1e-2)

    # Check get main wing index
    assert cpacs.aircraft.get_main_wing_idx() == 1

    # Change ref wing with uid
    cpacs.aircraft.ref_wing_uid = "Wing2H"
    assert cpacs.aircraft.ref_wing_idx == 2

    cpacs.aircraft.ref_wing_uid = "Wing3V"
    assert cpacs.aircraft.ref_wing_idx == 3

    # Check __str__ method
    assert cpacs.aircraft.__str__()
