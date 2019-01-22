import usb.core
import sys
import threading
from multiprocessing import Process, Queue
import time
import math
import numpy as np
import usb.util
from setting import *

def init():
    device.ctrl_transfer(bmRequestType = 0x40, #Write
                                         bRequest = 0x01,
                                         wValue = 0x0000,
                                         wIndex = 0x0D, #PIX_GRAB register value
                                         data_or_wLength = None
                                         )

class SlideArray:
    def __init__(self, size):
        self.window = None
        self.size = size

    def push(self, ele): # chunk for coordinate, ele for binary bits
        if self.is_full():
            self.window = self.window[1:]
        if self.window is None:
            self.window = ele
            return
        assert ele[0][0] > self.window[-1][0]
        self.window = np.vstack((self.window, ele))

    def is_full(self):
        if self.window is None:
            return False
        return self.window.size == self.size * 2

    def reset(self):
        self.window = None


def update():
    global raw_frames_m
    global q
    raw_file_count = 0
    while True:

        response, timestamp = q.get()
        if not response:
            return

        val = int.from_bytes(response, 'big')
        val_fixed = val
        # print(val)
        if val_fixed < 128:
            val_fixed += 128
        if val_fixed > 240:
            continue

        # print(timestamp, val_fixed)
        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))
        if raw_frames_m.is_full():
            fn = './data/' + str(raw_file_count) + '_raw_v3.bin'
            raw_frames_m.window.tofile(fn)
            print('[ Expection: 45 ] Write done: ' + fn)
            raw_frames_m.reset()
            raw_file_count += 1

dur = input('Duration: ')
dur = 10 if dur == '' else int(dur)

device = usb.core.find(idVendor=0x046d, idProduct=0xc077)

if device.is_kernel_driver_active(0):
    device.detach_kernel_driver(0)

device.set_configuration()

raw_frames_m = SlideArray(MOUSE_FRAME_RATE * 60)

q = Queue()
p = Process(target=update) # for display
p.start()

start = time.time()
while time.time() - start < dur: # 11000
    response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                    bRequest = 0x01,
                    wValue = 0x0000,
                    wIndex = 0x0D, #PIX_GRAB register value
                    data_or_wLength = 1
                    )
    init()
    q.put((response, time.time()))
print('All done.')

