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

import os
import shutil
import xmltodict

import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from cpacspy.cpacspy import CPACS
from cpacspy.utils import PARAMS_COEFS

MODULE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


# Page setups
st.set_page_config(page_title="cpacspy interactive plot")
logo = Image.open(MODULE_DIR + "/logo/logo_transparant_bg.png")
st.sidebar.image(logo)
st.title("Aeromap plot")

# CPACS file uplooad
file = st.sidebar.file_uploader("Select a CPACS file")


aeromap_list = []

if file:

    # Remove and recreate the tmp file
    tmp_dir = os.path.join(MODULE_DIR, "my_tmp_cpacs")
    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.mkdir(tmp_dir)

    # Path of the CPACS file in tmp dir
    if str(file.name).endswith(".xml"):
        st.session_state.cpacs_file = os.path.join(tmp_dir, file.name)
        with open(st.session_state.cpacs_file, "w") as f:
            f.write(xmltodict.unparse(xmltodict.parse(file.read())))

        # Load a CPACS file with cpacspy
        cpacs = CPACS(st.session_state.cpacs_file)

        # Get aeromap(s) selection from multiselection box
        aeromap_uid_list = cpacs.get_aeromap_uid_list()
        aeromap_selected = st.sidebar.multiselect("Select aeromap", aeromap_uid_list)
        aeromap_list = [cpacs.get_aeromap_by_uid(aeromap_uid) for aeromap_uid in aeromap_selected]
    else:
        st.sidebar.error("You must select a CPACS file (*.xml)")
else:
    st.warning("First, you must select a CPACS file!")

# If aeromap(s) are selected, plot them
if aeromap_list:

    # temp (TODO: could be improve, how to look into all df)
    df_tmp = aeromap_list[0].df

    # Option choose axis
    col1, col2, col3 = st.columns(3)

    with col1:
        x_axis = st.selectbox("x", PARAMS_COEFS)
    with col2:
        y_axis = st.selectbox("y", PARAMS_COEFS)
    with col3:
        st.write(" ")

    # Option filter 1
    with st.expander("Filter 1"):
        f1_col1, f1_col2 = st.columns(2)

        with f1_col1:
            remaning = [item for item in PARAMS_COEFS if item not in [x_axis, y_axis]]
            filter1 = st.selectbox("Filter by:", remaning)
        with f1_col2:
            value_list = df_tmp[filter1].unique()
            value_selected = st.multiselect("Filter value:", value_list, value_list[0])

    # Option filter 2
    with st.expander("Filter 2"):
        f2_col1, f2_col2 = st.columns(2)
        with f2_col1:
            remaning2 = [item for item in PARAMS_COEFS if item not in [x_axis, y_axis, filter1]]
            filter2 = st.selectbox("Filter2 by:", remaning2)
        with f2_col2:
            value_list2 = df_tmp[filter2].unique()
            value_selected2 = st.multiselect("Filter2 value:", value_list2, value_list2[0])

    # Plot figure
    fig = go.Figure()
    for aeromap in aeromap_list:

        if not len(value_selected):
            value_selected = value_list

        for value in value_selected:
            if not len(value_selected2):
                value_selected2 = value_list2

            for value2 in value_selected2:
                df = aeromap.df[(aeromap.df[filter1] == value) & (aeromap.df[filter2] == value2)]
                legend = f"{aeromap.uid}<br>{filter1}={value}<br>{filter2}={value2}"
                fig.add_trace(go.Scatter(x=df[x_axis], y=df[y_axis], name=legend))

    fig.update_traces(
        mode="markers+lines",
        hovertemplate="x: %{x:.2f} \ny: %{y:.2f} ",
    )

    grid_color = "rgb(188,188,188)"
    axis_color = "rgb(0,0,0)"
    bg_color = "rgb(255,255,255)"

    fig.update_layout(
        xaxis=dict(title=x_axis),
        yaxis=dict(title=y_axis),
        plot_bgcolor=bg_color,
    )
    fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor=axis_color,
        gridcolor=grid_color,
        zerolinecolor=grid_color,
    )
    fig.update_yaxes(
        showline=True,
        linewidth=2,
        linecolor=axis_color,
        gridcolor=grid_color,
        zerolinecolor=grid_color,
    )

    st.plotly_chart(fig)

else:
    st.warning("You must select at leat one aeromap on the sidebar!")

    # # Workaround to create a folder picker dialog
    # import tkinter as tk
    # from tkinter import filedialog
    # root = tk.Tk()
    # root.withdraw()
    # root.wm_attributes('-topmost', 1)

    # st.write('## Save figure')
    # fig_name = st.text_input("Figure name:","myfigure.png")
    # if not fig_name.endswith(".png"):
    #     fig_name = fig_name + ".png"

    # st.write('Please select a folder to save the figure:')
    # clicked = st.button('Select & Save')
    # if clicked:
    #     dirname = st.text_input('Selected folder:', filedialog.askdirectory(master=root))
    #     fig_path = os.path.join(dirname, fig_name)
    #     fig.savefig(fig_path)
    #     st.success("This figure has been saved!")
