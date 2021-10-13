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

import tigl3.configuration
import tixi3.tixi3wrapper as tixi3wrapper
import tigl3.tigl3wrapper as tigl3wrapper
from tixi3.tixi3wrapper import Tixi3Exception
from tigl3.tigl3wrapper import Tigl3Exception


def open_tixi(cpacs_path):
    """ Create the TIXI Handle of a CPACS file given as input
    by its path. If this operation is not possible, it returns 'None'

    Source :
        * TIXI functions: http://tixi.sourceforge.net/Doc/index.html

    Args:
        cpacs_path (str): Path to the CPACS file

    Returns::
        tixi_handle (handles): TIXI Handle of the CPACS file
    """

    tixi_handle = tixi3wrapper.Tixi3()
    tixi_handle.open(cpacs_path)

    print(f'TIXI handle has been created for {cpacs_path}.')

    return tixi_handle


def open_tigl(tixi_handle):
    """ Function 'open_tigl' return the TIGL Handle from its TIXI Handle.
    If this operation is not possible, it returns 'None'

    Source :
        * TIGL functions http://tigl.sourceforge.net/Doc/index.html

    Args:
        tixi_handle (handles): TIXI Handle of the CPACS file

    Returns:
        tigl_handle (handles): TIGL Handle of the CPACS file
    """

    # Get model uid, requierd to open TiGL handle in case there is also a rotorcraft in the CPACS file
    model_xpath = '/cpacs/vehicles/aircraft/model'
    if tixi_handle.checkAttribute(model_xpath, 'uID'):
        model_uid = tixi_handle.getTextAttribute(model_xpath, 'uID')
    else:
        model_uid = ''

    tigl_handle = tigl3wrapper.Tigl3()
    tigl_handle.open(tixi_handle, model_uid)

    tigl_handle.logSetVerbosity(1)  # 1 - only error, 2 - error and warnings

    return tigl_handle


def get_tigl_configuration(tigl):
    """ Get the TiGL aircraft configuration manager. """
    
    # Get the configuration manager
    mgr =  tigl3.configuration.CCPACSConfigurationManager_get_instance()
    aircraft = mgr.get_configuration(tigl._handle.value)
    
    return aircraft


def get_value(tixi, xpath):
    """ Check first if the the xpath exist and a value is store
    at this place. Then, it gets and returns this value. If the value or the
    xpath does not exist it raise an error and return 'None'.

    Source :
        * TIXI functions: http://tixi.sourceforge.net/Doc/index.html

    Args:
        tixi_handle (handles): TIXI Handle of the CPACS file
        xpath (str): xpath of the value to get

    Returns:
         value (float or str): Value found at xpath
    """

    # Try to get the a value at xpath
    try:
        value = tixi.getTextElement(xpath)
    except:
        value = None

    if value:
        try: # check if it is a 'float'
            is_float = isinstance(float(value), float)
            value = float(value)
        except:
            pass
    else:
        # check if the path exist
        if tixi.checkElement(xpath):
            raise ValueError('No value has been found at ' + xpath)
        else:
            raise ValueError(xpath + ' cannot be found in the CPACS file')

    # Special return for boolean
    if value == 'True':
        return True
    elif value == 'False':
        return False

    return value

def copy_branch(tixi, xpath_from, xpath_to):
    """ Function to copy a CPACS branch.

    Function 'copy_branch' copy the branch (with sub-branches) from
    'xpath_from' to 'xpath_to' by using recursion. The new branch should
    be identical (uiD, attribute, etc). 

    Source :
        * TIXI functions: http://tixi.sourceforge.net/Doc/index.html

    Args:
        tixi_handle (handles): TIXI Handle of the CPACS file
        xpath_from (str): xpath of the branch to copy
        xpath_to (str): Destination xpath

    Returns:
        tixi (handles): Modified TIXI Handle (with copied branch)
    """

    if not tixi.checkElement(xpath_from):
        raise ValueError(xpath_from + ' XPath does not exist!')
    if not tixi.checkElement(xpath_to):
        raise ValueError(xpath_to + ' XPath does not exist!')

    child_nb = tixi.getNumberOfChilds(xpath_from)

    if child_nb:
        xpath_to_split = xpath_to.split("/")
        xpath_to_parent = '/'.join(str(m) for m in xpath_to_split[:-1])

        child_list = []
        for i in range(child_nb):
            child_list.append(tixi.getChildNodeName(xpath_from, i+1))

        # If it is a text Element --> no child
        if "#" in child_list[0]:
            elem_to_copy = tixi.getTextElement(xpath_from)
            tixi.updateTextElement(xpath_to, elem_to_copy)

        else:
            # If child are named child (e.g. wings/wing)
            if all(x == child_list[0] for x in child_list):
                namedchild_nb = tixi.getNamedChildrenCount(xpath_from,
                                                           child_list[0])

                for i in range(namedchild_nb):
                    new_xpath_from = xpath_from + "/" + child_list[0] \
                                     + '[' + str(i+1) + ']'
                    new_xpath_to = xpath_to + "/" + child_list[0] \
                                   + '[' + str(i+1) + ']'
                    tixi.createElement(xpath_to, child_list[0])

                    # Call the function itself for recursion
                    copy_branch(tixi, new_xpath_from, new_xpath_to)

            else:
                for child in child_list:
                    new_xpath_from = xpath_from + "/" + child
                    new_xpath_to = xpath_to + "/" + child

                    # Create child
                    tixi.createElement(xpath_to, child)

                    # Call the function itself for recursion
                    copy_branch(tixi, new_xpath_from, new_xpath_to)

        # Copy attribute(s) if exists
        last_attrib = 0
        attrib_index = 1
        while not last_attrib:
            try:
                attrib_name = tixi.getAttributeName(xpath_from, attrib_index)
                attrib_text = tixi.getTextAttribute(xpath_from, attrib_name)
                tixi.addTextAttribute(xpath_to, attrib_name, attrib_text)
                attrib_index = attrib_index + 1
            except:
                last_attrib = 1

