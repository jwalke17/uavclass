#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import numpy as np
import math
import re

# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string. If not specified, SITL automatically started and used.")
args = parser.parse_args()

connection_string = args.connect
sitl = None

# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


filename = "coordinates.txt"
default_altitude = 15

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

#sleeps for given num, and prints coordinates to coordinates file every second
def sleep_print(num):
    file = open(filename, "a")
    while num > 0:
        time.sleep(1)
        line = "%s" % vehicle.location.global_frame
        lat = re.match(r'.*lat=(.*),lon.*', line)
        lon = re.match(r'.*lon=(.*),.*', line)
        file.write("{},{}".format(lat.group(1),lon.group(1)))
        file.write("\n")
        num = num - 1
    file.close()


def go_to_point(lat, long, alt):
    point = LocationGlobalRelative(lat, long, alt)
    vehicle.simple_goto(point)

#assuming uav starts on pole side opposite direction of movement vector
#loops around one pole in 4 parts 45 degrees apart from each other,
#~5 meters from the pole center
def loop_pole(vector, side, pole, alt):
    # .000047 lat is ~5 meter
    # .000069 long is ~5 meter

    theta = np.radians(45 * side)
    c, s = np.cos(theta), np.sin(theta)
    matrix45 = np.matrix([[c, -s], [s, c]])
    c, s = np.cos(theta * 2), np.sin(theta * 2)
    matrix90 = np.matrix([[c, -s], [s, c]])
    c, s = np.cos(theta * 3), np.sin(theta * 3)
    matrix135 = np.matrix([[c, -s], [s, c]])

    point = np.array(np.add(pole, np.multiply([.000047, .000069], matrix135.dot(vector))))
    point = point.flatten()
    go_to_point(point[0], point[1], alt)
    sleep_print(15)

    point = np.array(np.add(pole, np.multiply([.000047, .000069], matrix90.dot(vector))))
    point = point.flatten()
    go_to_point(point[0], point[1], alt)
    sleep_print(5)

    point = np.array(np.add(pole, np.multiply([.000047, .000069], matrix45.dot(vector))))
    point = point.flatten()
    go_to_point(point[0], point[1], alt)
    sleep_print(5)

    point = np.array(np.add(pole, np.multiply([.000047, .000069], vector)))
    point = point.flatten()
    go_to_point(point[0], point[1], alt)
    sleep_print(5)


#navigates all poles in pole array below
def navigate_poles(alt):
    poles = [[41.71480, -86.24300],
             [41.71480, -86.24250],
             [41.71480, -86.24200],
             [41.71480, -86.24150],
             [41.71480, -86.24100]]

    #movement vector determines which direction drone moves
    movement_vector = np.subtract(poles[1], poles[0])
    mv_mag = math.sqrt(movement_vector[0]*movement_vector[0] + movement_vector[1]*movement_vector[1])
    movement_vector = np.true_divide(movement_vector, mv_mag)

    go_to_point(41.71435, -86.24187, alt)
    sleep_print(3)

    side = 1
    go_to_point(poles[0][0], poles[0][1] - .00025, alt)
    sleep_print(35)
    for pole in poles:
        loop_pole(movement_vector, side, pole, alt)
        side = side * -1

    go_to_point(41.71435, -86.24187, alt)
    sleep_print(40)

arm_and_takeoff(default_altitude)

print("Set default/target airspeed to 5")
vehicle.airspeed = 5

open(filename, "w").close()
navigate_poles(default_altitude)

print("Returning to Launch")
vehicle.mode = VehicleMode("RTL")

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

# Shut down simulator if it was started.
if sitl:
    sitl.stop()
