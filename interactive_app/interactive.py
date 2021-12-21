import os
import streamlit as st
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from PIL import Image
from cpacspy.cpacspy import CPACS
from cpacspy.utils import PARAMS_COEFS



# Load a CPACS file
cpacs = CPACS("../examples/D150_simple.xml")


    
# Set up the sidebar
logo = Image.open('../logo/logo_transparant_bg.png')
st.sidebar.image(logo)
    
aeromap_list = cpacs.get_aeromap_uid_list()
aeromap_selected = st.sidebar.selectbox("Select aeromap", aeromap_list)

    
st.title("Aeromap plot")
    
# Get the aeromap
aeromap = cpacs.get_aeromap_by_uid(aeromap_selected)
df = aeromap.df
    
# Get the options
col1, col2, col3, col4 = st.columns(4)
with col1:
    x_axis = st.selectbox("x", PARAMS_COEFS)
with col2:
    y_axis = st.selectbox("y", PARAMS_COEFS)  
with col3:
    remaning = [item for item in PARAMS_COEFS if item not in [x_axis, y_axis]]
    filt = st.selectbox("Filter by:", remaning)
with col4:
    value_list = df[filt].unique()
    value_selected = st.multiselect("Filter value:", value_list, value_list[0])

# Plot aeromap
fig, ax = plt.subplots()
plt.style.use('seaborn-whitegrid')
for value in value_selected:
    mylabel = f"{filt}={value}"
    ax.plot(df[x_axis][df[filt]==value],df[y_axis][df[filt]==value], "o", label=mylabel)
ax.set_xlabel(x_axis)
ax.set_ylabel(y_axis)
ax.legend()
st.pyplot(fig)
    

# Workaround to create a folder picker dialog
root = tk.Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)

st.write('## Save figure')
fig_name = st.text_input("Figure name:","myfigure.png")
if not fig_name.endswith(".png"):
    fig_name = fig_name + ".png"
    
st.write('Please select a folder to save the figure:')
clicked = st.button('Select & Save')
if clicked:
    dirname = st.text_input('Selected folder:', filedialog.askdirectory(master=root))
    fig_path = os.path.join(dirname, fig_name)
    fig.savefig(fig_path)
    st.success("This figure has been saved!")    