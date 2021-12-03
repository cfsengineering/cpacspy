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

from cpacspy.cpacsfunctions import get_value_or_default, get_tigl_configuration
from cpacspy.utils import REF_XPATH


class Aircraft:
    """ Aircraft class """

    def __init__(self, tixi, tigl):
        """ Aircraft class to store references values and other information about the aircraft

        Args:
            tixi (object): TIXI object open from the CPACS file
            tigl (object): TIGL object open from the CPACS file
        """

        self.tixi = tixi
        self.tigl = tigl

        # Reference values
        self.ref_lenght = get_value_or_default(self.tixi, REF_XPATH + "/length", 1)
        self.ref_area = get_value_or_default(self.tixi, REF_XPATH + "/area", 1)
        self.ref_point_x = get_value_or_default(self.tixi, REF_XPATH + "/point/x", 0)
        self.ref_point_y = get_value_or_default(self.tixi, REF_XPATH + "/point/y", 0)
        self.ref_point_z = get_value_or_default(self.tixi, REF_XPATH + "/point/z", 0)

        # Aircraft specific values (extract with TiGL)
        self.configuration = get_tigl_configuration(self.tigl)
        self.ref_wing_idx = self.get_main_wing_idx()  # By default reference wing is the largest

    @property
    def ref_wing_idx(self):
        return self._ref_wing_idx

    @ref_wing_idx.setter
    def ref_wing_idx(self, new_idx):
        self._ref_wing_idx = new_idx

        self._ref_wing_uid = self.configuration.get_wing(self._ref_wing_idx).get_uid()

        sym = 1
        if self.configuration.get_wing(self._ref_wing_idx).get_symmetry():
            sym = 2

        self.wing_span = self.configuration.get_wing(self._ref_wing_idx).get_wing_half_span() * sym
        self.wing_area = self.configuration.get_wing(self._ref_wing_idx).get_surface_area()
        self.wing_ar = self.configuration.get_wing(self._ref_wing_idx).get_aspect_ratio()

    @property
    def ref_wing_uid(self):
        return self._ref_wing_uid

    @ref_wing_uid.setter
    def ref_wing_uid(self, uid):
        self._ref_wing_uid = uid

        self._ref_wing_idx = self.configuration.get_wing_index(uid)

        sym = 1
        if self.configuration.get_wing(self._ref_wing_idx).get_symmetry():
            sym = 2

        self.wing_span = self.configuration.get_wing(self._ref_wing_uid).get_wing_half_span() * sym
        self.wing_area = self.configuration.get_wing(self._ref_wing_uid).get_surface_area()
        self.wing_ar = self.configuration.get_wing(self._ref_wing_uid).get_aspect_ratio()

    def get_main_wing_idx(self):
        """ Find the larest wing index

        Args:
            self (object)
        """

        wing_area_max = 0
        wing_idx = None

        for i_wing in range(self.configuration.get_wing_count()):
            wing_area = self.configuration.get_wing(i_wing + 1).get_surface_area()

            if wing_area > wing_area_max:
                wing_area_max = wing_area
                wing_idx = i_wing + 1

        return wing_idx

    def __str__(self):

        text_line = []
        text_line.append("\nAircraft data -------------------------------------------------------")
        text_line.append(" ")
        text_line.append(f"Reference lengh: \t{self.ref_lenght} [m]")
        text_line.append(f"Reference area: \t{self.ref_area} [m^2]")
        text_line.append(
            f"Reference point: \t({self.ref_point_x},{self.ref_point_y},{self.ref_point_z}) [m]"
        )
        text_line.append(" ")
        text_line.append(f"Reference wing index: \t{self._ref_wing_idx}")
        text_line.append(f"Wing span: \t\t{self.wing_span} [m]")
        text_line.append(f"Wing area: \t\t{self.wing_area} [m^2]")
        text_line.append(f"Wing AR: \t\t{self.wing_ar} [-]")
        text_line.append(" ")
        text_line.append("---------------------------------------------------------------------\n")
        return ("\n").join(text_line)
