import usb.core
import sys
import threading
from scipy.interpolate import interp1d
from scipy import interpolate
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

if GRAPHICS:
    plt.ion()

    line1, = plt.plot([], [], 'r', label='original') # plot the data and specify the 2d line
    line2, = plt.plot([], [], 'b', label='inter')
    line3, = plt.plot([], [], 'g', label='mean')
    line4, = plt.plot([], [], 'y', label='repaired')
    line5, = plt.plot([], [], 'black', label='power')
    ax = plt.gca() # get most of the figure elements 
x = np.array([])
y = np.array([])
y_fixed = np.array([])
y_mean = np.array([])

start = time.time()

class SlideArray:
    def __init__(self, window, size, line, location_mod=False):
        self.window = window
        self.line = line
        self.size = size
        self.location_mod = location_mod
        if location_mod:
            self.occur_times = {}
            if self.window != np.array([]):
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

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

    def push_chunk(self, chunk): # for coordinate
        assert chunk.size <= self.size
        if self.window.size + chunk.size > self.size:
            self.window = self.window[-(self.size - chunk.size):]
        self.window = np.concatenate((self.window, chunk))

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

def get_gap_len(y):
    old = 0
    #one_frame = int((MOUSE_FRAME_RATE - 400) * times_interpolate / FRAME_RATE) - 10
    gaps = []
    for i in range(y.size):
        ele = y[i]
        if ele != old:
            gaps.append(i)
            old = ele
    own_len = [gaps[i + 1] - gaps[i] for i in range(len(gaps) - 1)]
    return gaps, own_len


def get_continue_num_less_frame(y):
    gaps, own_len = get_gap_len(y)
    if own_len != []:
        intervals = [(gaps[i], gaps[i] + own_len[i]) for i in range(len(own_len))]

    #print(own_len)

    for i in range(len(own_len)):
        l = own_len[i]
        if l < MIN_LEN_PER_BIT: 
            y[intervals[i][0]:intervals[i][1] + 1] = y[intervals[i][0] - 1] 

    #gaps, own_len = get_gap_len(y)
    #print(own_len)

    return y

def correct(y):
    y_corrected = get_continue_num_less_frame(y)
    return y

x4decode = np.array([])
y4decode = np.array([])
y_mean4decode = np.array([])

def decode(x, y_corrected):

        # within latest 2 periods
        if x.size < 3 * times_interpolate * MOUSE_FRAME_RATE / points_per_frame:
        #if x.size < 2 * POINTS_PER_SECOND_AFTER_INTERPOLATE:
            return

        x_cut = x[-math.floor(3 * times_interpolate * MOUSE_FRAME_RATE / points_per_frame):-1]
        y_cut = y_corrected[-math.floor(3 * times_interpolate * MOUSE_FRAME_RATE / points_per_frame):-1]
        #x_cut = x[-2 * POINTS_PER_SECOND_AFTER_INTERPOLATE:-1]
        #y_cut = y_corrected[-2 * POINTS_PER_SECOND_AFTER_INTERPOLATE:-1]
        max_indexes = np.where(y_cut==np.max(y_cut))[0]
        x_interval = x_cut[1] - x_cut[0]
        points_per_screen_frame = math.floor(1 / FRAME_RATE / x_interval)

        # for align
        duration_points = 0
        old_index = -1
        for max_index in max_indexes:
            if old_index == -1:
                old_index = max_index
                continue
            if max_index - old_index == 1:
                duration_points += 1
                old_index = max_index
            else:
                old_index = max_index
                if duration_points >= int(0.7 * points_per_screen_frame) and duration_points < int(points_per_screen_frame * 1.5):
                    break
                duration_points = 0

        current_bit_index = old_index - int(duration_points / 2) # first_bit_index
        slide_arr = SlideArray(np.array([]), preamble.size)
        bit_arr = SlideArray(np.array([]), BITS_NUM)
        detected = False
        power_arr = np.array([100] * x_cut.size)
        while current_bit_index < x_cut.size:
            bit = '0' if y_cut[current_bit_index] == zero else '1'
            if detected:
                bit_arr.push(bit)
                if bit_arr.is_full():
                    cur_loc = bit_arr.output()
                    location_arr.push((cur_loc[0], cur_loc[1]))
                    print('Most likely location: ' + str(location_arr.most_frequent_ele()))
                    if TESTING_MODE:
                        global delay_arr
                        delay = time.time() - x_cut[current_bit_index]
                        delay_arr = np.append(delay_arr, delay)
                        print('current mean delay: ' + str(delay_arr.mean()))
                    bit_arr.reset()
                    detected = False
            slide_arr.push(bit)
            power = slide_arr.cal_power(preamble)
            power_arr[current_bit_index] = power**2 + 100
            if GRAPHICS:
                line5.set_xdata(x_cut[max(-x_cut.size, -int(times_interpolate * MOUSE_FRAME_RATE / points_per_frame)):])
                line5.set_ydata(power_arr[max(-power_arr.size, -int(times_interpolate * MOUSE_FRAME_RATE / points_per_frame)):])
            if power == preamble.size:
                detected = True
            #current_bit_index += duration_points
            current_bit_index += points_per_screen_frame


