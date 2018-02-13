import threading
import time
import os
import json
import dronekit
import dronekit_sitl
from pymavlink import mavutil

class Copter:
    def __init__(self, drone, to_dronology):
        self.sitl = None
        self.vehicle = None
        self.drone = drone
        self.to_dronology = to_dronology
    
    def goto(self, lat, lon, alt):
        self.vehicle.simple_goto(dronekit.LocationGlobalRelative(lat, lon, alt))
        
    def set_armed(self, armed):
        if self.vehicle.armed != armed:
            if armed:
                while not self.vehicle.is_armable:
                    time.sleep(2.0)

            self.vehicle.armed = armed
            if self.drone['vehicle_type'] == 'PHYS':
                time.sleep(2.0)
            while self.vehicle.armed != armed:
                self.vehicle.armed = armed
                if self.drone['vehicle_type'] == 'PHYS':
                    time.sleep(2.0)
        
    def set_groundspeed(self, groundspeed):
        message = self.vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 0, groundspeed, 0, 0, 0, 0, 0)
        self.vehicle.send_mavlink(message)
        self.vehicle.flush()
        
    def set_home(self, lat, lon, alt):

        message = self.vehicle.message_factory.command_long_encode(0, 0, mavutil.mavlink.MAV_CMD_DO_SET_HOME, 0, 2, 0, 0, 0, lat, lon, alt)
        self.vehicle.send_mavlink(message)
        self.vehicle.flush()
        
    def set_mode(self, mode):
        self.vehicle.mode = dronekit.VehicleMode(mode)
        if self.drone['vehicle_type'] == 'PHYS':
            time.sleep(5.0)
        check_mode = self.vehicle.mode.name

        while check_mode != mode:
            self.vehicle.mode = dronekit.VehicleMode(mode)
            if self.drone['vehicle_type'] == 'PHYS':
                time.sleep(5.0)
            check_mode = self.vehicle.mode.name
        
    def takeoff(self, alt):
        self.set_mode(MODE_GUIDED)
        self.set_armed(armed=True)
        self.vehicle.simple_takeoff(alt)
        if self.drone['vehicle_type'] == 'PHYS':
            time.sleep(5.0)
        
    def connect_vehicle(self):
        #threading.Thread(target=self.connect_vehicle_thread).start()

    
    #def connect_vehicle_thread(self):
        print("Entering connect thread =======================")
        drone = self.drone
        ip = self.drone['ip']
        vehicle = None
        baud = 57600
        status = 1
        ardupath = drone["ardupath"]
        defaults = os.path.join(ardupath, 'Tools', 'autotest', 'default_params', 'copter.parm')

        home = drone['home']
        if len(home) == 2:
            home = tuple(home) + (0, 0)
        else:
            home = tuple(home)

        try:
            if self.drone['vehicle_type'] == 'PHYS':
                vehicle = dronekit.connect(ip, wait_ready=True, baud=baud)

            elif self.drone['vehicle_type'] == 'VRTL':
                sitl_args = [
                    '--model', '+',
                    '--home', ','.join(map(str, home)),
                    '--rate', str(10),
                    '--speedup', str(1.0),
                    '--defaults', defaults
                ]
                sitl = dronekit_sitl.SITL(path=os.path.join(ardupath, 'build', 'sitl', 'bin', 'arducopter'))
                sitl.launch(sitl_args, await_ready=True)
                tcp, ip, port = sitl.connection_string().split(':')
                conn_string = ':'.join([tcp, ip, port])
                vehicle = dronekit.connect(conn_string, baud=baud)
                vehicle.wait_ready(timeout=120)
                self.sitl = sitl

            else:
                print("Error: connect_vehicle")

            while not vehicle.is_armable:
                time.sleep(3.0)

            time.sleep(3.0)
            self.vehicle = vehicle

        except dronekit.APIException:
            status = -1

        if status >= 0:
            message = {}
            message['type'] = "handshake" 
            message['uavid'] = drone['vehicle_id']
            message['sendtimestamp'] = long(round(time.time() * 1000))
            message['data'] = {}
            message['data']['home'] = home
            self.to_dronology.put_message(str(message))
            
        else:
            print("Error: connect_vehicle1")
            
        print("exiting connect thread +++++++++++++++++++++++++++++")
        
            
    def create_state_message(self):
        vehicle = self.vehicle
        print(vehicle.location.global_relative_frame.lat)
        message = {} 
        message['type'] = "state" 
        message['uavid'] = self.drone['vehicle_id']
        message['sendtimestamp'] = long(round(time.time() * 1000))
        message['data'] = {}
        message['data']['location'] = {}
        message['data']['location']['x'] = vehicle.location.global_relative_frame.lat
        message['data']['location']['y'] = vehicle.location.global_relative_frame.lon
        message['data']['location']['z'] = vehicle.location.global_relative_frame.alt
        message['data']['attitude'] = vehicle.attitude
        message['data']['velocity'] = {}
        message['data']['velocity']['x'] = vehicle.velocity[0]
        message['data']['velocity']['y'] = vehicle.velocity[1]
        message['data']['velocity']['z'] = vehicle.velocity[2]
        message['data']['status'] = str(vehicle.system_status.state)
        message['data']['mode'] = str(vehicle.mode.name)
        message['data']['armed'] = vehicle.armed
        message['data']['armable'] = vehicle.is_armable
        message['data']['groundspeed'] = vehicle.groundspeed
        message['data']['batterystatus'] = vehicle.battery
        return message
    
    def send_state_message(self):
        self.to_dronology.put_message(str(self.create_state_message()))
        
        
