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

    def check_bit(self, sample_slide):
        if self.init_timestamp and CHECK_BIT == 'BY_TIME':
            x, y = divide_coordinate(self.window)
            if x[-1] >= self.init_timestamp + 1 / FRAME_RATE:
                bit = '1' if y[-1] == one else '0'
                if bit == '1':
                    sample_slide.push(np.array([[x[-1], one]]))
                else:
                    sample_slide.push(np.array([[x[-1], zero]]))
                self.init_timestamp = x[-1]
                return bit
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

        if num_one / y.size >= 0.9:
            if self.last_detected < self.window.size * 0.9:
                self.last_detected += 1
                return None
            self.last_detected = 0
            sample_slide.push(np.array([[x.mean(), one]]))
            if CHECK_BIT == 'BY_TIME':
                self.init_timestamp = x.mean()
            return '1'
        elif num_zero / y.size >= 0.9:
            if self.last_detected < self.window.size * 0.9:
                self.last_detected += 1
                return None
            self.last_detected = 0
            sample_slide.push(np.array([[x.mean(), zero]]))
            if CHECK_BIT == 'BY_TIME':
                self.init_timestamp = x.mean()
            return '0'
        else:
            self.last_detected += 1
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
        else:
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
        return self.decode()

    def decode(self):
        if MANCHESTER_MODE:
            temp_str = ''.join(self.window)[-len(PREAMBLE_STR) - BITS_NUM * 2:]
            #if DETAILS:
            #    print(temp_str)
            sub_str = re.findall(self.pattern, temp_str)
            if sub_str == []:
                return
            possible_dataB = []
            possible_dataD = []
            for i in sub_str:
                i_removed_preamble = sim_fix(i[len(PREAMBLE_STR):])
                if len(i_removed_preamble) != 2 * BITS_NUM:
                    continue
                bit_str = Manchester_decode(i_removed_preamble)
                if not bit_str:
                    continue
                decoded_num = bit_str2num(bit_str)
                if DETAILS:
                    print(bit_str)
                    print(decoded_num)
                possible_dataB.append(bit_str)
                possible_dataD.append(decoded_num)
            return possible_dataB, possible_dataD
        elif CRC4:
            #if DETAILS:
            #    print(temp_str)
            if len(self.window) < BITS_NUM + 4:
                return
            possible_dataB = []
            possible_dataD = []
            i_removed_preamble = ''.join(self.window)[-BITS_NUM-4:]
            if not crc_validate(i_removed_preamble[:BITS_NUM], i_removed_preamble[-4:]):
                return
            bit_str = i_removed_preamble[:BITS_NUM]
            decoded_num = bit_str2num(bit_str)
            if DETAILS:
                print(bit_str)
                print(decoded_num)
            possible_dataB.append(bit_str)
            possible_dataD.append(decoded_num)
            return possible_dataB, possible_dataD
        elif fiveBsixB:
            # only for 10b12b
            if len(self.window) < len(PREAMBLE_STR) + BITS_NUM + 2:
                return
            temp_str = ''.join(self.window)[-len(PREAMBLE_STR) - BITS_NUM - 2:]
            #if DETAILS:
            #    print(temp_str)
            sub_str = re.findall(self.pattern, temp_str)
            if sub_str == []:
                return
            possible_dataB = []
            possible_dataD = []
            for i in sub_str:
                i_removed_preamble = i[len(PREAMBLE_STR):]
                if len(i_removed_preamble) != 2 + BITS_NUM:
                    continue
                try:
                    bit_str = REVERSE_DIC[i_removed_preamble]
                except:
                    continue
                if not bit_str:
                    continue
                decoded_num = bit_str2num(bit_str)
                if DETAILS:
                    print(bit_str)
                    print(decoded_num)
                possible_dataB.append(bit_str)
                possible_dataD.append(decoded_num)
            return possible_dataB, possible_dataD
        else:
            bit_str = ''.join(self.window)[-len(PREAMBLE_STR) - BITS_NUM:]
            if DETAILS:
                print(bit_str)
            sub_str = re.findall(self.pattern, bit_str)
            decoded_data = [i[len(PREAMBLE_STR):] for i in sub_str]
            decoded_num = [bit_str2num(i) for i in decoded_data]
            if decoded_data != []:
                if DETAILS:
                    print(decoded_data)
                    print(decoded_num)
                return decoded_data, decoded_num
            

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

    def most_frequent_ele(self):
        assert self.location_mod
        return max(self.occur_times, key=self.occur_times.get)

    def reset(self):
        self.window = np.array([])


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
if TESTING_MODE:
    location_list = []
    dataB_list = []
    dataD_list = []
    delay_list = []


