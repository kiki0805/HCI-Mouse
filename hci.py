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

dur = input('Duration: ')
dur = 10 if dur == '' else int(dur)
if TESTING_MODE:
    fixed_val = int(input('[TESTING MODE] Fixed value: '))
    fixed_bit_arr = num2bin(fixed_val, BITS_NUM)
    ans_arr = np.array([])
    dis_arr = np.array([]) 
    delay_arr = np.array([])


preamble = np.array(PREAMBLE_LIST) 
times_interpolate = TIMES_INTERPOLATE
points_per_frame = POINTS_PER_FRAME # combine to one


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
    response = device.ctrl_transfer(bmRequestType = 0x40, #Write
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
line5 = plt.scatter([], [], marker='x', color='black', label='power')
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
        if location_mod:
            self.occur_times = {}
            if self.window != np.array([]):
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

    def push(self, chunk_or_ele): # chunk for coordinate, ele for binary bits
        assert chunk_or_ele.size <= self.size
        if self.window.size + chunk_or_ele.size > self.size:
            if self.location_mod:
                print(self.window)
                print(self.occur_times)
                self.occur_times[self.window[0]] -= 1
            self.window = self.window[int((chunk_or_ele.size + self.window.size) - self.size):]
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
        if self.window.size > self.size:
            print('outflow')
        return abs(self.window.size - self.size) <= 1

    def output(self):
        bit_str = ''.join(self.window.tolist())
        print(bit_str)
        location_range = hld(bit_str, SIZE, '1', '0')
        print(location_range[1][1], location_range[0][1])

        if TESTING_MODE:
            global ans_arr, fixed_val, dis_arr
            num = bit_str2num(bit_str)
            print(num)
            ans_arr = np.append(ans_arr, num)
            print('current accuracy(decimal): ' + str(sum(ans_arr == np.array([fixed_val] * ans_arr.size)) / ans_arr.size))
            
            dis_arr = np.append(dis_arr, sum(np.array(list(bit_str)) == np.array(list(fixed_bit_arr))))
            print('current mean number of error bits(decimal): ' + str(BITS_NUM - dis_arr.mean()))

        return (location_range[1][1], location_range[0][1])

    def most_frequent_ele(self):
        assert self.location_mod
        return max(self.occur_times, key=self.occur_times.get)

    def reset(self):
        self.window = np.array([])

    def cal_power(self, preamble):
        if self.window.size < preamble.size:
            return 0
        
        return sum(preamble == self.window[:preamble.size])

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

    def check_bit(self, sample_slide):
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

        if num_one / y.size >= 0.9:
            if self.last_detected < self.window.size * 0.9:
                self.last_detected += 1
                return None
            self.last_detected = 0
            sample_slide.push(np.array([[x.mean(), one]]))
            return '1'
        elif num_zero / y.size >= 0.9:
            if self.last_detected < self.window.size * 0.9:
                self.last_detected += 1
                return None
            self.last_detected = 0
            sample_slide.push(np.array([[x.mean(), zero]]))
            return '0'
        else:
            self.last_detected += 1
            return None

class BitSlideArray:
    def __init__(self, window, size, location_mod=False):
        self.pattern = PREAMBLE_STR + '\d{' + str(BITS_NUM) + '}'  
        self.window = window
        self.size = size
        self.last_detected = -1
        self.location_mod = location_mod
        if location_mod:
            self.occur_times = {}
            if self.window != np.array([]):
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

    def update(self, one_bit, sample_arr):
        bit_detected = one_bit.check_bit(sample_arr)
        if not bit_detected:
           # if self.window.size != 0:
           #     self.reset()
            return
        self.push(bit_detected)
        self.decode()

    def decode(self):
        bit_str = ''.join(self.window)
        print(bit_str)
        sub_str = re.findall(self.pattern, bit_str)
        decoded_data = [i[len(PREAMBLE_STR):] for i in sub_str]
        decoded_num = [bit_str2num(i) for i in decoded_data]
        if decoded_data != []:
            print(decoded_data)
            print(decoded_num)

    def push(self, ele):
        if self.window.size >= self.size:
            if self.location_mod:
                print(self.window)
                print(self.occur_times)
                self.occur_times.pop(self.window[0])
            self.window = np.delete(self.window, 0, axis=0)
        self.window = np.append(self.window, ele)
        if self.location_mod:
            if ele in self.occur_times:
                self.occur_times[ele] += 1
            else:
                self.occur_times[ele] = 1

    def is_full(self):
        return self.window.size == self.size

    def output(self):
        bit_str = ''.join(self.window.tolist())
        print(bit_str)
        location_range = hld(bit_str, SIZE, '1', '0')
        print(location_range[1][1], location_range[0][1])

        if TESTING_MODE:
            global ans_arr, fixed_val, dis_arr
            num = bit_str2num(bit_str)
            print(num)
            ans_arr = np.append(ans_arr, num)
            print('current accuracy(decimal): ' + str(sum(ans_arr == np.array([fixed_val] * ans_arr.size)) / ans_arr.size))
            
            dis_arr = np.append(dis_arr, sum(np.array(list(bit_str)) == np.array(list(fixed_bit_arr))))
            print('current mean number of error bits(decimal): ' + str(BITS_NUM - dis_arr.mean()))


        return (location_range[1][1], location_range[0][1])


        #loc_x = num % SIZE[0]
        #loc_y = math.floor(num / SIZE[0])
        #print(loc_x, loc_y)

    def most_frequent_ele(self):
        assert self.location_mod
        return max(self.occur_times, key=self.occur_times.get)

    def reset(self):
        self.window = np.array([])

    def cal_power(self, preamble):
        if self.window.size < preamble.size:
            return 0
        
        return sum(preamble == self.window[:preamble.size])


class TupleSlideArray:
    def __init__(self, window, size, location_mod=False):
        self.window = window
        self.size = size
        self.location_mod = location_mod
        if location_mod:
            self.occur_times = {}
            if self.window != []:
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

    def push(self, ele):
        if len(self.window) >= self.size:
            if self.location_mod:
                self.occur_times[self.window[0]] -= 1
            del self.window[0]
        self.window.append(ele)
        if self.location_mod:
            if ele in self.occur_times:
                self.occur_times[ele] += 1
            else:
                self.occur_times[ele] = 1

    def is_full(self):
        return len(self.window) == self.size

    def most_frequent_ele(self):
        assert self.location_mod
        return max(self.occur_times, key=self.occur_times.get)

    def reset(self):
        self.window = np.array([])

location_arr = TupleSlideArray([], LOCATION_SLIDE_WINDOW_SIZE, True)


x4decode = np.array([])
y4decode = np.array([])
y_mean4decode = np.array([])

def update():
    global q, points_per_frame
    global x, y, line, ax, y_fixed
    raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, None, int(MOUSE_FRAME_RATE / 2))  # maintain raw frames within around 2 seconds
    frames_m = SlideArray(np.array([[]]), int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line2, \
            int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 2)) # maintain frames within 2 seconds after interpolation
    y_mean = SlideArray(np.array([[]]), int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line3, \
            int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 2)) # maintain frames within 2 seconds after interpolation
    one_bit = SlideArray(np.array([[]]), math.ceil(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / FRAME_RATE), line4, \
            int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 2)) # maintain frames within 2 seconds after interpolation
    sample_arr = SlideArray(np.array([[]]), int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line5, \
            int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 2), scatter_mode=True) # maintain frames within 2 seconds after interpolation

    binary_arr =  SlideArray(np.array([[]]), math.ceil(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line1, \
            int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 2)) # maintain frames within 2 seconds after interpolation

    bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM + len(PREAMBLE_STR)) * 2) # maintain frames within 2 seconds after interpolation


    max_pixel = 200
    min_pixel = 100
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

        if lasttime_interpolated == 0:
            frames_m.push(np.array([raw_frames_m.window[0]]))
            lasttime_interpolated = raw_frames_m.window[0][0]
        elif raw_frames_m.window[-1][0] - lasttime_interpolated > 1: # conduct once interpolation per 0.1 second
            raw_frames_m_not_interpolated = raw_frames_m.window[raw_frames_m.window[:, 0]>lasttime_interpolated]
            frames_m_interpolated = interpolate_f(raw_frames_m_not_interpolated)

            l = len(frames_m_interpolated)
            temp_x = np.array([])
            temp_y = np.array([])
            for i in range(l + 1):
                if i >= 2:
                    max_pixel = frames_m.window[:, 1].max()
                    min_pixel = frames_m.window[:, 1].min()

                if i < l:
                    temp_x = np.append(temp_x, frames_m_interpolated[i][0])
                    temp_y = np.append(temp_y, frames_m_interpolated[i][1])
                if temp_x.size % POINTS_TO_COMBINE == 0 or i == l:
                    if temp_x.size == 0:
                        continue
                    frames_m.push(np.array([[temp_x.mean(), temp_y.mean()]]))
                    x, y = divide_coordinate(frames_m.window)
                    #y_mean.push(np.array([[x[-1], y[max(0, y.size - MEAN_WIDTH):].mean()]]))
                    y_mean.push(np.array([[x[-1], (max_pixel + min_pixel) / 2]]))
                    if y_mean.window.size == 2:
                        one_bit.push(np.array([[x[-1], one]]))

                    elif abs(y_mean.window[-1][1] - frames_m.window[-1][1]) < 5:
                        if one_bit.window.size != 0:
                            one_bit.push(np.array([[x[-1], one_bit.window[-1].tolist()[1]]]))
                        else:
                            one_bit.push(np.array([[x[-1], one]]))
                    elif y_mean.window[-1][1] < frames_m.window[-1][1]:
                        one_bit.push(np.array([[x[-1], zero]]))
                    else:
                        one_bit.push(np.array([[x[-1], one]]))

                    binary_arr.push(np.array([[x[-1], one_bit.window[-1].tolist()[1]]]))
                    # fix
                    if one_bit.window.size > 4:
                        if one_bit.window[-2][1] != one_bit.window[-1][1] and \
                                one_bit.window[-2][1] != one_bit.window[-3][1]:
                                    one_bit.window[-2][1] = one_bit.window[-1][1]
                                    binary_arr.window[-2][1] = binary_arr.window[-1][1]

                    bit_arr.update(one_bit, sample_arr)

                    temp_x = np.array([])
                    temp_y = np.array([])

                    if GRAPHICS:
                        one_bit.update_line_data()
                        binary_arr.update_line_data()
                        y_mean.update_line_data()
                        sample_arr.update_line_data()
                        #raw_frames_m.update_line_data()
                        frames_m.update_line_data()
                        ax.relim() # renew the data limits
                        ax.autoscale_view(True, True, True) # rescale plot view
                        plt.draw() # plot new figure
                        plt.pause(1e-17)


            lasttime_interpolated = raw_frames_m_not_interpolated[-1][0]
q = Queue()
p = Process(target=update) # for display
p.start()


start = time.time()
global_count = 0


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

