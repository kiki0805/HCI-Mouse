import os
from crccheck.crc import Crc4Itu
from scipy.fftpack import fft,ifft
from setting import *
import numpy as np
import math
from scipy.signal import savgol_filter

def smooth(y):
    if y.size < 15:
        return y
    return savgol_filter(y, 15, 3)

# def smooth(y, box_pts):
#     box = np.ones(box_pts)/box_pts
#     y_smooth = np.convolve(y, box, mode='same')
#     return y_smooth

# ceil based on 0.5
def half_ceil(raw):
    flt, dcm = math.modf(raw)
    if flt <= 0.5:
        return dcm + 0.5
    else:
        return dcm + 1


def half_floor(raw):
    flt, dcm = math.modf(raw)
    if flt < 0.5:
        return dcm
    else:
        return dcm + 0.5


def sim_fix(raw_str):
    new_str = ''
    continue_num = 1
    last_ele = ''
    for i in range(len(raw_str)):
        assert raw_str[i] == '0' or raw_str[i] == '1'
        if raw_str[i] != last_ele:
            continue_num = 1
            last_ele = raw_str[i]
        elif continue_num == 2:
            continue
        else:
            continue_num += 1
        new_str += raw_str[i]
    return new_str

def Manchester_encode(raw_bit_str): # input: str, output: str
    new_bit_str = ['Unassigned'] * len(raw_bit_str)
    for i in range(len(raw_bit_str)):
        bit = raw_bit_str[i]
        new_bit_str[i] = '01' if bit == '0' else '10'
    return ''.join(new_bit_str)

def Manchester_decode(raw_bit_str): # input: str, output: str
    assert len(raw_bit_str) % 2 == 0
    new_bit_str = ['Unassigned']  * int(len(raw_bit_str) / 2)
    for i in range(len(raw_bit_str)):
        if i % 2 != 0:
            continue
        bit0 = raw_bit_str[i]
        bit1 = raw_bit_str[i + 1]
        if not (bit0 + bit1 != '11' and bit0 + bit1 != '00'):
            return None
        new_bit_str[int(i / 2)] = '0' if bit0 == '0' and bit1 == '1' else '1'
    return ''.join(new_bit_str)

def get_coordinate(x, y):
    return np.concatenate((x.reshape(x.size, 1), \
            y.reshape(y.size, 1)), axis=1)

def divide_coordinate(xy):
    return xy[:, 0], xy[:, 1]

# def get_screen_size():
#     import re
#     output = os.popen('xdpyinfo | grep dimensions').readlines()[0]
#     nums = re.findall("\d+",output)
#     return (int(nums[0]), int(nums[1]))


def bit_str2num(bits_str):
    num = 0
    for i in range(len(bits_str) - 1, -1, -1):
        bit_str = bits_str[i]
        multiplier = 0 if bit_str == '0' else 1
        num += multiplier * pow(2, len(bits_str) - 1 - i)
    return num 


def num2bin(num, bit_num): # return str
    current = ''
    while num != 0:
        current = str(int(num % 2)) + current
        num /= 2
    while len(current) < bit_num:
        current = '0' + current
    return current[-bit_num:]


def crc_cal(num, binary=True, bit_num=10):
    if binary:
        num = bit_str2num(num)
    byte_arr = bytearray(num.to_bytes(2, 'big'))
    crc = Crc4Itu.calc(byte_arr)
    if binary:
        return num2bin(crc, 4)
    else:
        return crc


def crc_validate(num, crc, binary=True, bit_num=10):
    if binary:
        num = bit_str2num(num)
        crc = bit_str2num(crc)
    hex_byte = bytes([crc])
    byte_arr = bytearray(num.to_bytes(2, 'big')) + hex_byte
    new_crc = Crc4Itu.calc(byte_arr)
    if new_crc == 0:
        return True
    return False


def hld(bit_arr, size, bit_one, bit_zero):
    print(bit_arr)
    assert len(bit_arr) == BITS_NUM

    init_location_range = [[0, size[0]], [0, size[1]]]
    width_divided = size[0]
    height_divided = size[1]

    turn = True
    for bit in bit_arr:
        if turn:
            if width_divided <= 1:
                continue
            dis = init_location_range[1][1] - init_location_range[1][0]
            init_location_range[1] = [init_location_range[1][0], init_location_range[1][1]  - dis / 2] if bit == bit_zero \
                    else [init_location_range[1][0] + dis / 2, init_location_range[1][1]]
            width_divided /= 2
        else:
            if height_divided <= 1:
                continue
            dis = init_location_range[0][1] - init_location_range[0][0]
            init_location_range[0] = [init_location_range[0][0], init_location_range[0][1] - dis / 2] if bit == bit_zero \
                    else [init_location_range[0][0] + dis / 2, init_location_range[0][1]]
            height_divided /= 2
        turn = not turn

    return init_location_range

def mid_one_larger_than(x, compare_num):
    mid_one = None
    for i in x:
        if i >= compare_num:
            mid_one = i
            break
    return (mid_one + x[-1])/2

def first_one_larger_than(x, compare_num):
    for i in x:
        if i >= compare_num:
            return i

############################################
################## DSP #####################
############################################
def filter_normalize(complex_arr):
    assert complex_arr.size == 25
    a1 = fft(complex_arr)
    a1[1:4]=0
    a1[22:25]=0
    a2 = ifft(a1).real
    # a2 = a2 - a2.mean()
    # a2 = a2 / 2 + 0.5
    amax = a2.max()
    amin = a2.min()
    a2 = [(i-amin)/(amax-amin) for i in a2]
    return a2

