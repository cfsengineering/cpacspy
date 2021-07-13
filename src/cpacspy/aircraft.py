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

from cpacspy.cpacsfunctions import (get_value_or_default, open_tigl, get_tigl_aircraft)
from cpacspy.utils import REF_XPATH


class Aircraft:

    def __init__(self,tixi):
        """ Aircraft class to store references values and other information about the aircraft

        Args:
            tixi (object): TIXI object open from a CPACS file
        """
        
        self.tixi = tixi
        self.tigl = open_tigl(self.tixi)

        # Reference values
        self.ref_lenght = get_value_or_default(self.tixi,REF_XPATH + '/length',1)
        self.ref_area = get_value_or_default(self.tixi,REF_XPATH + '/area',1)
        self.ref_point_x = get_value_or_default(self.tixi,REF_XPATH + '/point/x',0)
        self.ref_point_y = get_value_or_default(self.tixi,REF_XPATH + '/point/y',0)
        self.ref_point_z = get_value_or_default(self.tixi,REF_XPATH + '/point/z',0)

        # Aircraft specific values (extract with TiGL)
        self.aircraft_tigl = get_tigl_aircraft(self.tigl)
        self.ref_wing_idx = 1 # By defauld the reference wing is "1", could be changed by updating this attribute
  
    # When self.ref_wing_idx is change:  
    # TODO: change it by uid also
    @property
    def ref_wing_idx(self):
        return self._ref_wing_idx

    @ref_wing_idx.setter
    def ref_wing_idx(self, new_idx):
        self._ref_wing_idx = new_idx

        self.wing_half_span = self.aircraft_tigl.get_wing(self._ref_wing_idx).get_wing_half_span()
        self.wing_area = self.aircraft_tigl.get_wing(self._ref_wing_idx).get_surface_area()
        self.wing_ar = self.aircraft_tigl.get_wing(self._ref_wing_idx).get_aspect_ratio()
        
    def __str__(self): 

        text_line = []
        text_line.append('\nAircraft data --------------------------------------------------------------------------------------')
        text_line.append(' ')
        text_line.append(f'Reference lengh: \t{self.ref_lenght} [m]')
        text_line.append(f'Reference area: \t{self.ref_area} [m^2]')
        text_line.append(f'Reference point: \t({self.ref_point_x},{self.ref_point_y},{self.ref_point_z}) [m]')
        text_line.append(' ')
        text_line.append(f'Reference wing index: \t{self._ref_wing_idx}')
        text_line.append(f'Wing half span: \t{self.wing_half_span} [m]')
        text_line.append(f'Wing area: \t\t{self.wing_area} [m^2]')
        text_line.append(f'Wing AR: \t\t{self.wing_ar} [-]')
        text_line.append(' ')
        text_line.append('----------------------------------------------------------------------------------------------------\n')
        return ('\n').join(text_line)
