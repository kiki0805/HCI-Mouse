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
if TESTING_MODE:
    fixed_val = int(input('[ TESTING MODE ] Fixed value: '))
    fixed_bit_arr = num2bin(fixed_val, BITS_NUM)
    ans_arr = np.array([])
    dis_arr = np.array([]) 
    delay_arr = np.array([])


preamble = np.array(PREAMBLE_LIST) 
times_interpolate = TIMES_INTERPOLATE


one = 130
zero = 140

def one_bit_array(size):
    return np.array([one] * size)

def zero_bit_array(size):
    return np.array([zero] * size)

device = usb.core.find(idVendor=0x046d, idProduct=0xc077)
#device = usb.core.find(idVendor=0x2188, idProduct=0x0ae1)

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
line3, = plt.plot([], [], 'g', label='mean')
line4, = plt.plot([], [], 'y', label='repaired')
line5 = plt.scatter([], [], marker='x', color='black')
line6, = plt.plot([], [], 'm')
ax = plt.gca() # get most of the figure elements 
x = np.array([])
y = np.array([])
y_fixed = np.array([])
y_mean = np.array([])

start = time.time()
last_bit = None
total_one = 0
total_zero = 0
global_mean_one = None
global_mean_zero = None
global_var_one = None
global_var_zero = None

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


class OneBitArray(SlideArray):
    def push(self, chunk_or_ele): # chunk for coordinate, ele for binary bits
        assert chunk_or_ele.size <= self.size * 3
        if self.window.size + chunk_or_ele.size > self.size * 3:
            self.window = self.window[int((chunk_or_ele.size + self.window.size) - self.size * 3):]
        if self.window.size == 0:
            self.window = chunk_or_ele
        else:
            self.window = np.concatenate((self.window, chunk_or_ele))

    def is_full(self):
        if self.window.size > self.size * 3:
            print('outflow')
        return self.window.size == self.size * 3
    
    def check_bit(self, sample_slide):
        if self.init_timestamp:
            x, y = divide_coordinate(self.window)
            mid_index = int(x.size/3)
            if x[mid_index] >= self.init_timestamp + 1 / FRAME_RATE * 0.9:
                num_one = 0 
                num_zero = 0
                len_zero = 5
                len_one = 5
                pct = 1

                left_zero = math.floor((y.size-len_zero)/2)
                for e in y[left_zero:left_zero + len_zero].tolist():
                    if e == zero:
                        num_zero += 1

                left_one = math.floor((y.size-len_one)/2)
                for e in y[left_one:left_one + len_one].tolist():
                    if e == one:
                        num_one += 1

                if num_one / len_one >= pct:
                    sample_slide.push(np.array([[x[mid_index], one]]))
                    self.init_timestamp = x[mid_index]
                    # print(self.window[mid_index, 2])
                    print('Var for BIT 1: ' + str(np.var(self.window[mid_index-2:mid_index+2,2])))
                    print('Mean for BIT 1: ' + str(np.mean(self.window[mid_index-2:mid_index+2,2])))
                    return '1'
                elif num_zero / len_zero >= pct:
                    sample_slide.push(np.array([[x[mid_index], zero]]))
                    self.init_timestamp = x[mid_index]
                    # print(self.window[mid_index, 2])
                    print('Var for BIT 0: ' + str(np.var(self.window[mid_index-2:mid_index+2,2])))
                    print('Mean for BIT 0: ' + str(np.mean(self.window[mid_index-2:mid_index+2,2])))
                    return '0'
                    
            return

        if not self.is_full():
            return None
        x, y = divide_coordinate(self.window)
        num_one = 0
        num_zero = 0
        for e in y.tolist():
            if e == one:
                num_one += 1
            else:
                num_zero += 1

        pct = 0.7
        if num_one / y.size > pct and num_zero == 1:
            self.init_timestamp = x[math.floor((x.size - 1) / 2) - 1] if y[-1] == zero \
                else x[math.floor((x.size - 1) / 2) + 1]
            sample_slide.push(np.array([[self.init_timestamp, one]]))
            return '1'
        elif num_zero / y.size > pct and num_one == 1:
            self.init_timestamp = x[math.floor((x.size - 1) / 2) - 1] if y[-1] == one \
                else x[math.floor((x.size - 1) / 2) + 1]
            sample_slide.push(np.array([[self.init_timestamp, zero]]))
            return '0'
        return None

