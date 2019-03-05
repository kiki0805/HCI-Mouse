import sys
from interpolate_f import interpolate_f
import threading
from scipy.interpolate import interp1d
from multiprocessing import Process, Queue
from matplotlib import animation
import time
import math
import numpy as np
from main_variables import *


def handle_data():
    import time
    import re
    from utils import smooth, interpl, chunk_decode
    from numpy import genfromtxt
    len_e = 3000
    last_ts = None
    pos_data = genfromtxt('data233.csv', delimiter=',')
    real_time = pos_data[:,1]
    real_val = pos_data[:,0]
    even_time = np.arange(real_time[0], real_val[-1], 1/2400)
    even_time = even_time[even_time < real_time[-1]]
    even_val = interpl(real_time, real_val, even_time, 'nearest')
    even_val_smooth = smooth(even_val, 41)
    even_val_DCremove = smooth(even_val - even_val_smooth, 5)
    np.savetxt('even_val_DCremove.csv', even_val_DCremove, delimiter=',')

    # for response, timestamp in pos_data:
    #     val_fixed = response
    #     raw_frames_m.push(np.array([[timestamp, val_fixed], ]))

    #     if last_ts is None:
    #         last_ts = raw_frames_m.window[0][0]
        
    #     if raw_frames_m.window[-1][0] - last_ts < 0.6:
    #         continue

    #     M = raw_frames_m.window
    #     M = M[np.logical_and(M[:,0] > last_ts - 0.5, M[:,0] < last_ts + 0.5)]
    #     Mtime = M[:,0]
    #     value = M[:,1]
    #     last_ts = Mtime[-1]
    #     sample_time = np.arange(Mtime[0], Mtime[-1], 1/2400)
    #     sample_time = sample_time[sample_time<Mtime[-1]]
    #     sample_value = interpl(Mtime, value, sample_time, 'nearest')
    #     sample_value_smooth = smooth(sample_value, 41)
    #     sample_value_DCremove = smooth(sample_value - sample_value_smooth, 5)

    #     value = np.zeros((10, 1))
    #     for i in range(10):
    #         temp_sample = sample_value_DCremove[i:len_e:10]
    #         value[i] = max(temp_sample) - min(temp_sample)
    #     std_min = max(value)
    #     shift_index = np.where(value==std_min)[0][0]
    #     sample_wave = sample_value_DCremove[shift_index:len_e:10]
    #     temp_sample = sample_value_DCremove[shift_index:len_e:10]
        
    #     # bit_stream = sample_wave <= (max(temp_sample) + min(temp_sample)) / 2
    #     bit_stream = sample_wave <= np.mean(temp_sample)
    #     bit_stream = bit_stream.astype(int)
    #     result, crc_fail = chunk_decode(bit_stream)

    #     if result is not None:
    #         for i in result:
    #             print(i)


if __name__ == '__main__':
    p = Process(target=handle_data)
    p.start()
