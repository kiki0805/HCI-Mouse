import usb.core
import re
import sys
from interpolate_f import interpolate_f
import threading
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
import time
import math
import numpy as np
import usb.util
from setting import *
from utils import *

dur = input('Duration: ')
update_time = input('update time: _s ')
update_time = -1 if update_time == '' else int(update_time)

dur = 10 if dur == '' else int(dur)
#413c:301a
#0461:4d15
#device = usb.core.find(idVendor=0x413c, idProduct=0x3010)
#device = usb.core.find(idVendor=0x046d, idProduct=0xc05b)
device = usb.core.find(idVendor=0x046d, idProduct=0xc077)

if device.is_kernel_driver_active(0):
    device.detach_kernel_driver(0)

device.set_configuration()

def init():
    device.ctrl_transfer(bmRequestType = 0x40, #Write
                                         bRequest = 0x01,
                                         wValue = 0x0000,
                                         #wIndex = 0x0D, #PIX_GRAB register value
                                         wIndex = 0x0B, #PIX_GRAB register value
                                         data_or_wLength = None
                                         )

# init()

plt.ion()

line1, = plt.plot([], [], 'r', label='original') 
ax = plt.gca() # get most of the figure elements 

start = time.time()

class SlideArray:
    def __init__(self, window, size, line, draw_interval, ele_type='coordiante', location_mod=False, sample_line=None, scatter_mode=False):
        self.scatter_mode = scatter_mode
        self.sample_line = sample_line
        self.window = window
        self.draw_interval = draw_interval
        self.line = line
        self.size = size
        self.last_detected = -1
        self.location_mod = location_mod
        self.init_timestamp = None
        self.window_of_last_one = None
        self.window_of_last_zero = None

    def push(self, chunk_or_ele): # chunk for coordinate, ele for binary bits
        assert chunk_or_ele.size <= self.size * 2
        if self.window.size + chunk_or_ele.size > self.size * 2:
            self.window = self.window[int((chunk_or_ele.size + self.window.size) - self.size * 2):]
        if self.window.size == 0:
            self.window = chunk_or_ele
        else:
            self.window = np.concatenate((self.window, chunk_or_ele))

    def is_full(self):
        if self.window.size > self.size * 2:
            print('outflow')
        return self.window.size == self.size * 2

    def update_line_data(self):
        if self.line is None:
            return
        if self.window.size == 0:
            return

        x, y = divide_coordinate(self.window)
        if x.size < self.draw_interval:
            if self.scatter_mode:
                self.line.set_offsets(self.window)
                return
            self.line.set_xdata(x)
            self.line.set_ydata(y)
        else:
            if self.scatter_mode:
                self.line.set_offsets(self.window[-self.draw_interval:,:])
                return
            self.line.set_xdata(x[-self.draw_interval:])
            self.line.set_ydata(y[-self.draw_interval:])

def update():
    global q, update_time
    raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, line1, int(MOUSE_FRAME_RATE * 0.05))
    # raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, line1, MOUSE_FRAME_RATE)
    time1 = None
    while True:

        response, timestamp = q.get()
        if not time1:
            time1 = timestamp
        if not response:
            return

        val = int.from_bytes(response, 'big')
        val_fixed = val
        if val_fixed < 128:
           # print('+ 128')
           val_fixed += 128
        if val_fixed > 240:
           # print('delete')
           continue

        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))
        if raw_frames_m.line and timestamp - time1 > update_time:
            raw_frames_m.update_line_data()
            ax.relim() # renew the data limits
            ax.autoscale_view(True, True, True) # rescale plot view
            plt.draw() # plot new figure
            if update_time != -1:
                time1 = timestamp
                plt.pause(update_time)
            else:
                plt.pause(1e-6)

q = Queue()
p = Process(target=update) # for display
p.start()


start = time.time()
global_count = 0
flag = 0
while time.time() - start < dur:
    response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                     bRequest = 0x01,
                     wValue = 0x0000,
                     #wIndex = 0x0D, #PIX_GRAB register value
                     wIndex = 0x0B, #PIX_GRAB register value
                     data_or_wLength = 1
                     )
    
    init()
    q.put((response, time.time()))
    global_count += 1

print('Frame rate: ' + str(global_count / (time.time() - start)))
p.terminate()
# sys.exit()
