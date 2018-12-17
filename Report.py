import os
import numpy as np
import math
import time
from crccheck.crc import Crc4Itu
from scipy.fftpack import fft,ifft
from setting import *
from utils import *
from SlideWindow import TupleSlideArray

class Report:
    def __init__(self, dur, fixed_val=None, fixed_bit_arr=None):
        self.location_arr = TupleSlideArray([], LOCATION_SLIDE_WINDOW_SIZE, True)
        self.ans_arr = np.array([])
        self.dis_arr = np.array([]) 
        self.delay_arr = np.array([])
        self.location_list = []
        self.dataB_list = []
        self.dataD_list = []
        self.delay_list = []
        self.dur = dur
        self.fixed_val = fixed_val
        self.fixed_bit_arr = fixed_bit_arr
        self.detailed = False
    
    def show_detail(self):
        self.detailed = True

    def get_test_report(self, one_bit, possible_dataB, possible_dataD, fixed_bit_arr, fixed_val):
        location_range = hld(possible_dataB[0], SIZE, '1', '0')
        delay = time.time() - divide_coordinate(one_bit.window)[0].mean()
        for i in possible_dataB:
            self.dataB_list.append(i)
        for i in possible_dataD:
            self.dataD_list.append(i)
        self.delay_list.append(delay)
        self.location_list.append((location_range[1][1], location_range[0][1]))
        temp_arr = np.array(self.dataD_list)
        print('Total Num in ' + str(self.dur) + 's: ' + str(temp_arr.size))
        print('Correct Num: ' + str(sum(temp_arr == fixed_val)))
        print('Correct Percentage: ' + str(sum(temp_arr == fixed_val) / temp_arr.size))
        correct_bit_num_arr = []
        for i in self.dataB_list:
            correct_bit_num_arr.append(sum(np.array(list(i)) == np.array(list(fixed_bit_arr))))
        print('Average Correct Number of Bits: ' + str(np.array(correct_bit_num_arr).mean()))
        print('Average Delay: ' + str(np.array(self.delay_list).mean()))
        self.location_arr.push((location_range[1][1], location_range[0][1]))
        if self.detailed:
            print(possible_dataD[0])
            print('delay: ' + str(time.time() - \
                divide_coordinate(one_bit.window)[0].mean()))
            print('Current Location: ', end='')
            print(location_range[1][1], location_range[0][1])
    
    def get_final_report(self):
        time.sleep(5)
        temp_arr = np.array(self.dataD_list)
        print('Total Num in ' + str(self.dur) + 's: ' + str(temp_arr.size))
        print('Correct Num: ' + str(sum(temp_arr == self.fixed_val)))
        if temp_arr.size != 0:
            print('Correct Percentage: ' + str(sum(temp_arr == self.fixed_val) / temp_arr.size))
        # correct_bit_num_arr = [sum(np.array([int(str_i) for str_i in list(i)]) == self.fixed_bit_arr) for i in self.dataB_list]
        # print('Pencentage of Correct Number of Bits: ' + str(np.array(correct_bit_num_arr).mean()))