# Script to show the example of utilization of the cpacspy package 

import sys

sys.path.append('../src/')

# When the cpacspy package is installed, you should import it like that:
from cpacspy.cpacspy import CPACS

# Load the CPACS file and all AeroMap in it
my_cpacs = CPACS('D150_simple.xml')

# Print info about the CPACS file
print(my_cpacs)

# Print info about the Aircraft 
print(my_cpacs.aircraft)

# Aircraft reference value
print('Ref lenght:',my_cpacs.aircraft.ref_lenght, 'm')
print('Ref area:',my_cpacs.aircraft.ref_area, 'm^2')
print('Ref point:', f'({my_cpacs.aircraft.ref_point_x},{my_cpacs.aircraft.ref_point_y},{my_cpacs.aircraft.ref_point_z}) m')

# Aircraft specific values
# Wing
my_cpacs.aircraft.ref_wing_idx = 1
print('Main wing aspect ratio',my_cpacs.aircraft.wing_ar)
print('Main wing area',my_cpacs.aircraft.wing_area)
print('Main wing span',my_cpacs.aircraft.wing_span)

# Get list of all available aeroMaps
print(my_cpacs.get_uid_list())

# Loop in all aeroMaps
for aeromap in my_cpacs.aeromap:
    print('---')
    print(aeromap.uid)
    print(aeromap.description)

# Get values from an aeromap
ThisAeroMap = my_cpacs.get_aeromap_by_uid('extended_aeromap')
print(ThisAeroMap.get('angleOfAttack',alt=15500.0,aos=0.0,mach=0.3))
print(ThisAeroMap.get('cl',alt=15500.0,aos=0.0,mach=0.3))
print(ThisAeroMap.get('angleOfAttack',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))
print(ThisAeroMap.get('cd',alt=15500.0,aos=0.0,mach=[0.3,0.4,0.5]))

# Plot aeromap
#ThisAeroMap.plot('cd','cl',alt=15500,aos=0.0,mach=0.5)
#ThisAeroMap.plot('angleOfAttack','cd',alt=15500,aos=0.0,mach=0.5)

# Add new values to the aeromap
SimpleAeroMap = my_cpacs.get_aeromap_by_uid('aeromap_test2')
SimpleAeroMap.add_values(mach=0.555,alt=15000,aos=0.0,aoa=2.4,cd=0.001,cl=1.1,cs=0.22,cmd=0.22)
SimpleAeroMap.save()

# Create new aeromap 
NewAeromap = my_cpacs.create_aeromap('my_new_aeromap')

for i in range(12):
    NewAeromap.add_values(mach=0.555,alt=15000,aos=0.0,aoa=i,cd=0.001*i*i,cl=0.1*i,cs=0.0,cmd=0.0,cml=1.1,cms=0.0)

NewAeromap.description = 'Test of creation of a new aeromap'
NewAeromap.save()

# Duplicate an aeromap
DuplicatedAeromap = my_cpacs.duplicate_aeromap('my_new_aeromap', 'my_duplicated_aeromap')
DuplicatedAeromap.add_values(mach=0.666,alt=10000,aos=0.0,aoa=2.4,cd=0.001,cl=1.1,cs=0.22,cmd=0.22)
DuplicatedAeromap.save()

# Export to CSV
DuplicatedAeromap.export_csv('aeromap.csv')

# Import from CSV
ImportedAeromap = my_cpacs.create_aeromap_from_csv('aeromap.csv','imported_aeromap')
ImportedAeromap.description = 'This aeromap has been imported from a CSV file'
ImportedAeromap.save()
print(ImportedAeromap)

# CD0 and oswald factor
aspect_ratio = my_cpacs.aircraft.wing_ar
cd0,e = ThisAeroMap.get_cd0_oswald(aspect_ratio,alt=15500.0,aos=0.0,mach=0.5)

# ...



# Save all the change in a CPACS file
my_cpacs.save_cpacs('D150_simple_updated_aeromap.xml',overwrite=True)



