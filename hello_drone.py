#Import DroneKit-Python
from dronekit import connect, VehicleMode, time

#Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Print out vehicle state information.')
parser.add_argument('--connect',help="vehicle connection target string.")
args = parser.parse_args()

connection_string = args.connect
sitl = None


#Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle.
#   Set `wait_ready=True` to ensure default attributes are populated before `connect()` returns.
print "\nConnecting to vehicle on: %s" % connection_string
vehicle = connect(connection_string, wait_ready=True)

vehicle.wait_ready('autopilot_version')

#Get some vehicle attributes (state)
print "Get some vehicle attribute values:"
print "GPS: %s" % vehicle.gps_0
print "Attitude: %s" % vehicle.attitude
print "Velocity: %s" % vehicle.velocity
print "Airspeed: %s" % vehicle.airspeed
print "Groundspeed: %s" % vehicle.groundspeed
print "Battery: %s" % vehicle.battery
print "Last Heartbeat: %s" % vehicle.last_heartbeat
print "Is Armable?: %s" % vehicle.system_status.state
print "Mode: %s" % vehicle.mode.name # settable

# Close vehicle object before exiting script
vehicle.close()

time.sleep(5)

print("Completed")
