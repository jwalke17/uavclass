import threading
import MyVehicle
import json
import time

MODE_LAND = 'LAND'
MODE_GUIDED = 'GUIDED'
MODE_RTL = 'RTL'
MODE_LOITER = 'LOITER'

class ControlStation:
    def __init__(self, from_dronology, to_dronology, connection, drone):
        self.connection = connection
        self.from_dronology = from_dronology
        self.to_dronology = to_dronology
        self.drone = drone
        self.keep_running = 1
        self.ready_to_start = 0
        self.vehicle = None
    
    def start(self):
        while self.keep_running:
            in_msgs = self.from_dronology.get_messages()
            for message in in_msgs:
                msg = json.loads(message)
                threading.Thread(target=self.handle_message, args=(msg,)).start()
                time.sleep(.1)
                
            in_msgs = self.to_dronology.get_messages()
            for msg in in_msgs:
                threading.Thread(target=self.to_dronology_thread, args=(msg,)).start()
                time.sleep(.1)
            time.sleep(1)
            self.vehicle.send_state_message()
                    
    def to_dronology_thread(self, message):
        success = self.connection.send(str(message))
        if not success:
            self.to_dronology.put_message(message)
    
    def add_vehicle(self):
        vehicle = MyVehicle.Copter(self.drone, self.to_dronology)
        vehicle.connect_vehicle()
        self.vehicle = vehicle
        
    def handle_message(self, msg):
        if msg['command'] == "gotoLocation":
            self.vehicle.goto(msg['data']['x'], msg['data']['y'], msg['data']['z'])
        elif msg['command'] == "setArmed":
            self.vehicle.set_armed(msg['data']['armed'])
        elif msg['command'] == "setGroundspeed":
            self.vehicle.set_groundspeed(msg['data']['speed'])
        elif msg['command'] == "setHome":
            self.vehicle.set_home(msg['data']['x'], msg['data']['y'], msg['data']['z'])
        elif msg['command'] == "setMode":
            self.vehicle.set_mode(msg['data']['mode'])
        elif msg['command'] == "takeoff":
            self.vehicle.takeoff(msg['data']['altitude'])
        else:
            print("Error: no command {}".format(msg['command']))
        
    
        