class BitSlideArray:
    def __init__(self, window, size, location_mod=False):
        if MANCHESTER_MODE:
            self.pattern = PREAMBLE_STR + '\d{' + str(BITS_NUM * 2) + '}'
        elif fiveBsixB:
            # only for 10b12b
            self.pattern = PREAMBLE_STR + '\d{12}'
        elif CRC4:
            self.pattern = None
            self.pending_count = 0
        else:
            self.pattern = PREAMBLE_STR + '\d{' + str(BITS_NUM) + '}'  
        self.window = window
        self.size = size
        self.last_detected = -1
        self.location_mod = location_mod
        

    def update(self, one_bit, sample_arr):
        bit_detected = one_bit.check_bit(sample_arr)
        if not bit_detected:
           # if self.window.size != 0:
           #     self.reset()
            return
        self.push(bit_detected)
        return


    def push(self, ele):
        if self.window.size >= self.size:
            self.window = np.append(self.window, ele)
        

    def is_full(self):
        return self.window.size == self.size

    def reset(self):
        self.window = np.array([])


def update():
    global location_list, dataB_list, dataD_list, delay_list
    global q 
    global x, y, ax, y_fixed
    raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE, line2, int(MOUSE_FRAME_RATE / 16))
    y_mean = SlideArray(np.array([[]]), MOUSE_FRAME_RATE, line3, int(MOUSE_FRAME_RATE / 16))
    one_bit = OneBitArray(np.array([[]]), math.ceil(FRAMES_PER_SECOND_AFTER_INTERPOLATE / \
            POINTS_TO_COMBINE / FRAME_RATE), line4, \
            math.floor((MOUSE_FRAME_RATE - 200) / FRAME_RATE)) 
    sample_arr = SlideArray(np.array([[]]), MOUSE_FRAME_RATE, line5, \
            int(MOUSE_FRAME_RATE / 16), scatter_mode=True)

    binary_arr =  SlideArray(np.array([[]]), MOUSE_FRAME_RATE, line1, int(MOUSE_FRAME_RATE / 16))

    if MANCHESTER_MODE:
        bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM * 2 + len(PREAMBLE_STR)) * 2) # maintain frames within 2 seconds after interpolation
    elif fiveBsixB:
        bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM + 2 + len(PREAMBLE_STR)) * 2)
    elif CRC4:
        bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM + 4) * 2)
    else:
        bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM + len(PREAMBLE_STR)) * 2) # maintain frames within 2 seconds after interpolation

    max_pixel = 200
    min_pixel = 100
    while True:

        response, timestamp = q.get()
        if not response:
            return

        val = int.from_bytes(response, 'big')
        # print(val)
        val_fixed = val
        if val_fixed < 128:
            val_fixed += 128
        if val_fixed > 240:
            continue

        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))

        x, y = divide_coordinate(raw_frames_m.window)
        y_mean.push(np.array([[x[-1], y[max(0, int(y.size / 2) - MEAN_WIDTH):].mean()]]))
        
        if y_mean.window.size == 2:
            one_bit.push(np.array([[x[-1], one, one]]))

        elif y_mean.window[-1][1] < y[-1]:
            one_bit.push(np.array([[x[-1], zero, y[-1]]]))
        else:
            one_bit.push(np.array([[x[-1], one, y[-1]]]))

        binary_arr.push(np.array([[x[-1], one_bit.window[-1].tolist()[1]]]))
        # fix one bit peak
        if one_bit.window.size > 6:
            if one_bit.window[-2][1] != one_bit.window[-1][1] and \
                    one_bit.window[-2][1] != one_bit.window[-3][1]:
                        one_bit.window[-2][1] = one_bit.window[-1][1]
                        binary_arr.window[-2][1] = binary_arr.window[-1][1]

        bit_arr.update(one_bit, sample_arr)
        ###############################################

        if GRAPHICS:
            one_bit.update_line_data()
            binary_arr.update_line_data()
            y_mean.update_line_data()
            sample_arr.update_line_data()
            raw_frames_m.update_line_data()
            ax.relim() # renew the data limits
            ax.autoscale_view(True, True, True) # rescale plot view
            plt.draw() # plot new figure
            plt.pause(1e-17)

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
    init()
    q.put((response, time.time()))
    global_count += 1

print('Frame rate: ' + str(global_count / (time.time() - start)))

if FORCED_EXIT:
    p.terminate()

