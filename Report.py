import os
import numpy as np
import math
import time
import collections
from crccheck.crc import Crc4Itu
from scipy.fftpack import fft,ifft
from setting import *
from utils import *
from SlideWindow import TupleSlideArray

class Report:
    def __init__(self, dur, fixed_val=None, fixed_bit_arr=None):
        self.location_arr = TupleSlideArray([], LOCATION_SLIDE_WINDOW_SIZE, True)
        self.binary_loc_arr = collections.deque(maxlen=LOCATION_SLIDE_WINDOW_SIZE)
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
        self.binary_loc_arr.append(list(possible_dataB[0]))
        delay = time.time() - divide_coordinate(one_bit.window)[0].mean()
        self.delay_list.append(delay)

        ######################################
        tmp_np = np.array(self.binary_loc_arr)
        freq_binary_loc = ''
        for i in range(BITS_NUM):
            col = tmp_np[:,i]
            col = col.astype(int)
            if sum(col) / col.size > 0.5:
                freq_binary_loc = freq_binary_loc + '1'
            else:
                freq_binary_loc = freq_binary_loc + '0'
        freq_loc = bit_str2num(freq_binary_loc)
        location = naive_location(freq_loc, SIZE)
        print('Current Location: ', end='')
        print(location)
        ######################################

        self.dataB_list.append(possible_dataB[0])
        self.dataD_list.append(possible_dataD[0])

        temp_arr = np.array(self.dataD_list)
        print('Total Num in ' + str(self.dur) + 's: ' + str(temp_arr.size))
        print('Correct Num: ' + str(sum(temp_arr == fixed_val)))
        print('Correct Percentage: ' + str(sum(temp_arr == fixed_val) / temp_arr.size))
        correct_bit_num_arr = []
        for i in self.dataB_list:
            correct_bit_num_arr.append(sum(np.array(list(i)) == np.array(list(fixed_bit_arr))))
        print('Average Correct Number of Bits: ' + str(np.array(correct_bit_num_arr).mean()))
        print('Average Delay: ' + str(np.array(self.delay_list).mean()))
    
    def get_final_report(self):
        pass
        # time.sleep(5)
        # temp_arr = np.array(self.dataD_list)
        # print('Total Num in ' + str(self.dur) + 's: ' + str(temp_arr.size))
        # print('Correct Num: ' + str(sum(temp_arr == self.fixed_val)))
        # if temp_arr.size != 0:
        #     print('Correct Percentage: ' + str(sum(temp_arr == self.fixed_val) / temp_arr.size))
        # correct_bit_num_arr = [sum(np.array([int(str_i) for str_i in list(i)]) == self.fixed_bit_arr) for i in self.dataB_list]
        # print('Pencentage of Correct Number of Bits: ' + str(np.array(correct_bit_num_arr).mean()))