import os
from setting import *
import numpy as np

def get_coordinate(x, y):
    return np.concatenate((x.reshape(x.size, 1), \
            y.reshape(y.size, 1)), axis=1)

def divide_coordinate(xy):
    return xy[:, 0], xy[:, 1]

def get_screen_size():
    output = os.popen('xdpyinfo | grep dimensions').readlines()[0]
    nums = re.findall("\d+",output)
    return (int(nums[0]), int(nums[1]))


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

def hld(bit_arr, size, bit_one, bit_zero):
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

