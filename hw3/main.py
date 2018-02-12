import os
import time
import Connection
import messages


class StartUp:
    def __init__(self):
        self.port = 1234
        self.addr = 'localhost'
        self.id = "default"
        self.drone = {
            "ardupath": "/home/jwalke17/git/ardupilot" 
            "vehicle_type": "VRTL",
            "vehicle_id": "ND-1",     
            "home": [41.697947, -86.233919]
                     }
        self.connection = None
        self.from_dronology = messages.Messages()
        
        
    def start(self):
        self.connection = Connection.Connection(self.from_dronology, addr=self.addr, port=self.port, g_id=self.id)
        self.connection.start()
    
    
    
if __name__ == '__main__':
    start = StartUp()
    start.start()
    