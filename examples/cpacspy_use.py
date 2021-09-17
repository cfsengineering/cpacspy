# Script to show how to use the cpacspy package 

import sys

sys.path.append('../src/')

# Importing cpacspy
from cpacspy.cpacspy import CPACS


# Load a CPACS file
my_cpacs = CPACS('D150_simple.xml')

# For each object you can print it to what it contains
print(my_cpacs)
print(my_cpacs.aircraft)

# Aircraft reference value
print('Ref lenght:',my_cpacs.aircraft.ref_lenght, 'm')
print('Ref area:',my_cpacs.aircraft.ref_area, 'm^2')
print('Ref point:', f'({my_cpacs.aircraft.ref_point_x},{my_cpacs.aircraft.ref_point_y},{my_cpacs.aircraft.ref_point_z}) m')

# Wing specific values
my_cpacs.aircraft.ref_wing_idx = 1 # To choose which wing value will be used
print('Main wing aspect ratio',my_cpacs.aircraft.wing_ar)
print('Main wing area',my_cpacs.aircraft.wing_area)
print('Main wing span',my_cpacs.aircraft.wing_span)

# Get list of all available aeroMaps
print(my_cpacs.get_aeromap_uid_list())

# Loop in all aeroMaps
for aeromap in my_cpacs.aeromap:
    print('---')
    print(aeromap.uid)
    print(aeromap.description)

# Get values from an aeromap
one_aeromap = my_cpacs.get_aeromap_by_uid('extended_aeromap')
print(one_aeromap.get('angleOfAttack',alt=15500.0,aos=0.0,mach=0.3))
print(one_aeromap.get('cl',alt=15500.0,aos=0.0,mach=0.3))
print(one_aeromap.get('angleOfAttack',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))
print(one_aeromap.get('cd',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))

# Plot aeromap
#one_aeromap.plot('cd','cl',alt=15500,aos=0.0,mach=0.5)
#one_aeromap.plot('angleOfAttack','cd',alt=15500,aos=0.0,mach=0.5)

# Add new values to the aeromap
simple_aeromap = my_cpacs.get_aeromap_by_uid('aeromap_test2')
simple_aeromap.add_values(mach=0.555,alt=15000,aos=0.0,aoa=2.4,cd=0.001,cl=1.1,cs=0.22,cmd=0.22)
simple_aeromap.save()


### Add a new aeromap with values

# Create new aeromap 
new_aeromap = my_cpacs.create_aeromap('my_new_aeromap')

# Add a description
new_aeromap.description = 'Test of creation of a new aeromap'

# Fill the aeromap with parameter and coefficients
for i in range(12):
    new_aeromap.add_values(mach=0.555,alt=15000,aos=0.0,aoa=i,cd=0.001*i*i,cl=0.1*i,cs=0.0,cmd=0.0,cml=1.1,cms=0.0)

# Print the aeromap
print(new_aeromap)

# Save the aeromamp
new_aeromap.save()


# Duplicate an aeromap
duplicated_aeromap = my_cpacs.duplicate_aeromap('my_new_aeromap', 'my_duplicated_aeromap')
duplicated_aeromap.add_values(mach=0.666,alt=10000,aos=0.0,aoa=2.4,cd=0.001,cl=1.1,cs=0.22,cmd=0.22)
duplicated_aeromap.save()

# Export to CSV
duplicated_aeromap.export_csv('aeromap.csv')

# Import from CSV
imported_aeromap = my_cpacs.create_aeromap_from_csv('aeromap.csv','imported_aeromap')
imported_aeromap.description = 'This aeromap has been imported from a CSV file'
imported_aeromap.save()


# CD0 and oswald factor
aspect_ratio = my_cpacs.aircraft.wing_ar
cd0,e = one_aeromap.get_cd0_oswald(aspect_ratio,alt=15500.0,aos=0.0,mach=0.5)

# Get Force
one_aeromap.calculate_forces(my_cpacs.aircraft)
print(one_aeromap.get('cd',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))
print(one_aeromap.get('drag',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))

# Save all the change in a CPACS file
my_cpacs.save_cpacs('D150_simple_updated_aeromap.xml',overwrite=True)
