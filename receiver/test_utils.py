import time
import random

def read_virtual_mouse(frame_rate):
    time.sleep(1 / frame_rate)
    return random.randint(0, 255).to_bytes(1, 'big')

class TestPrinter:
    def __init__(self, status):
        self.active = status
    
    def simple_print(self, name, data):
        if not self.active:
            return
        print('\n[ TESTING ] From ' + name)
        print(data)
        print()
    