def get_uid(tixi, xpath):
    """ Function to get uID from a specific XPath.

    Function 'get_uid' checks the xpath and get the corresponding uID.

    Source :
        * TIXI functions: http://tixi.sourceforge.net/Doc/index.html

    Args:
        tixi (handles): TIXI Handle of the CPACS file
        xpath (str): xpath of the branch to add the uid

    Returns:
        uid (str): uid to add at xpath
    """


    if not tixi.checkElement(xpath):
        raise ValueError(xpath + ' XPath does not exist!')

    if tixi.checkAttribute(xpath, 'uID'):
        uid = tixi.getTextAttribute(xpath, 'uID')
        return uid
    else:
        raise ValueError("No uID found for: " + xpath)


def add_uid(tixi, xpath, uid):
    """ Function to add UID at a specific XPath.

    Function 'add_uid' checks and add UID to a specific path, the function will
    automatically update the chosen UID if it exists already.

    Source :
        * TIXI functions: http://tixi.sourceforge.net/Doc/index.html

    Args:
        tixi (handles): TIXI Handle of the CPACS file
        xpath (str): xpath of the branch to add the uid
        uid (str): uid to add at xpath
    """

    exist = True
    uid_new = uid
    i = 0
    while exist is True:
        if not tixi.uIDCheckExists(uid_new):
            tixi.uIDSetToXPath(xpath, uid_new)
            exist = False
        else:
            i = i + 1
            uid_new = uid + str(i)
            print('UID already existing changed to: ' + uid_new)

def get_value_or_default(tixi,xpath,default_value):
    """ Do the same than the function 'get_value'
    but if no value is found at this xpath it returns the default value and add
    it at the xpath. If the xpath does not exist, it is created.

    Source :
        * TIXI functions: http://tixi.sourceforge.net/Doc/index.html

    Args:
        tixi_handle (handles): TIXI Handle of the CPACS file
        xpath (str): xpath of the value to get
        default_value (str, float or int): Default value

    Returns:
        tixi (handles): Modified TIXI Handle (with added default value)
        value (str, float or int): Value found at xpath
    """

    value = None
    try:
        value = get_value(tixi, xpath)
    except:
        pass

    if value is None:
        value = default_value

        xpath_parent = '/'.join(str(m) for m in xpath.split("/")[:-1])
        value_name = xpath.split("/")[-1]
        create_branch(tixi,xpath_parent,False)

        try:
            is_int = isinstance(float(default_value), int)
        except:
            is_int = False

        try:
            is_float = isinstance(float(default_value), float)
        except:
            is_float = False

        try:
            is_bool = isinstance(default_value, bool)
        except:
            is_bool = False

            
        if is_bool:
           tixi.addTextElement(xpath_parent,value_name,str(value))
        elif is_float or is_int:
            value = float(default_value)
            tixi.addDoubleElement(xpath_parent,value_name,value,'%g')
        else:
            value = str(value)
            tixi.addTextElement(xpath_parent,value_name,value)
    else:
        # Special return for boolean
        if value == 'True':
            return True
        elif value == 'False':
            return False
        elif isinstance(value,bool):
            return value

    return value


def get_float_vector(tixi, xpath):
    """ Get a vector (composed by float) at the
    given XPath, if the node does not exist, an error will be raised.

    Args:
        tixi (handle): Tixi handle
        xpath (str): XPath of the vector to get
    """

    if not tixi.checkElement(xpath):
        raise ValueError(xpath + ' path does not exist!')

    float_vector_str = tixi.getTextElement(xpath)

    if float_vector_str == '':
        raise ValueError('No value has been fournd at ' + xpath)

    if float_vector_str.endswith(';'):
        float_vector_str = float_vector_str[:-1]
    float_vector_list = float_vector_str.split(';')
    float_vector = [float(elem) for elem in float_vector_list]

    return float_vector


