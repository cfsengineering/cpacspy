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

# XPATH
AEROPERFORMANCE_XPATH = '/cpacs/vehicles/aircraft/model/analyses/aeroPerformance'
REF_XPATH  = '/cpacs/vehicles/aircraft/model/reference'

# Lists
PARAMS = ['altitude','machNumber','angleOfSideslip','angleOfAttack']
COEFS = ['cd','cl','cs','cmd','cml','cms']
PARAMS_COEFS = PARAMS + COEFS


def listify(value):
    """If variable, return a list of 1 value, if already a list don't change a list. """

    if value is not None:
        if not isinstance(value,list):
            value = [value]
    else:
        value = []

    return value



        