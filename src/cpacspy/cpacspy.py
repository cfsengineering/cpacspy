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
import pandas as pd

from cpacspy.aeromap import AeroMap
from cpacspy.aircraft import Aircraft
from cpacspy.cpacsfunctions import open_tixi
from cpacspy.utils import AEROPERFORMANCE_XPATH


class CPACS:

    def __init__(self, cpacs_file):

        # CPACS
        self.cpacs_file = cpacs_file
        self.tixi = open_tixi(cpacs_file)

        # Aircraft name
        ac_name_xpath = '/cpacs/header/name'
        if self.tixi.checkElement(ac_name_xpath):
            self.ac_name = self.tixi.getTextElement(ac_name_xpath)

        # Aircraft data
        self.aircraft = Aircraft(self.tixi)

        # AeroMaps
        self.aeromap = []
        self.nb_aeromap = 0
        self.load_all_aeromaps()

    def load_all_aeromaps(self):
        """ Load all the aeromap present in the CPACS file as object. """

        for aeromap_uid in self.get_uid_list():
            aeromap = AeroMap(self.tixi,aeromap_uid)
            self.aeromap.append(aeromap)
            self.nb_aeromap += 1

    def get_uid_list(self):
        """ Get the list of all aeroMap UID. """

        uid_list = []

        if not self.tixi.checkElement(AEROPERFORMANCE_XPATH):
            return uid_list

        aeromap_count = self.tixi.getNamedChildrenCount(AEROPERFORMANCE_XPATH, 'aeroMap')
        if aeromap_count:
            for i in range(aeromap_count):
                aeromap_xpath = AEROPERFORMANCE_XPATH + '/aeroMap[' + str(i+1) + ']'
                aeromap_uid = self.tixi.getTextAttribute(aeromap_xpath, 'uID')
                uid_list.append(aeromap_uid)
        else:
            print('No "aeroMap" has been found in this CPACS file')

        return uid_list

    def get_aeromap_by_uid(self, uid):
        """ Get an aeromap object by its uid. """

        for am in self.aeromap:
            if am.uid == uid:
                return am

        raise ValueError(f'No aeromap with "{uid}" as uid as been found!')

    def create_aeromap(self,uid):
        """ Create a new aeromap object. """

        if ' ' in uid:
            raise ValueError('AeroMap uid should not contain any space!')

        if uid not in self.get_uid_list():
            new_aeromap = AeroMap(self.tixi,uid,create_new=True)
            self.aeromap.append(new_aeromap)
            self.nb_aeromap += 1
            return new_aeromap
        else:
            raise ValueError('This uid already exit!')

    def create_aeromap_from_csv(self,csv_path,uid=None):
        """ Create a new aeromap object from a CSV file. """

        if not uid:
            head, tail = os.path.split(csv_path)
            uid = tail.split('.')[0]

        if not os.path.exists(csv_path):
            raise ValueError(f'CSV file not found at {os.path.abspath(csv_path)}')

        new_aeromap = self.create_aeromap(uid)
        new_aeromap.df = pd.read_csv(csv_path,keep_default_na=False)

        return new_aeromap

    def duplicate_aeromap(self, uid_base, uid_duplicate):
        """ Duplicate an aeromap and retrun the new aeromap object. """

        # Check uid's
        if not uid_base in self.get_uid_list():
            raise ValueError('The AeroMap to duplicate does not exit!')

        if uid_duplicate in self.get_uid_list():
            raise ValueError('This uid for the duplicate already exit!')

        # Get AeroMap and duplicate
        am_base = self.get_aeromap_by_uid(uid_base)
        am_duplicated = AeroMap(self.tixi,uid_duplicate,create_new=True)

        # Copy data
        am_duplicated.df = am_base.df
        am_duplicated.description = am_base.description + f' (duplicate from "{uid_base}")'

        self.aeromap.append(am_duplicated)
        self.nb_aeromap += 1

        return am_duplicated

    def save_cpacs(self,cpacs_file,overwrite=False):
        """ Save a CPACS file from the TIXI object at a chosen path. """

        # Check for .xml file
        if not cpacs_file.endswith('.xml'):
            raise ValueError('The CPACS file name must be a .xml file!')

        # Check if file name must be change to avoid overwrite
        if os.path.exists(cpacs_file) and not overwrite:
            find_name = False
            i = 1
            while not find_name:
                cpacs_file_new_name = cpacs_file.split('.xml')[0] + f'_{str(i)}.xml' 
                if not os.path.exists(cpacs_file_new_name):
                    find_name = True
                    cpacs_file = cpacs_file_new_name
                else:
                    i += 1

        self.tixi.save(cpacs_file)

    def __str__(self): 

        text_line = []
        text_line.append('\n----------------------------------------------------------------------------------------------------')
        text_line.append(f'Aircraft name : {self.ac_name}')
        text_line.append(f'CPACS file path: {self.cpacs_file}')
        text_line.append(' ')
        text_line.append('Aeromaps list:')
        for aeromap_uid in self.get_uid_list():
            text_line.append(aeromap_uid)
        text_line.append('----------------------------------------------------------------------------------------------------\n')

        return ('\n').join(text_line)


if __name__ == '__main__':
    pass
