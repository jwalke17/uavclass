import os
import time
import Connection
import messages


class Everything:
    def __init__(self):
        self.port = 1234
        self.addr = 'localhost'
        self.id = "default_groundstation"
        self.drone = {
            "ardupath": "/home/jwalke17/git/ardupilot" 
            "vehicle_type": "VRTL",
            "vehicle_id": "ND-1",     
            "home": [41.697947, -86.233919]
                     }
        self.connection = None
        self.controlstation = None
        self.from_dronology = messages.Messages()
        self.to_dronology = messages.Messages()
        
        
        
    def start(self):
        self.connection = Connection.Connection(self.from_dronology, addr=self.addr, port=self.port, g_id=self.id)
        self.controlstation = controlstation.ControlStation(self.from_dronology, self.to_dronology, self.connection, self.drone)
        self.connection.start()
        self.controlstation.start()
        self.controlstation.add_vehicle(self.drone)
    
    
    
if __name__ == '__main__':
    everything = Everything()
    everything.start()
    