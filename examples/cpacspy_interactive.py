# Importing cpacspy
from cpacspy.cpacspy import CPACS

# Load a CPACS file
cpacs = CPACS("D150_simple.xml")

# Test interactive plot with streamlit
cpacs.interactive_plot()