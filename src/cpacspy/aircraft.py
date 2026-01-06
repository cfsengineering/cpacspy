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
from cpacspy.utils import AIRCRAFT_XPATH


class Aircraft:
    """Aircraft class"""

    def __init__(self, tixi, tigl):
        """Aircraft class to store references values and other information about the aircraft

        Args:
            tixi (object): TIXI object open from the CPACS file
            tigl (object): TIGL object open from the CPACS file
        """

        self.tixi = tixi
        self.tigl = tigl

        # Reference values
        reference_xpath = AIRCRAFT_XPATH + "/reference"
        self.ref_length = get_value_or_default(self.tixi, reference_xpath + "/length", 1)
        self.ref_area = get_value_or_default(self.tixi, reference_xpath + "/area", 1)
        self.ref_point_x = get_value_or_default(self.tixi, reference_xpath + "/point/x", 0)
        self.ref_point_y = get_value_or_default(self.tixi, reference_xpath + "/point/y", 0)
        self.ref_point_z = get_value_or_default(self.tixi, reference_xpath + "/point/z", 0)

        # Aircraft specific values (extract with TiGL)
        self.configuration = get_tigl_configuration(self.tigl)
        self.ref_wing_idx = self.get_main_wing_idx()  # By default reference wing is the largest

    @property
    def ref_wing_idx(self):
        return self._ref_wing_idx

    @ref_wing_idx.setter
    def ref_wing_idx(self, new_idx) -> None:
        if new_idx is None:
            self._clear_wing_reference()
            return

        try:
            wing_count = self.configuration.get_wing_count()
        except Exception:
            self._clear_wing_reference()
            return

        if wing_count == 0:
            self._clear_wing_reference()
            return

        if new_idx < 1 or new_idx > wing_count:
            raise ValueError(f"Reference wing index {new_idx} out of range (1-{wing_count})")

        try:
            wing = self.configuration.get_wing(new_idx)
        except Exception:
            self._clear_wing_reference()
            return

        self._ref_wing_idx = new_idx
        self._ref_wing_uid = wing.get_uid()

        sym = 1
        if wing.get_symmetry():
            sym = 2

        self.wing_span = wing.get_wing_half_span() * sym
        self.wing_area = wing.get_surface_area()
        self.wing_ar = wing.get_aspect_ratio()

    @property
    def ref_wing_uid(self):
        return self._ref_wing_uid

    @ref_wing_uid.setter
    def ref_wing_uid(self, uid):
        if uid is None:
            self._clear_wing_reference()
            return

        try:
            wing_count = self.configuration.get_wing_count()
        except Exception:
            self._clear_wing_reference()
            return

        if wing_count == 0:
            self._clear_wing_reference()
            return

        try:
            self._ref_wing_idx = self.configuration.get_wing_index(uid)
        except ValueError as err:
            raise ValueError(f'No wing with uid "{uid}" found') from err
        except Exception:
            self._clear_wing_reference()
            return

        sym = 1
        try:
            wing = self.configuration.get_wing(self._ref_wing_idx)
        except Exception:
            self._clear_wing_reference()
            return

        if wing.get_symmetry():
            sym = 2

        self._ref_wing_uid = uid
        self.wing_span = wing.get_wing_half_span() * sym
        self.wing_area = wing.get_surface_area()
        self.wing_ar = wing.get_aspect_ratio()

    def get_main_wing_idx(self) -> int | None:
        """Find the largest wing index"""

        wing_area_max = 0
        wing_idx = None

        try:
            wing_count = self.configuration.get_wing_count()
        except Exception:
            return wing_idx

        if wing_count == 0:
            return wing_idx

        for i_wing in range(wing_count):
            try:
                wing_area = self.configuration.get_wing(i_wing + 1).get_surface_area()
            except Exception:
                continue

            if wing_area > wing_area_max:
                wing_area_max = wing_area
                wing_idx = i_wing + 1

        return wing_idx

    def __str__(self) -> str:
        text_line = []
        text_line.append("\nAircraft data -------------------------------------------------------")
        text_line.append(" ")
        text_line.append(f"Reference length: \t{self.ref_length} [m]")
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

    def _clear_wing_reference(self) -> None:
        """Clear cached wing reference data when no wing is available."""

        self._ref_wing_idx = None
        self._ref_wing_uid = None
        self.wing_span = None
        self.wing_area = None
        self.wing_ar = None
