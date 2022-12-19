import sys
import clr
import time


clr.AddReference("MissionPlanner.Utilities") # includes the Utilities class
time.sleep(10)                                             # wait 10 seconds before starting
print 'Starting Mission'
Script.ChangeMode("Guided")                     # changes mode to "Guided"
print 'Guided Mode'
item = MissionPlanner.Utilities.Locationwp() # creating waypoint
lat = 39.343674                                           # Latitude value
lng = -86.029741                                         # Longitude value
alt = 45.720000                                           # altitude value
MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat)     # sets latitude
MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng)   # sets longitude
MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt)     # sets altitude
print 'WP 1 set'
MAV.setGuidedModeWP(item)                                    # tells UAV "go to" the set lat/long @ alt
print 'Going to WP 1'
time.sleep(10)                                                            # wait 10 seconds
print 'Ready for next WP'
lat = 39.345358
lng = -86.029054
alt = 76.199999
MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat)
MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng)
MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt)
print 'WP 2 set'
MAV.setGuidedModeWP(item)
print 'Going to WP 2'
time.sleep(10)
print 'Ready for next WP'
lat = 39.342106
lng = -86.031371
alt = 53.340000
MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat)
MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng)
MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt)
print 'WP 3 set'
MAV.setGuidedModeWP(item)
print 'Going to WP 3'
time.sleep(10)
print 'Ready for next WP'
lat = 39.343540
lng = -86.028732
alt = 53.199999
MissionPlanner.Utilities.Locationwp.lat.SetValue(item,lat)
MissionPlanner.Utilities.Locationwp.lng.SetValue(item,lng)
MissionPlanner.Utilities.Locationwp.alt.SetValue(item,alt)
print 'WP 4 set'
MAV.setGuidedModeWP(item)
print 'Going to WP 4'
time.sleep(10)
print 'Mission Complete'
#MAV.setMode(RETURN_TO_LAUNCH)
Script.ChangeMode("RTL")                                      # Return to Launch point
print 'Returning to Launch'
time.sleep(10)
Script.ChangeMode("LOITER")                                # switch to "LOITER" mode
print 'LOITERING'