def update():
    global location_list, dataB_list, dataD_list, delay_list
    global q 
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
        elif raw_frames_m.window[-1][0] - lasttime_interpolated > INTERPOLATION_INTERVAL: # conduct once interpolation per 0.1 second
            # probe = min(raw_frames_m.window[-1][0]-0.1, lasttime_interpolated + INTERPOLATION_INTERVAL)
            # condition = np.logical_and(raw_frames_m.window[:, 0]>lasttime_interpolated, raw_frames_m.window[:, 0]<=probe)
            probe = raw_frames_m.window[-1][0]
            condition = raw_frames_m.window[:, 0]>lasttime_interpolated
            raw_frames_m_not_interpolated = \
                raw_frames_m.window[condition]
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

                    result = bit_arr.update(one_bit, sample_arr)
                    if result:
                        possible_dataB = result[0] 
                        possible_dataD = result[1]
                        if possible_dataB != []:
                            print(possible_dataB[0])
                            location_range = hld(possible_dataB[0], SIZE, '1', '0')
                            if TESTING_MODE:
                                delay = time.time() - divide_coordinate(one_bit.window)[0].mean()
                                for i in possible_dataB:
                                    dataB_list.append(i)
                                for i in possible_dataD:
                                    dataD_list.append(i)
                                delay_list.append(delay)
                                location_list.append((location_range[1][1], location_range[0][1]))
                                temp_arr = np.array(dataD_list)
                                print('Total Num in ' + str(dur) + 's: ' + str(temp_arr.size))
                                print('Correct Num: ' + str(sum(temp_arr == fixed_val)))
                                print('Correct Percentage: ' + str(sum(temp_arr == fixed_val) / temp_arr.size))
                                correct_bit_num_arr = []
                                for i in dataB_list:
                                    correct_bit_num_arr.append(sum(np.array(list(i)) == np.array(list(fixed_bit_arr))))
                                print('Average Correct Number of Bits: ' + str(np.array(correct_bit_num_arr).mean()))
                                print('Average Delay: ' + str(np.array(delay_list).mean()))
                            if DETAILS:
                                print(possible_dataB[0])
                                print(possible_dataD[0])
                                print('delay: ' + str(time.time() - divide_coordinate(one_bit.window)[0].mean()))
                                print(location_range[1][1], location_range[0][1])
                            location_arr.push((location_range[1][1], location_range[0][1]))
                            print('Most likely location: ' + str(location_arr.most_frequent_ele()))

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


            lasttime_interpolated = probe
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

# if TESTING_MODE:
#     time.sleep(5)
#     temp_arr = np.array(dataD_list)
#     print('Total Num in ' + str(dur) + 's: ' + str(temp_arr.size))
#     print('Correct Num: ' + str(sum(temp_arr == fixed_val)))
#     print('Correct Percentage: ' + str(sum(temp_arr == fixed_val) / temp_arr.size))
#     correct_bit_num_arr = [sum(np.array([int(str_i) for str_i in list(i)]) == fixed_bit_arr) for i in dataB_list]
#     print('Pencentage of Correct Number of Bits: ' + str(np.array(correct_bit_num_arr).mean()))

    

if FORCED_EXIT:
    p.terminate()

