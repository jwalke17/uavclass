import os
import time
import Connection
import messages
import threading
import controlstation


class Everything:
    def __init__(self):
        self.port = 1234
        self.addr = 'localhost'
        self.id = "default_groundstation"
        self.drone = {"ardupath": "/home/jwalke17/git/ardupilot", "vehicle_type": "VRTL", "vehicle_id": "ND-1","home": [41.697947, -86.233919], "ip": None}
        self.connection = None
        self.controlstation = None
        self.from_dronology = messages.Messages()
        self.to_dronology = messages.Messages()
        
    def start(self):
        threading.Thread(target=self.start_thread).start()
        
    def wait(self):
        while true:
            time.sleep(3)
        
    def start_thread(self):
        self.connection = Connection.Connection(self.from_dronology, addr=self.addr, port=self.port, g_id=self.id)
        self.controlstation = controlstation.ControlStation(self.from_dronology, self.to_dronology, self.connection, self.drone)
        self.connection.start()
        self.controlstation.add_vehicle()
        self.controlstation.start()
    
    
    
if __name__ == '__main__':
    everything = Everything()
    everything.start()
    