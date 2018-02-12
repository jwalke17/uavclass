import threading
import os
import time


class Messages:
    def __init__(self):
        self.lock = threading.Lock()
        self.messages = []
        
    def put_message(self, msg):
        with self.lock:
            self.messages.append(msg)
            
    def get_messages(self):
        msgs = []
        with self.lock:
            while self.messages:
                msgs.append(self.messages.pop(0))
                
        return msgs