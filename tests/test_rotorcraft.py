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

from cpacspy.cpacspy import CPACS
from cpacspy.utils import PROPELLER_TESTS_PATH


def test_main_attrib():
    """Test main attributes of the Rotorcraft CPACS class"""

    # Load the CPACS file and all AeroMap in it
    cpacs = CPACS(PROPELLER_TESTS_PATH)

    # Check that reference value are saved
    assert cpacs.rotorcraft.ref_length == 1
    assert cpacs.rotorcraft.ref_area == 1
    assert cpacs.rotorcraft.ref_point_x == 0
    assert cpacs.rotorcraft.ref_point_y == 0
    assert cpacs.rotorcraft.ref_point_z == 0

    # Check value for wing index 1 (default)
    assert cpacs.rotorcraft.rotor_count == 2

    # Check __str__ method
    assert cpacs.aircraft.__str__()
