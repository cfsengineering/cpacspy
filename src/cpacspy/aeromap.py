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

import math

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from ambiance import Atmosphere

from cpacspy.cpacsfunctions import (
    add_float_vector,
    create_branch,
    get_float_vector,
    get_xpath_parent,
)
from cpacspy.utils import (
    AEROPERFORMANCE_XPATH,
    COEFS,
    PARAMS,
    PARAMS_COEFS,
    DAMPING_COEFS,
    listify,
)


def get_filter(df, alt_list, mach_list, aos_list, aoa_list):
    """Get a dataframe filter for a set of parameters lists."""

    filt = pd.Series(True, index=df.index)

    if alt_list:
        filt &= df["altitude"].isin(alt_list)

    if mach_list:
        filt &= df["machNumber"].isin(mach_list)

    if aos_list:
        filt &= df["angleOfSideslip"].isin(aos_list)

    if aoa_list:
        filt &= df["angleOfAttack"].isin(aoa_list)

    return filt


class AeroMap:
    """AeroMap class for CPACS AeroMap."""

    def __init__(self, tixi, uid, create_new=False):
        """Init aeromap class

        Args:
            tixi (object): TIXI object open from a CPACS file
            uid (str): UID of the AeroMap
            create_new (bool, optional): If True crate a new AeroMap in TIXI,
                                         if False find it in the CPACS file.
                                         Defaults to False.
        """

        self.tixi = tixi
        self.uid = uid
        self.name = uid
        self.description = ""
        self.atmospheric_model = "ISA"
        self.df = pd.DataFrame(columns=PARAMS_COEFS)

        if create_new:
            self.name = uid
            self.xpath = None

        else:
            self.xpath = self.tixi.uIDGetXPath(uid) + "/aeroPerformanceMap"
            name_xpath = get_xpath_parent(self.xpath) + "/name"
            if self.tixi.checkElement(name_xpath):
                self.name = self.tixi.getTextElement(name_xpath)

            description_xpath = get_xpath_parent(self.xpath) + "/description"
            if self.tixi.checkElement(description_xpath):
                self.description = self.tixi.getTextElement(description_xpath)

            atm_model_xpath = get_xpath_parent(self.xpath) + "/boundaryConditions/atmosphericModel"
            if self.tixi.checkElement(atm_model_xpath):
                self.atmospheric_model = self.tixi.getTextElement(atm_model_xpath)

            self.get_param_and_coef_from_cpacs()

    def get_param_and_coef_from_cpacs(self):
        """Get the parameters and coefficients from the aeroMap of a CPACS file."""

        param_dict = {}

        # Get parameters
        for param in PARAMS:
            param_xpath = self.xpath + f"/{param}"

            if self.tixi.checkElement(param_xpath):
                param_dict[param] = get_float_vector(self.tixi, param_xpath)
            else:
                raise ValueError(f'No value has been found for "{param}" in "{self.uid}" aeroMap!')

        # Get coefficients
        for coef in COEFS:
            coef_xpath = self.xpath + f"/{coef}"

            if self.tixi.checkElement(coef_xpath):
                param_dict[coef] = get_float_vector(self.tixi, coef_xpath)

        # Get damping derivatives coefficients
        for rates in ["negativeRates", "positiveRates"]:
            for damping_coef in DAMPING_COEFS:

                col_name = f"dampingDerivatives_{rates}_{damping_coef}"
                coef_xpath = self.xpath + f"/dampingDerivatives/{rates}/{damping_coef}"

                if self.tixi.checkElement(coef_xpath):
                    param_dict[col_name] = get_float_vector(self.tixi, coef_xpath)

        # Get incrementMaps coefficients
        # TODO

        df_param = pd.DataFrame(param_dict)
        self.df = pd.concat([self.df, df_param], axis=0)

    def get(self, list_of, alt=None, mach=None, aos=None, aoa=None):
        """Get parameter or coefficient as a numpy vector with other parameters as filter (optional).

        Args:
            list_of (str): Parameter or coefficient to get.
            alt (list, optional): List of altitudes to filter. Defaults to None.
            mach (list, optional): List of Mach numbers to filter. Defaults to None.
            aos (list, optional): List of angle of sideslip to filter. Defaults to None.
            aoa (list, optional): List of angle of attack to filter. Defaults to None.

        """

        alt_list = listify(alt)
        mach_list = listify(mach)
        aos_list = listify(aos)
        aoa_list = listify(aoa)

        filt = get_filter(self.df, alt_list, mach_list, aos_list, aoa_list)

        return self.df.loc[filt, list_of].to_numpy()

    def get_damping_derivatives(self, coef, axis, rates, alt=None, mach=None, aos=None, aoa=None):
        """Get damping derivatives coefficients as a numpy vector with other parameters as
        filter (optional).

        Args:
            coef (str): Coefficient to get ['cl','cd','cm','cml','cmd','cms']
            axis (str): Axis to get ['dp','dq','dr']
            rates (str): Rates to get ['pos','neg']
            alt (float, optional): Altitude
            mach (float, optional): Mach number
            aos (float, optional): Angle of sideslip
            aoa (float, optional): Angle of attack

        """

        if coef not in COEFS:
            raise ValueError(
                f'{coef} is not a valid coefficient! \n \
                Must be one of the following: {",".join(COEFS)}'
            )

        if axis not in ["dp", "dq", "dr"]:
            raise ValueError(
                f'{axis} is not a valid axis! \n \
                Must be one of the following: {"dp","dq","dr"}'
            )

        if rates in ["posivitive", "pos", "p"]:
            rates_name = "positiveRates"
        elif rates in ["negative", "neg", "n"]:
            rates_name = "negativeRates"
        else:
            raise ValueError(
                f'Invalid rates "{rates}"! \n \
                             Must be written as: \n \
                                 ("posivitive","pos","p" or "+") for positiveRates or \n \
                                     ("negative","neg","n" or "-") for negativeRates'
            )

        col_name = f"dampingDerivatives_{rates_name}_d{coef}{axis}Star"

        if col_name not in self.df.columns:
            raise ValueError(
                f"Damping derivative for {coef} coefficient on {axis} axis \
                with {rates_name} has not been found!"
            )

        return self.get(col_name, alt=alt, mach=mach, aos=aos, aoa=aoa)

    def add_row(
        self,
        alt,
        mach,
        aos,
        aoa,
        cd=np.nan,
        cl=np.nan,
        cs=np.nan,
        cmd=np.nan,
        cml=np.nan,
        cms=np.nan,
    ):
        """Add a row in an Aeromap dataframe.

        Args:
            alt (float): Altitude
            mach (float): Mach number
            aos (float): Angle of sideslip
            aoa (float): Angle of attack
            cd (float, optional): Coefficient of drag
            cl (float, optional): Coefficient of lift
            cs (float, optional): Coefficient of side force
            cmd (float, optional): Coefficient of moment due to drag
            cml (float, optional): Coefficient of moment due to lift
            cms (float, optional): Coefficient of moment due to side force

        """

        # Check if the parameter already exists
        filt = get_filter(self.df, [alt], [mach], [aos], [aoa])
        if not self.df.loc[filt].empty:
            raise ValueError(
                f"Row with alt={alt}, mach={mach}, aos={aos}, aoa={aoa} already exists!"
            )

        new_row = {
            "altitude": alt,
            "machNumber": mach,
            "angleOfSideslip": aos,
            "angleOfAttack": aoa,
            "cd": cd,
            "cl": cl,
            "cs": cs,
            "cmd": cmd,
            "cml": cml,
            "cms": cms,
        }

        # Check if all colomn already exist
        for col in new_row:
            if col not in self.df.columns:
                self.df[col] = np.nan

        # Add the new row
        self.df = self.df.append(new_row, ignore_index=True)

    def remove_row(self, alt, mach, aos, aoa):
        """Remove a row in an Aeromap dataframe for a set of parameters.

        Args:
            alt (float): Altitude
            mach (float): Mach number
            aos (float): Angle of sideslip
            aoa (float): Angle of attack

        """

        # Check if the parameter exists
        filt = get_filter(self.df, [alt], [mach], [aos], [aoa])

        if filt.empty or filt.any() == False:
            raise ValueError(
                f'No values has been found for \
                {alt}, {mach}, {aos}, {aoa} in "{self.uid}" aeroMap!'
            )

        # Remove the row
        self.df = self.df.drop(self.df.loc[filt].index)

    def add_coefficients(
        self,
        alt,
        mach,
        aos,
        aoa,
        cd=np.nan,
        cl=np.nan,
        cs=np.nan,
        cmd=np.nan,
        cml=np.nan,
        cms=np.nan,
    ):
        """Add coefficients to existing set of parmeter.

        Args:
            alt (float): Altitude
            mach (float): Mach number
            aos (float): Angle of sideslip
            aoa (float): Angle of attack
            cd (float, optional): Coefficient of drag
            cl (float, optional): Coefficient of lift
            cs (float, optional): Coefficient of side force
            cmd (float, optional): Coefficient of moment due to drag
            cml (float, optional): Coefficient of moment due to lift
            cms (float, optional): Coefficient of moment due to side force

        """

        # Check if parameter are already in the dataframe
        filt = get_filter(self.df, [alt], [mach], [aos], [aoa])

        if filt.empty or filt.any() == False:
            raise ValueError(
                f'No values has been found for \
                {alt}, {mach}, {aos}, {aoa} in "{self.uid}" aeroMap!'
            )

        self.df.loc[filt, ["cd", "cl", "cs", "cmd", "cml", "cms"]] = [cd, cl, cs, cmd, cml, cms]

    def add_damping_derivatives(self, alt, mach, aos, aoa, coef, axis, value, rate=-1.0):
        """Add a damping derivative coeficient for an existing set of alt,mach,aos,aoa.

        Args:
            alt (float): Altitude
            mach (float): Mach number
            aos (float): Angle of sideslip
            aoa (float): Angle of attack
            coef (str) : equivalent aero coefficient (cd,cl,cs,cmd,cml,cms)
            axis (str) : axis of rotation (dp,dq,dr)
            value (float) : value of the coeficient
            rate (float, optional): Rotation rate. Defaults to -1.0.

        """

        damping_coef = "d" + coef + axis + "Star"

        if damping_coef not in DAMPING_COEFS:
            raise ValueError(f'Damping coeficient "{damping_coef}" is not valid!')

        if rate < 0:
            col_name = "dampingDerivatives_negativeRates_" + damping_coef
        elif rate > 0:
            col_name = "dampingDerivatives_positiveRates_" + damping_coef
        else:
            raise ValueError(f'Rotation rate "{rate}" is not valid!')

        # Check if this set of parameters exists
        filter = get_filter(self.df, [alt], [mach], [aos], [aoa])
        if not filter.any():
            raise ValueError(
                f"Parameters for alt={alt}, mach={mach}, aos={aos}, aoa={aoa} \
                do not exist!"
            )

        self.df.loc[
            (self.df["altitude"] == alt)
            & (self.df["machNumber"] == mach)
            & (self.df["angleOfSideslip"] == aos)
            & (self.df["angleOfAttack"] == aoa),
            [col_name],
        ] = value

    def plot(self, x_param, y_param, alt=None, mach=None, aos=None, aoa=None):
        """Plot 'x_param' vs 'y_param' with filtered parameters passed as float or string."""

        alt_list = listify(alt)
        mach_list = listify(mach)
        aos_list = listify(aos)
        aoa_list = listify(aoa)

        filt = get_filter(self.df, alt_list, mach_list, aos_list, aoa_list)
        self.df.loc[filt].plot(x=x_param, y=y_param, marker="o")
        plt.show()

    def save(self):
        """Save the AeroMap in the TIXI object."""

        # Create and fill the '/aeroPerformanceMap' field
        if not self.xpath:
            if self.tixi.checkElement(AEROPERFORMANCE_XPATH):
                child_nb = self.tixi.getNumberOfChilds(AEROPERFORMANCE_XPATH)
                self.tixi.createElementAtIndex(AEROPERFORMANCE_XPATH, "aeroMap", child_nb + 1)
                self.xpath = AEROPERFORMANCE_XPATH + f"/aeroMap[{child_nb+1}]/aeroPerformanceMap"
            else:
                create_branch(self.tixi, AEROPERFORMANCE_XPATH + "/aeroMap")
                self.xpath = AEROPERFORMANCE_XPATH + "/aeroMap/aeroPerformanceMap"

            self.tixi.uIDSetToXPath(get_xpath_parent(self.xpath), self.uid)
            create_branch(self.tixi, self.xpath)

        # Create and fill parameters fields
        for param in PARAMS:
            if param in self.df:
                if not self.df[param].isnull().values.any():
                    param_xpath = self.xpath + "/" + param
                    create_branch(self.tixi, param_xpath)
                    add_float_vector(self.tixi, param_xpath, self.df[param].tolist())
                else:
                    raise ValueError(
                        "All the 4 parametres (alt,mach,aos,aoa) must not contains NaN value to \
                            be saved in an aeroMap!"
                    )
            else:
                raise ValueError(
                    "All the 4 parametres (alt,mach,aos,aoa) must be define to save an aeroMap!"
                )

        # Create and fill coefficients fields
        for coef in COEFS:
            if coef in self.df:
                if not self.df[coef].isnull().values.all():
                    coef_xpath = self.xpath + "/" + coef
                    create_branch(self.tixi, coef_xpath)
                    add_float_vector(self.tixi, coef_xpath, self.df[coef].tolist())
                else:
                    print(
                        f'Warning: {coef} coeffiecient from "{self.uid}" aeroMap will not be written in the \
                          CPACS file becuase it contains only NaN!'
                    )

        # Create and fill damping derivatives fields
        for rates in ["negativeRates", "positiveRates"]:
            for damping_coef in DAMPING_COEFS:
                col_name = "dampingDerivatives_" + rates + "_" + damping_coef
                if col_name in self.df:
                    if not self.df[col_name].isnull().values.all():
                        coef_xpath = self.xpath + f"/dampingDerivatives/{rates}/{damping_coef}"
                        create_branch(self.tixi, coef_xpath)
                        add_float_vector(self.tixi, coef_xpath, self.df[col_name].tolist())
                    else:
                        print(
                            f'Warning: {damping_coef} coeffiecient from "{self.uid}" aeroMap will \
                              not be written in the CPACS file becuase it contains onlz NaN!'
                        )

        # Create and fill incrementMap fields
        # TODO

        # Create and fill the '/name' field
        name_xpath = get_xpath_parent(self.xpath) + "/name"
        create_branch(self.tixi, name_xpath)
        self.tixi.updateTextElement(name_xpath, self.name)

        # Create and fill the '/description' field
        description_xpath = get_xpath_parent(self.xpath) + "/description"
        create_branch(self.tixi, description_xpath)
        self.tixi.updateTextElement(description_xpath, self.description)

        # Create and fill the '/atmosphericModel' field
        atm_model_xpath = get_xpath_parent(self.xpath) + "/boundaryConditions/atmosphericModel"
        if not self.tixi.checkElement(atm_model_xpath):
            create_branch(self.tixi, atm_model_xpath)
        self.tixi.updateTextElement(atm_model_xpath, self.atmospheric_model)

    def export_csv(self, csv_path):
        """Export the AeroMap as a CSV file."""

        self.df.to_csv(csv_path, na_rep="NaN", index=False, float_format="%g")

    def get_cd0_oswald(self, ar, alt=None, mach=None, aos=None, plot=False):
        """Calculate and return CD0 and Oswald factor."""

        # Check for unique angleOfAttack condition
        aoa = self.get("angleOfAttack", alt, mach, aos)
        aoa_unique = list(set(aoa))

        if len(aoa) > len(aoa_unique):
            raise ValueError(
                "You must have unique angle of attack value to calculate CD0 and Oswald factor!"
            )

        # Get coefficient
        cd = self.get("cd", alt, mach, aos)
        cl = self.get("cl", alt, mach, aos)
        cl2 = np.power(cl, 2)

        # Remove value when Cl < 0
        cond = cl >= 0
        cl2 = cl2[cond]
        cd = cd[cond]
        cl = cl[cond]

        # Linear regression
        coef = np.polyfit(cl2, cd, 1)
        f = np.poly1d(coef)
        x = np.arange(0, 2, 0.01)
        y = f(x)

        # Calculate CD0 and Oswald factor e
        k, cd0 = coef
        e = 1 / (k * ar * math.pi)

        print("---------------------------------------------")
        print(f"For alt={alt}m, Mach={mach}, AoS={aos}deg:")
        print("CD0:", round(cd0, 6))
        print("Oswald factor:", round(e, 4))
        print("---------------------------------------------")

        if plot:
            _, ax = plt.subplots()
            ax.plot(cl2, cd, "o")
            ax.plot(x, y, "-")
            plt.show()

        return cd0, e

    def calculate_forces(self, aircraft):
        """Calculate forces and momement from coefficients"""

        COEF2FORCE_DICT = {"cd": "drag", "cl": "lift", "cs": "side"}
        COEF2MOMENT_DICT = {"cmd": "md", "cml": "ml", "cms": "ms"}

        def coef2force(row, coef):
            """Calculate force from coefficient"""

            dens = Atmosphere(row["altitude"]).density[0]
            sos = Atmosphere(row["altitude"]).speed_of_sound[0]

            return 0.5 * dens * aircraft.ref_area * (row["machNumber"] * sos) ** 2 * row[coef]

        for coef in COEF2FORCE_DICT:
            if coef in self.df:
                self.df[COEF2FORCE_DICT[coef]] = self.df.apply(
                    lambda row: coef2force(row, coef), axis=1
                )
            else:
                print(
                    f"Warning: {COEF2FORCE_DICT[coef]} will not be calculated because there is no {coef} \
                    coefficient in the aeroMap!"
                )

        for coef in COEF2MOMENT_DICT:
            if coef in self.df:
                self.df[COEF2MOMENT_DICT[coef]] = self.df.apply(
                    lambda row: coef2force(row, coef) * aircraft.ref_length, axis=1
                )
            else:
                print(
                    f"Warning: {COEF2MOMENT_DICT[coef]} will not be calculated because there is no \
                    {coef} coefficient in the aeroMap!"
                )

    def __str__(self):

        text_line = []
        text_line.append("\nAeroMap Description -------------------------------------------------")
        text_line.append(f"\nAeroMap uid: {self.uid}")
        text_line.append(f"AeroMap xpath: {self.xpath}")
        text_line.append(f"AeroMap description: {self.description}")
        text_line.append(f"Atmospheric model: {self.atmospheric_model}\n")
        text_line.append(f'Number of states: \t\t{self.df["angleOfAttack"].size}')
        alt_list = self.df["altitude"].unique().tolist()
        mach_list = self.df["machNumber"].unique().tolist()
        aos_list = self.df["angleOfSideslip"].unique().tolist()
        aoa_list = self.df["angleOfAttack"].unique().tolist()
        text_line.append(f'Unique altitude: \t\t{str(alt_list).strip("[]")}')
        text_line.append(f'Unique Mach number: \t\t{str(mach_list).strip("[]")}')
        text_line.append(f'Unique angle of sideslip:  \t{str(aos_list).strip("[]")}')
        text_line.append(f'Unique angle of attack: \t{str(aoa_list).strip("[]")}\n')
        text_line.append("Parameters and coefficients:")
        text_line.append(str(self.df))
        text_line.append("---------------------------------------------------------------------\n")

        return ("\n").join(text_line)
