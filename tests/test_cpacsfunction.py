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
from pathlib import Path

import numpy as np
import pytest
from cpacspy.cpacsfunctions import (
    add_float_vector,
    add_string_vector,
    add_uid,
    add_value,
    copy_branch,
    create_branch,
    get_float_vector,
    get_string_vector,
    get_tigl_configuration,
    get_uid,
    get_value,
    get_value_or_default,
    get_xpath_parent,
    open_tigl,
    open_tixi,
)
from cpacspy.utils import D150_TESTS_PATH

# from tigl3.tigl3wrapper import Tigl3Exception
from tixi3.tixi3wrapper import Tixi3Exception


def test_open_tixi():

    """Test the function 'open_tixi'"""

    # Create TIXI handles for a valid CPACS file (from str)
    tixi_handle = open_tixi(D150_TESTS_PATH)
    assert tixi_handle

    # Create TIXI handles for a valid CPACS file (from Path)
    tixi_handle = open_tixi(Path(D150_TESTS_PATH))
    assert tixi_handle

    # Raise error for an invalid CPACS path
    with pytest.raises(Tixi3Exception):
        tixi_handle = open_tixi("invalid_CPACS_path")


def test_open_tigl():
    """Test the function 'open_tigl'"""

    # Create TIGL handle for a valid TIXI handles
    tixi_handle = open_tixi(D150_TESTS_PATH)
    tigl_handle = open_tigl(tixi_handle)

    assert tigl_handle

    # Raise error for an invalid TIXI handles
    with pytest.raises(AttributeError):
        tixi_handle = open_tigl("invalid_TIGL_handle")


def test_get_tigl_configuration():

    tixi_handle = open_tixi(D150_TESTS_PATH)
    tigl_handle = open_tigl(tixi_handle)
    assert get_tigl_configuration(tigl_handle)


def test_add_value():

    tixi = open_tixi(D150_TESTS_PATH)

    xpath = "/cpacs/toolspecific/pytest/addedValueStr"

    add_value(tixi, xpath, "test1")
    assert tixi.getTextElement(xpath) == "test1"

    add_value(tixi, xpath, "test2")
    assert tixi.getTextElement(xpath) == "test2"

    xpath = "/cpacs/toolspecific/pytest/addedValueInt"

    add_value(tixi, xpath, 44)
    assert tixi.getTextElement(xpath) == "44"

    xpath = "/cpacs/toolspecific/pytest/addedValueFloat"

    add_value(tixi, xpath, 5.55)
    assert tixi.getTextElement(xpath) == "5.55"


def test_get_value():

    tixi = open_tixi(D150_TESTS_PATH)

    # Raise ValueError with not existing xpath
    xpath = "/cpacs/toolspecific/pytest/notARealPath"
    with pytest.raises(ValueError):
        get_value(tixi, xpath)

    # Test if return None if no value has been found at xpath
    xpath = "/cpacs/toolspecific/pytest"
    with pytest.raises(ValueError):
        get_value(tixi, xpath)

    # Test different types of float/Nan/Inf
    xpath = "/cpacs/vehicles/aircraft/model/reference/area"
    assert get_value(tixi, xpath) == 122.4
    assert isinstance(get_value(tixi, xpath), float)

    xpath = "/cpacs/toolspecific/pytest/aSciFloat"
    assert get_value(tixi, xpath) == 123000.0
    assert isinstance(get_value(tixi, xpath), float)

    xpath = "/cpacs/toolspecific/pytest/aNaN"
    assert np.isnan(get_value(tixi, xpath))
    assert isinstance(get_value(tixi, xpath), float)

    xpath = "/cpacs/toolspecific/pytest/anan"
    assert np.isnan(get_value(tixi, xpath))
    assert isinstance(get_value(tixi, xpath), float)

    xpath = "/cpacs/toolspecific/pytest/aInf"
    assert get_value(tixi, xpath) == float("-inf")
    assert isinstance(get_value(tixi, xpath), float)

    # Return Boolean
    xpath = "/cpacs/toolspecific/pytest/aTrueBoolean"
    assert get_value(tixi, xpath)
    assert isinstance(get_value(tixi, xpath), bool)
    xpath = "/cpacs/toolspecific/pytest/aFalseBoolean"
    assert not get_value(tixi, xpath)
    assert isinstance(get_value(tixi, xpath), bool)

    # Return String
    xpath = "/cpacs/header/name"
    assert get_value(tixi, xpath) == "D150"
    assert isinstance(get_value(tixi, xpath), str)


