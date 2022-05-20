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

from cpacspy.cpacsfunctions import get_tigl_configuration, get_value_or_default

from cpacspy.utils import ROTORCRAFT_XPATH


class Rotorcraft:
    """Rotorcraft class"""

    def __init__(self, tixi, tigl):
        """Rotorcraft class to store references values and other information about the rotorcraf

        Args:
            tixi (object): TIXI object open from the CPACS file
            tigl (object): TIGL object open from the CPACS file
        """

        self.tixi = tixi
        self.tigl = tigl

        # Reference values
        reference_xpath = ROTORCRAFT_XPATH + "/reference"
        self.ref_length = get_value_or_default(self.tixi, reference_xpath + "/length", 1)
        self.ref_area = get_value_or_default(self.tixi, reference_xpath + "/area", 1)
        self.ref_point_x = get_value_or_default(self.tixi, reference_xpath + "/point/x", 0)
        self.ref_point_y = get_value_or_default(self.tixi, reference_xpath + "/point/y", 0)
        self.ref_point_z = get_value_or_default(self.tixi, reference_xpath + "/point/z", 0)

        # Rotorcraft specific values (extract with TiGL)
        self.configuration = get_tigl_configuration(self.tigl)
        self.rotor_count = self.configuration.get_rotor_count()

    def __str__(self):

        text_line = []
        text_line.append(
            "\nRotorcraft data -------------------------------------------------------"
        )
        text_line.append(" ")
        text_line.append(f"Reference length: \t{self.ref_length} [m]")
        text_line.append(f"Reference area: \t{self.ref_area} [m^2]")
        text_line.append(
            f"Reference point: \t({self.ref_point_x},{self.ref_point_y},{self.ref_point_z}) [m]"
        )
        text_line.append(" ")
        # text_line.append(f"Reference wing index: \t{self._ref_rotor_idx}")
        text_line.append(f"Rotor count: \t\t{self.rotor_count}")
        text_line.append(" ")
        text_line.append("---------------------------------------------------------------------\n")
        return ("\n").join(text_line)