def add_float_vector(tixi, xpath, vector):
    """ Add a vector (composed by float) at the given XPath, 
    if the node does not exist, it will be created. Values will be
    overwritten if paths exists.

    Args:
        tixi (handle): Tixi handle
        xpath (str): XPath of the vector to add
        vector (list, tuple): Vector of floats to add
    """

    # Strip trailing '/' (has no meaning here)
    if xpath.endswith('/'):
        xpath = xpath[:-1]

    # Get the field name and the parent CPACS path
    xpath_child_name = xpath.split("/")[-1]
    xpath_parent = xpath[:-(len(xpath_child_name)+1)]

    if not tixi.checkElement(xpath_parent):
        create_branch(tixi,xpath_parent)

    vector = [float(v) for v in vector]

    if tixi.checkElement(xpath):
        tixi.updateFloatVector(xpath, vector, len(vector), format='%g')
        tixi.addTextAttribute(xpath, 'mapType', 'vector')
    else:
        tixi.addFloatVector(xpath_parent, xpath_child_name, vector, \
                            len(vector), format='%g')
        tixi.addTextAttribute(xpath, 'mapType', 'vector')


def add_string_vector(tixi, xpath, vector):
    """ Add a vector (of string) at given CPACS xpath

    Function 'add_string_vector' will add a vector (composed by stings) at the
    given XPath, if the node does not exist, it will be created. Values will be
    overwritten if paths exists.

    Args:
        tixi (handle): Tixi handle
        xpath (str): XPath of the vector to add
        vector (list): Vector of string to add
    """

    # Strip trailing '/' (has no meaning here)
    if xpath.endswith('/'):
        xpath = xpath[:-1]

    # Get the field name and the parent CPACS path
    xpath_child_name = xpath.split("/")[-1]
    xpath_parent = xpath[:-(len(xpath_child_name)+1)]

    vector_str = ";".join([str(elem) for elem in vector])

    if not tixi.checkElement(xpath_parent):
        create_branch(tixi,xpath_parent)

    if tixi.checkElement(xpath):
        tixi.updateTextElement(xpath, vector_str)
    else:
        tixi.addTextElement(xpath_parent,xpath_child_name,vector_str)

def get_string_vector(tixi, xpath):
    """ Get a vector (of string) at given CPACS xpath

    Function 'get_string_vector' will get a vector (composed by string) at the
    given XPath, if the node does not exist, an error will be raised.

    Args:
        tixi (handle): Tixi handle
        xpath (str): XPath of the vector to get
    """

    if not tixi.checkElement(xpath):
        raise ValueError(xpath + ' path does not exist!')

    string_vector_str = tixi.getTextElement(xpath)

    if string_vector_str == '':
        raise ValueError('No value has been fournd at ' + xpath)

    if string_vector_str.endswith(';'):
        string_vector_str = string_vector_str[:-1]
    string_vector_list = string_vector_str.split(';')
    string_vector = [str(elem) for elem in string_vector_list]

    return string_vector

def get_xpath_parent(xpath,level=1):
    """ Get the parent xpath at any level, 1 is parent just above the input xpath.

    Args:
        xpath (str): Input xpath
        level (int, optional): Parent level. Defaults to 1.

    Returns:
        str: Parent xpath
    """

    if not xpath.startswith('/'):
        raise ValueError('"get_xpath_parent" must recieve an xpath as argument!')

    if len(xpath.split('/'))-1 <= level:
        raise ValueError('No parent available at this level')

    return '/'.join(xpath.split('/')[:-level])


def create_branch(tixi, xpath, add_child=False):
    """ Create a branch in the tixi handle and also all the missing parent nodes. 
    Be careful, the xpath must be unique until the last element, it means, 
    if several element exist, its index must be precised (index start at 1).
    e.g.: '/cpacs/vehicles/aircraft/model/wings/wing[2]/name'

    If the entire xpath already exist, the option 'add_child' (True/False) lets
    the user decide if a named child should be added next to the existing
    one(s). This only valid for the last element of the xpath.

    Source :
        * TIXI functions: http://tixi.sourceforge.net/Doc/index.html

    Args:
        tixi (handles): TIXI Handle of the CPACS file
        xpath (str): xpath of the branch to create
        add_child (boolean): Choice of adding a name child if the last element
                             of the xpath if one already exists

    Returns:
        tixi (handles): Modified TIXI Handle (with new branch)
    """

    xpath_split = xpath.split("/")
    xpath_count = len(xpath_split)

    for i in range(xpath_count-1):
        xpath_index = i + 2
        xpath_partial = '/'.join(str(m) for m in xpath_split[0:xpath_index])
        xpath_parent = '/'.join(str(m) for m in xpath_split[0:xpath_index-1])
        child = xpath_split[(xpath_index-1)]
        if tixi.checkElement(xpath_partial):
            if child == xpath_split[-1] and add_child:
                namedchild_nb = tixi.getNamedChildrenCount(xpath_parent, child)
                tixi.createElementAtIndex (xpath_parent,child,namedchild_nb+1)
        else:
            tixi.createElement(xpath_parent, child)
            