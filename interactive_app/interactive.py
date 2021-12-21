import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

from cpacspy.cpacspy import CPACS
from cpacspy.utils import PARAMS_COEFS


# Load a CPACS file
cpacs = CPACS("../examples/D150_simple.xml")
df_is_loaded = None

# Page setups
st.set_page_config(page_title="cpacspy interactive plot")
logo = Image.open('../logo/logo_transparant_bg.png')
st.sidebar.image(logo)
st.title("Aeromap plot")

# Get the aeromap from multiselection box
aeromap_uid_list = cpacs.get_aeromap_uid_list()
aeromap_selected = st.sidebar.multiselect("Select aeromap", aeromap_uid_list)
aeromap_list = [cpacs.get_aeromap_by_uid(aeromap_uid) for aeromap_uid in aeromap_selected]
    
# If aeromap(s) are selected, plot them
if aeromap_list: 
    
    # temp (TODO: could be improve, how to look into all df)
    df_tmp = aeromap_list[0].df
     
    # Get the options (TODO: improve layout)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        x_axis = st.selectbox("x", PARAMS_COEFS)
    with col2:
        y_axis = st.selectbox("y", PARAMS_COEFS)  
    with col3:
        remaning = [item for item in PARAMS_COEFS if item not in [x_axis, y_axis]]
        filt = st.selectbox("Filter by:", remaning)
    with col4:
        value_list = df_tmp[filt].unique()
        value_selected = st.multiselect("Filter value:", value_list, value_list[0])

    with col3:
        remaning2 = [item for item in PARAMS_COEFS if item not in [x_axis, y_axis,filt]]
        filt2 = st.selectbox("Filter2 by:", remaning2)
    with col4:
        value_list2 = df_tmp[filt2].unique()
        value_selected2 = st.multiselect("Filter2 value:", value_list2, value_list2[0])

    fig = go.Figure()
    for aeromap in aeromap_list:
        
        if not len(value_selected):
            value_selected = value_list
            
        for value in value_selected:
            if not len(value_selected2):
                value_selected2 = value_list2
                
            for value2 in value_selected2:
                df = aeromap.df[(aeromap.df[filt]==value) & (aeromap.df[filt2]==value2)]
                legend = f"{aeromap.uid}<br>{filt}={value}<br>{filt2}={value2}"
                fig.add_trace(go.Scatter(x=df[x_axis], y=df[y_axis], name=legend))
                
    fig.update_traces(mode="markers+lines",hovertemplate = 'x: %{x:.2f} \ny: %{y:.2f} ',)
    fig.update_layout(
        xaxis=dict(title=x_axis),
        yaxis=dict(title=y_axis),
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
    
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