def test_get_value_or_default():

    tixi = open_tixi(D150_TESTS_PATH)

    # Same test as 'get_value' function (just main ones)
    xpath = "/cpacs/vehicles/aircraft/model/reference/area"
    value = get_value_or_default(tixi, xpath, 133.5)
    assert value == 122.4
    assert isinstance(value, float)
    xpath = "/cpacs/toolspecific/pytest/aTrueBoolean"
    value = get_value_or_default(tixi, xpath, False)
    assert value
    assert isinstance(value, bool)
    xpath = "/cpacs/header/name"
    value = get_value_or_default(tixi, xpath, "D150")
    assert value == "D150"
    assert isinstance(value, str)

    # Check if the default string value is return and the saved in the CPACS file
    xpath = "/cpacs/toolspecific/pytest/notExistingPathString"
    assert get_value_or_default(tixi, xpath, "test") == "test"
    assert get_value(tixi, xpath) == "test"

    # Return default float value for a non existing path
    xpath = "/cpacs/toolspecific/pytest/notExistingPathFloat"
    assert get_value_or_default(tixi, xpath, 10.01) == 10.01
    assert get_value(tixi, xpath) == 10.01

    # Return default boolean for a non existing path
    xpath = "/cpacs/toolspecific/pytest/notExistingPathBoolTrue"
    assert get_value_or_default(tixi, xpath, True)
    assert get_value(tixi, xpath)
    assert isinstance(get_value(tixi, xpath), bool)

    xpath = "/cpacs/toolspecific/pytest/notExistingPathBoolFalse"
    assert not get_value_or_default(tixi, xpath, False)
    assert not get_value(tixi, xpath)
    assert isinstance(get_value(tixi, xpath), bool)


def test_get_float_vector():

    tixi = open_tixi(D150_TESTS_PATH)

    # Raise ValueError with not existing xpath
    xpath = "/cpacs/toolspecific/pytest/notARealPath"
    with pytest.raises(ValueError):
        get_float_vector(tixi, xpath)

    # Raise ValueError when not value has been found at xpath
    xpath = "/cpacs/toolspecific/pytest"
    with pytest.raises(ValueError):
        get_float_vector(tixi, xpath)

    # Return a correct float vector
    xpath = "/cpacs/toolspecific/pytest/aCorrectFloatVector"
    get_float_vector(tixi, xpath) == [1, 0.95, 0.9, 0.8, 0.7, 0.6]


def test_add_float_vector():

    tixi = open_tixi(D150_TESTS_PATH)
    xpath = "/cpacs/toolspecific/pytest/addedFloatVector"
    vector = [0.1, 0.2, 0.3]
    add_float_vector(tixi, xpath, vector)

    # Check if the float vector has been added
    assert tixi.getTextElement(xpath) == "0.1;0.2;0.3"


def test_get_xpath_parent():

    xpath = "/cpacs/vehicles/aircraft/model/analyses/aeroPerformance/aeroMap[3]/aeroPerformanceMap"

    # Not an xpath
    with pytest.raises(ValueError):
        get_xpath_parent("NotAnXpath")

    # Not existing parent
    with pytest.raises(ValueError):
        get_xpath_parent(xpath, 8)

    # Get the first parent xpath
    parent_xpath = "/cpacs/vehicles/aircraft/model/analyses/aeroPerformance/aeroMap[3]"
    assert get_xpath_parent(xpath) == parent_xpath

    # Get the furthest parent xpath
    assert get_xpath_parent(xpath, 7) == "/cpacs"

    # Get another parent xpath
    assert get_xpath_parent(xpath, 5) == "/cpacs/vehicles/aircraft"


def test_create_branch():

    tixi = open_tixi(D150_TESTS_PATH)
    xpath = "/cpacs/toolspecific/pytest/newBranch"
    create_branch(tixi, xpath)

    # Check if the new branch exist
    assert tixi.checkElement(xpath)

    # Test adding named child branch
    xpath = "/cpacs/toolspecific/pytest/newBranch/namedChild"
    create_branch(tixi, xpath)
    create_branch(tixi, xpath, True)
    create_branch(tixi, xpath, True)

    # Check if the new branch exist
    assert tixi.checkElement(xpath + "[3]")