def update():
    global q, points_per_frame
    global x, y, line, ax, y_mean, y_fixed
    bkp_raw_frames
    raw_frames_m = SlideArray(np.array([]), MOUSE_FRAME_RATE * 2)  # maintain raw frames within around 2 seconds
    frames_m = SlideArray(np.array([]), FRAMES_PER_SECOND_AFTER_INTERPOLATE * 2) # maintain frames within 2 seconds after interpolation
    lasttime_interpolated = 0
    while True:
        response_list = np.array([])
        response_list_fixed = np.array([])
        timestamp_list = np.array([])

        single_frame_m, timestamp = q.get()
        raw_frames_m.push((timestamp, single_frame_m))
        if raw_frames_m.window[-1][0] - lasttime_interpolated > 0.1: # conduct once interpolation per 0.1 second
            raw_frames_m_not_interpolated = raw_frames_m.window[raw_frames_m.window[:, 0]>lasttime_interpolated]
            frames_m_interpolated = interpolate(raw_frames_m_not_interpolated)
            frames_m.push_chunk(frames_m_interpolated)


        '''
        for _ in range(points_per_frame):
            if not response:
                return
            val = int.from_bytes(response, 'big')
            if val > 240:
                continue
            val_fixed = val
            if val_fixed < 128:
                val_fixed += 128
            response_list = np.append(response_list, val)
            response_list_fixed = np.append(response_list_fixed, val_fixed)
            timestamp_list = np.append(timestamp_list, timestamp)
        
        new_x = timestamp_list.mean()
        new_y = response_list.mean()
        new_y_fixed = response_list_fixed.mean()

        x = np.append(x, new_x)
        y = np.append(y, new_y)
        y_fixed = np.append(y_fixed, new_y_fixed)
        y = y_fixed
        y_mean = np.append(y_mean, y[max(0, y.size - MEAN_WIDTH):-1].mean())

        if x.size > 20:
#        if x.size > (MOUSE_FRAME_RATE / points_per_frame) * 2: # maintain a window of samples in two seconds
            inter = interp1d(x, y, kind='linear')
            inter_mean = interp1d(x, y_mean, kind='linear')

            x_extend = np.linspace(x[0], x[-1], num=x.size * times_interpolate)
            #x_extend = np.linspace(x[0], x[-1], num=int(x[-1] - x[0]) * POINTS_PER_SECOND_AFTER_INTERPOLATE)
            f_extend = inter(x_extend)
            f_extend_mean = inter_mean(x_extend)
            f_extend_binary = one_bit_array(f_extend_mean.size) * (f_extend < f_extend_mean) \
                    + zero_bit_array(f_extend_mean.size) * (f_extend >= f_extend_mean)

            ##############

            y_corrected = correct(f_extend_binary)
            #t = threading.Thread(target=decode, args=(x_extend, y_corrected))
            #t.start()
            decode(x_extend, y_corrected)

            if GRAPHICS:
                line2.set_xdata(x_extend[max(-x_extend.size, -int(times_interpolate * MOUSE_FRAME_RATE / points_per_frame)):])
                line2.set_ydata(y_corrected[max(-y_corrected.size, -int(times_interpolate * MOUSE_FRAME_RATE / points_per_frame)):])
                line3.set_xdata(x[max(-x.size, -int(MOUSE_FRAME_RATE / points_per_frame)):])
                line3.set_ydata(y_mean[max(-y_mean.size, -int(MOUSE_FRAME_RATE / points_per_frame)):])
                line1.set_xdata(x[max(-x.size, -int(MOUSE_FRAME_RATE / points_per_frame)):])
                line1.set_ydata(y[max(-y.size, -int(MOUSE_FRAME_RATE / points_per_frame)):]) # set the curve with new data

                #if x_extend.size >= times_interpolate * MOUSE_FRAME_RATE / points_per_frame:
                #elif x.size >= MOUSE_FRAME_RATE / points_per_frame: 
                #    line3.set_xdata(x[-int(MOUSE_FRAME_RATE / points_per_frame):])
                #    line3.set_ydata(y_mean[-int(MOUSE_FRAME_RATE / points_per_frame):])
                #    line1.set_xdata(x[-int(MOUSE_FRAME_RATE / points_per_frame):])
                #    line1.set_ydata(y[-int(MOUSE_FRAME_RATE / points_per_frame):]) # set the curve with new data
                #    #line4.set_xdata(x[-int(MOUSE_FRAME_RATE / points_per_frame):-1])
                #    #line4.set_ydata(y_fixed[-int(MOUSE_FRAME_RATE / points_per_frame):-1]) # set the curve with new data
                #else:
                #    line2.set_xdata(x_extend)
                #    line2.set_ydata(y_corrected)
                #    line3.set_xdata(x)
                #    line3.set_ydata(y_mean)
                #    line1.set_xdata(x)
                #    line1.set_ydata(y)
                    #line4.set_xdata(x)
                    #line4.set_ydata(y_fixed)
                #if x_extend.size >= POINTS_PER_SECOND_AFTER_INTERPOLATE: 
                #    line1.set_xdata(x_extend[-POINTS_PER_SECOND_AFTER_INTERPOLATE:-1])
                #    line1.set_ydata(f_extend[-POINTS_PER_SECOND_AFTER_INTERPOLATE:-1]) # set the curve with new data
                #    line2.set_xdata(x_extend[-POINTS_PER_SECOND_AFTER_INTERPOLATE:-1])
                #    line2.set_ydata(y_corrected[-POINTS_PER_SECOND_AFTER_INTERPOLATE:-1])
                #    line3.set_xdata(x_extend[-POINTS_PER_SECOND_AFTER_INTERPOLATE:-1])
                #    line3.set_ydata(f_extend_mean[-POINTS_PER_SECOND_AFTER_INTERPOLATE:-1])
                #else:
                #    line1.set_xdata(x_extend[80:])
                #    line1.set_ydata(f_extend[80:])
                #    line2.set_xdata(x_extend[80:])
                #    line2.set_ydata(y_corrected[80:])
                #    line3.set_xdata(x_extend[80:])
                #    line3.set_ydata(f_extend_mean[80:])

        if GRAPHICS:
            ax.relim() # renew the data limits
            ax.autoscale_view(True, True, True) # rescale plot view
            plt.draw() # plot new figure

            plt.pause(1e-17)
        '''


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

