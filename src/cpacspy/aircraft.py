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

from cpacspy.cpacsfunctions import (get_value_or_default, get_tigl_aircraft)
from cpacspy.utils import REF_XPATH


class Aircraft:

    def __init__(self,tixi,tigl):
        """ Aircraft class to store references values and other information about the aircraft

        Args:
            tixi (object): TIXI object open from a CPACS file
        """
        
        self.tixi = tixi
        self.tigl = tigl

        # Reference values
        self.ref_lenght = get_value_or_default(self.tixi,REF_XPATH + '/length',1)
        self.ref_area = get_value_or_default(self.tixi,REF_XPATH + '/area',1)
        self.ref_point_x = get_value_or_default(self.tixi,REF_XPATH + '/point/x',0)
        self.ref_point_y = get_value_or_default(self.tixi,REF_XPATH + '/point/y',0)
        self.ref_point_z = get_value_or_default(self.tixi,REF_XPATH + '/point/z',0)

        # Aircraft specific values (extract with TiGL)
        self.aircraft_tigl = get_tigl_aircraft(self.tigl)
        self.ref_wing_idx = self.get_main_wing_idx() # By default the reference wing is the largest one
  
    # When self.ref_wing_idx is change:  
    # TODO: change it by uid also
    @property
    def ref_wing_idx(self):
        return self._ref_wing_idx

    @ref_wing_idx.setter
    def ref_wing_idx(self, new_idx):
        self._ref_wing_idx = new_idx

        self.wing_span = self.aircraft_tigl.get_wing(self._ref_wing_idx).get_wingspan()
        self.wing_area = self.aircraft_tigl.get_wing(self._ref_wing_idx).get_surface_area()

        ### TODO: use the function "get_aspect_ratio" instead, when it will be fixed in Tigl
        # self.wing_ar = self.aircraft_tigl.get_wing(self._ref_wing_idx).get_aspect_ratio()
        self.wing_ar = self.wing_span**2 / self.aircraft_tigl.get_wing(self._ref_wing_idx).get_reference_area(1)/2


    # TODO: add test for this function
    def get_main_wing_idx(self):
        """ Find the larest wing index

        Args:
            self (object)
        """
        
        # TODO: move that in a file with all the other useful xpath
        WINGS_XPATH = '/cpacs/vehicles/aircraft/model/wings'

        # Get Number of wings
        if self.tixi.checkElement(WINGS_XPATH):
            wing_count = self.tixi.getNamedChildrenCount(WINGS_XPATH, 'wing')
        else:
            wing_count = 0

        wing_area_max = 0
        wing_idx = None

        for i_wing in range(wing_count):
            wing_xpath = WINGS_XPATH + '/wing[' + str(i_wing+1) + ']'
            wing_uid = self.tixi.getTextAttribute(wing_xpath,'uID')

            # *2 to take the symetry into account
            wing_area = self.tigl.wingGetReferenceArea(i_wing+1,1) * 2

            # Get value from the largest wing (larger span)
            if wing_area > wing_area_max:
                wing_area_max = wing_area
                wing_span = self.tigl.wingGetSpan(wing_uid)

                wing_idx = i_wing+1

        return wing_idx

    def __str__(self): 

        text_line = []
        text_line.append('\nAircraft data --------------------------------------------------------------------------------------')
        text_line.append(' ')
        text_line.append(f'Reference lengh: \t{self.ref_lenght} [m]')
        text_line.append(f'Reference area: \t{self.ref_area} [m^2]')
        text_line.append(f'Reference point: \t({self.ref_point_x},{self.ref_point_y},{self.ref_point_z}) [m]')
        text_line.append(' ')
        text_line.append(f'Reference wing index: \t{self._ref_wing_idx}')
        text_line.append(f'Wing span: \t\t{self.wing_span} [m]')
        text_line.append(f'Wing area: \t\t{self.wing_area} [m^2]')
        text_line.append(f'Wing AR: \t\t{self.wing_ar} [-]')
        text_line.append(' ')
        text_line.append('----------------------------------------------------------------------------------------------------\n')
        return ('\n').join(text_line)