def test_copy_branch():
    """Test the function 'copy_branch'"""

    tixi = open_tixi(D150_TESTS_PATH)

    # Create a new 'header' branch and copy the original 'header' into it
    xpath_new = "/cpacs/header"
    xpath_from = "/cpacs/header[1]"
    xpath_to = "/cpacs/header[2]"
    create_branch(tixi, xpath_new, True)
    copy_branch(tixi, xpath_from, xpath_to)

    # Check if a specific element has been copied
    xpath_elem_from = "/cpacs/header[1]/updates/update[1]/timestamp"
    xpath_elem_to = "/cpacs/header[2]/updates/update[1]/timestamp"
    elem_from = tixi.getTextElement(xpath_elem_from)
    elem_to = tixi.getTextElement(xpath_elem_to)

    assert elem_from == elem_to

    # Check if a specific attribute has been copied
    attrib_text_from = tixi.getTextAttribute(xpath_elem_from, "uID")
    attrib_text_to = tixi.getTextAttribute(xpath_elem_to, "uID")

    assert attrib_text_from == attrib_text_to


def test_add_string_vector():
    """Test the function 'add_sting_vector'"""

    tixi = open_tixi(D150_TESTS_PATH)
    xpath = "/cpacs/toolspecific/CEASIOMpy/testVector/"

    # Add a new vector
    string_vector = ["aaa", "bbb", "ccc"]
    add_string_vector(tixi, xpath, string_vector)
    added_sting_vector_str = tixi.getTextElement(xpath)
    added_sting_vector = added_sting_vector_str.split(";")
    added_sting_vector = [str(elem) for elem in added_sting_vector]

    assert added_sting_vector == string_vector

    # Update a vector
    string_vector = ["abc", "123", "test-01"]
    add_string_vector(tixi, xpath, string_vector)
    added_sting_vector_str = tixi.getTextElement(xpath)
    added_sting_vector = added_sting_vector_str.split(";")
    added_sting_vector = [str(elem) for elem in added_sting_vector]

    assert added_sting_vector == string_vector


def test_get_string_vector():
    """Test the function 'get_string_vector'"""

    tixi = open_tixi(D150_TESTS_PATH)
    xpath = "/cpacs/toolspecific/CEASIOMpy/testVector"

    # Add a new vector
    string_vector = ["aaa", "zzz"]
    add_string_vector(tixi, xpath, string_vector)

    # Get a string vector
    string_vector_get = get_string_vector(tixi, xpath)

    assert string_vector_get == string_vector

    # Raise an error when the XPath is wrong
    wrong_xpath = "/cpacs/toolspecific/CEASIOMpy/testVectorWrong"
    with pytest.raises(ValueError):
        get_string_vector(tixi, wrong_xpath)

    # Raise an error when no value at XPath
    no_value_xpath = "/cpacs/toolspecific/CEASIOMpy"
    with pytest.raises(ValueError):
        get_string_vector(tixi, no_value_xpath)


def test_get_uid():
    """Test the function 'get_uid'"""

    tixi = open_tixi(D150_TESTS_PATH)

    # Check if a false xpath raises ValueError
    xpath = "/cpacs/vehicles/aircraft/MYmodel"
    with pytest.raises(ValueError):
        get_uid(tixi, xpath)

    # Check if a no uid at xpath raises ValueError
    xpath = "/cpacs/vehicles/aircraft"
    with pytest.raises(ValueError):
        get_uid(tixi, xpath)

    # Check if it get correctly the uid
    xpath = "/cpacs/vehicles/aircraft/model"
    uid = get_uid(tixi, xpath)
    assert uid == "D150_VAMP"


def test_add_uid():
    """Test the function 'add_uid'"""

    tixi = open_tixi(D150_TESTS_PATH)

    # Update UID
    xpath = "/cpacs/vehicles/aircraft/model"
    new_uid = "New_aircrat_name"
    add_uid(tixi, xpath, new_uid)
    updated_uid = tixi.getTextAttribute(xpath, "uID")

    assert updated_uid == new_uid

    # Add UID
    xpath = "/cpacs/vehicles/aircraft/model/name"
    new_uid = "nameUID"
    add_uid(tixi, xpath, new_uid)
    added_uid = tixi.getTextAttribute(xpath, "uID")

    assert added_uid == new_uid

    # Add existing UID (should add "1" at the end of the UID)
    xpath = "/cpacs/vehicles/aircraft/model/name"
    new_uid = "Fuselage1"
    add_uid(tixi, xpath, new_uid)
    added_uid = tixi.getTextAttribute(xpath, "uID")

    assert added_uid == "Fuselage11"
