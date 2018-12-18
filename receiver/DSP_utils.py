import collections
import numpy as np


"""
Note: 
    1. Skip values larger than 240.
    2. Add 128 to values less than 128.
"""
def fix_raw_value(response):
    if not response:
        return
    val = int.from_bytes(response, 'big')
    val_fixed = val
    if val_fixed < 128:
        val_fixed += 128
    if val_fixed > 240:
        return
    return val_fixed


class DataManager:
    def __init__(self):
        self.data = {}
    
    def register_data(self, label, max_len):
        self.data[label] = collections.deque(maxlen=max_len)

    def update_data(self, label, point):
        self.data[label].append(point)
