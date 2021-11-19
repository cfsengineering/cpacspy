# Script to show how to use the cpacspy package 

import sys
sys.path.append('../src/')

# Importing cpacspy
from cpacspy.cpacspy import CPACS


# Load a CPACS file
cpacs = CPACS('D150_simple.xml')

# For each object you can print it to what it contains
print(cpacs)
print(cpacs.aircraft)

# Aircraft reference value
print('Ref lenght:',cpacs.aircraft.ref_lenght, 'm')
print('Ref area:',cpacs.aircraft.ref_area, 'm^2')
print('Ref point:', f'({cpacs.aircraft.ref_point_x},{cpacs.aircraft.ref_point_y},{cpacs.aircraft.ref_point_z}) m')

# Wing specific values
# To choose another reference wing (by default the largest wing is the reference one)
# cpacs.aircraft.ref_wing_idx = 3 

print('Main wing aspect ratio',cpacs.aircraft.wing_ar)
print('Main wing area',cpacs.aircraft.wing_area)
print('Main wing span',cpacs.aircraft.wing_span)

# Get list of all available aeroMaps
print(cpacs.get_aeromap_uid_list())

# Loop in all aeroMaps
for aeromap in cpacs.aeromaps:
    print('---')
    print(aeromap.uid)
    print(aeromap.description)

# Get values from an aeromap
one_aeromap = cpacs.get_aeromap_by_uid('extended_aeromap')
print(one_aeromap.get('angleOfAttack',alt=15500.0,aos=0.0,mach=0.3))
print(one_aeromap.get('cl',alt=15500.0,aos=0.0,mach=0.3))
print(one_aeromap.get('angleOfAttack',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))
print(one_aeromap.get('cd',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))

# Plot aeromap
# one_aeromap.plot('cd','cl',alt=15500,aos=0.0,mach=0.5)
# one_aeromap.plot('angleOfAttack','cd',alt=15500,aos=0.0,mach=0.5)

# Add new values to the aeromap
simple_aeromap = cpacs.get_aeromap_by_uid('aeromap_test2')
simple_aeromap.add_row(mach=0.555,alt=15000,aos=0.0,aoa=2.4,cd=0.001,cl=1.1,cs=0.22,cmd=0.22)
simple_aeromap.save()


### Add a new aeromap with values

# Create new aeromap 
new_aeromap = cpacs.create_aeromap('my_new_aeromap')

# Add a description
new_aeromap.description = 'Test of creation of a new aeromap'

# Fill the aeromap with parameter and coefficients
for i in range(12):
    new_aeromap.add_row(mach=0.555,alt=15000,aos=0.0,aoa=i,cd=0.001*i*i,cl=0.1*i,cs=0.0,cmd=0.0,cml=1.1,cms=0.0)

# Print the aeromap
print(new_aeromap)

# Save the aeromamp
new_aeromap.save()

# Delete the aeromap
cpacs.delete_aeromap('aeromap_test1')
print(cpacs.get_aeromap_uid_list())

# Duplicate an aeromap
duplicated_aeromap = cpacs.duplicate_aeromap('my_new_aeromap', 'my_duplicated_aeromap')
duplicated_aeromap.add_row(mach=0.666,alt=10000,aos=0.0,aoa=2.4,cd=0.001,cl=1.1,cs=0.22,cmd=0.22)

# Modfiy aerocoef
print(duplicated_aeromap.get('cd'))
duplicated_aeromap.df['cd'] = duplicated_aeromap.df['cd'].add(1.0)
duplicated_aeromap.save() 
print(duplicated_aeromap.get('cd'))

# Export to CSV
duplicated_aeromap.export_csv('aeromap.csv')

# Import from CSV
imported_aeromap = cpacs.create_aeromap_from_csv('aeromap.csv','imported_aeromap')
imported_aeromap.description = 'This aeromap has been imported from a CSV file'
imported_aeromap.save()

# AeroMap with Damping Derivatives coefficients
aeromap_dd = cpacs.duplicate_aeromap('imported_aeromap','aeromap_dd')
aeromap_dd.description = 'Aeromap with damping derivatives coefficients'

# Add damping derivatives coefficients to the aeromap
# Coefficients must be one of the following: 'cd', 'cl', 'cs', 'cmd', 'cml', 'cms'
# Axis must be one of the following: 'dp', 'dq', 'dr'
# The sign of the rate will determine if the coefficient are stored in /positiveRate or /negativeRate
aeromap_dd.add_damping_derivatives(alt=15000,mach=0.555,aos=0.0,aoa=0.0,coef='cd',axis='dp',value=0.001,rate=-1.0)

# Same in a loop
for i in range(11):
    aeromap_dd.add_damping_derivatives(alt=15000,mach=0.555,aos=0.0,aoa=i+1,coef='cd',axis='dp',value=0.001*i+0.002,rate=-1.0)
aeromap_dd.save()

# Get damping derivatives coefficients
print(aeromap_dd.get_damping_derivatives(alt=15000,mach=0.555,coef='cd',axis='dp',rates='neg'))
print(aeromap_dd.get_damping_derivatives(alt=15000,mach=0.555,aoa=[4.0,6.0,8.0],coef='cd',axis='dp',rates='neg'))

# Also works with the simple "get" function, but the "coef name" is a bit more complicated
print(aeromap_dd.get('dampingDerivatives_negativeRates_dcddpStar',aoa=[4.0,6.0,8.0]))

# Damping derivatives coefficients can alos be plotted
# aeromap_dd.plot('angleOfAttack','dampingDerivatives_negativeRates_dcddpStar',alt=15000,aos=0.0,mach=0.555)


## Analyses

# CD0 and oswald factor
aspect_ratio = cpacs.aircraft.wing_ar
cd0,e = one_aeromap.get_cd0_oswald(aspect_ratio,alt=15500.0,aos=0.0,mach=0.5)

# Get Force
one_aeromap.calculate_forces(cpacs.aircraft)
print(one_aeromap.get('cd',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))
print(one_aeromap.get('drag',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))


## Save

# Save all the change in a CPACS file
cpacs.save_cpacs('D150_simple_updated_aeromap.xml',overwrite=True)


