import usb.core
import re
import sys
from interpolate_f import interpolate_f
import threading
from scipy.interpolate import interp1d
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
from matplotlib import animation
import time
import math
import numpy as np
import usb.util
from setting import *
from utils import *
from fiveBsixB_coding import *


dur = input('Duration: ')
dur = 10 if dur == '' else int(dur)

preamble = np.array(PREAMBLE_LIST) 
times_interpolate = TIMES_INTERPOLATE


one = 125
zero = 200

def one_bit_array(size):
    return np.array([one] * size)

def zero_bit_array(size):
    return np.array([zero] * size)

device = usb.core.find(idVendor=0x046d, idProduct=0xc077)

if device.is_kernel_driver_active(0):
    device.detach_kernel_driver(0)

device.set_configuration()

def init():
    device.ctrl_transfer(bmRequestType = 0x40, #Write
                                         bRequest = 0x01,
                                         wValue = 0x0000,
                                         wIndex = 0x0D, #PIX_GRAB register value
                                         data_or_wLength = None
                                         )

init()

plt.ion()

line1, = plt.plot([], [], 'r', label='original') # plot the data and specify the 2d line
line2, = plt.plot([], [], 'b', label='inter')
ax = plt.gca() # get most of the figure elements 
x = np.array([])
y = np.array([])
y_fixed = np.array([])
y_mean = np.array([])

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
        if location_mod:
            self.occur_times = {}
            if self.window != np.array([]):
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

    def push(self, chunk_or_ele): # chunk for coordinate, ele for binary bits
        assert chunk_or_ele.size <= self.size * 2
        if self.window.size + chunk_or_ele.size > self.size * 2:
            if self.location_mod:
                print(self.window)
                print(self.occur_times)
                self.occur_times[self.window[0]] -= 1
            self.window = self.window[int((chunk_or_ele.size + self.window.size) - self.size * 2):]
        if self.window.size == 0:
            self.window = chunk_or_ele
        else:
            self.window = np.concatenate((self.window, chunk_or_ele))
        if self.location_mod:
            if chunk_or_ele in self.occur_times:
                self.occur_times[chunk_or_ele] += 1
            else:
                self.occur_times[chunk_or_ele] = 1

    def is_full(self):
        if self.window.size > self.size * 2:
            print('outflow')
        return self.window.size == self.size * 2

    def most_frequent_ele(self):
        assert self.location_mod
        return max(self.occur_times, key=self.occur_times.get)

    def reset(self):
        self.window = np.array([])

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
    global location_list, dataB_list, dataD_list, delay_list
    global q 
    global x, y, ax, y_fixed
    raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, line1, MOUSE_FRAME_RATE)  # maintain raw frames within around 2 seconds
    # raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, None, int(MOUSE_FRAME_RATE / 2))  # maintain raw frames within around 2 seconds
    frames_m = SlideArray(np.array([[]]), int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line2, \
            int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 2)) # maintain frames within 2 seconds after interpolation

    lasttime_interpolated = 0
    while True:

        response, timestamp = q.get()
        if not response:
            return

        val = int.from_bytes(response, 'big')
        val_fixed = val
        if val_fixed < 128:
            val_fixed += 128
        if val_fixed > 240:
            continue

        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))
        if raw_frames_m.line:
            raw_frames_m.update_line_data()
            ax.relim() # renew the data limits
            ax.autoscale_view(True, True, True) # rescale plot view
            plt.draw() # plot new figure
            plt.pause(1e-17)

        if lasttime_interpolated == 0:
            frames_m.push(np.array([raw_frames_m.window[0]]))
            lasttime_interpolated = raw_frames_m.window[0][0]
        elif raw_frames_m.window[-1][0] - lasttime_interpolated > END_INTERVAL: # conduct once interpolation per 0.1 second
            end_probe = lasttime_interpolated + INTERPOLATION_INTERVAL
            condition = np.logical_and(raw_frames_m.window[:, 0]>=lasttime_interpolated, raw_frames_m.window[:, 0]<end_probe+EXTRA_LEN)

            raw_frames_m_not_interpolated = raw_frames_m.window[condition]
            if EXTRA_LEN != 0:
                frames_m_interpolated = interpolate_f(raw_frames_m_not_interpolated, interval=INTERPOLATION_INTERVAL)
            else:
                frames_m_interpolated = interpolate_f(raw_frames_m_not_interpolated)

            l = len(frames_m_interpolated)
            temp_x = np.array([])
            temp_y = np.array([])
            for i in range(l + 1):
                if i < l:
                    temp_x = np.append(temp_x, frames_m_interpolated[i][0])
                    temp_y = np.append(temp_y, frames_m_interpolated[i][1])
                if temp_x.size % POINTS_TO_COMBINE == 0 or i == l:
                    if temp_x.size == 0:
                        continue
                    frames_m.push(np.array([[temp_x.mean(), temp_y.mean()]]))
                   
                    temp_x = np.array([])
                    temp_y = np.array([])

                    if GRAPHICS and not raw_frames_m.line:
                        frames_m.update_line_data()
                        ax.relim() # renew the data limits
                        ax.autoscale_view(True, True, True) # rescale plot view
                        plt.draw() # plot new figure
                        plt.pause(1e-17)

            lasttime_interpolated = end_probe

q = Queue()
p = Process(target=update) # for display
p.start()


start = time.time()
global_count = 0
if LOOP:
    dur = 999999999

while time.time() - start < dur:
    response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                     bRequest = 0x01,
                     wValue = 0x0000,
                     wIndex = 0x0D, #PIX_GRAB register value
                     data_or_wLength = 1
                     )
    #time.sleep(0.0003)
    q.put((response, time.time()))
    global_count += 1

print('Frame rate: ' + str(global_count / (time.time() - start)))


if FORCED_EXIT:
    p.terminate()

