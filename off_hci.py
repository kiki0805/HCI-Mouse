import usb.core
import sys
from interpolate_f import interpolate_f
import threading
from scipy.interpolate import interp1d
from multiprocessing import Process, Queue
from matplotlib import animation
import time
import math
import numpy as np
import usb.util
from main_variables import *



def handle_data2():
    import time
    import re
    from utils import smooth, interpl, chunk_decode
    from numpy import genfromtxt
    len_e = 3000
    register = 0x0B
    last_ts = None
    plt.ion()
    ax = plt.gca()
    result_ts = time.time()
    pos_data2 = genfromtxt('pos_data2.csv', delimiter=',')
    for  timestamp, response in pos_data2:
        if not response:
            return

        # Fix raw value
        val = response
        val_fixed = val

        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))
        # print(raw_frames_m.window)

        if last_ts is None:
            last_ts = raw_frames_m.window[0][0]
        
        if raw_frames_m.window[-1][0] - last_ts < 0.6:
            continue

        M = raw_frames_m.window
        M = M[np.logical_and(M[:,0] > last_ts - 0.5, M[:,0] < last_ts + 0.5)]
        Mtime = M[:,0]
        value = M[:,1]
        last_ts = Mtime[-1]
        sample_time = np.arange(Mtime[0], Mtime[-1], 1/2400)
        sample_time = sample_time[sample_time<Mtime[-1]]
        sample_value = interpl(Mtime, value, sample_time, 'nearest')
        sample_value_smooth = smooth(sample_value, 41)
        sample_value_DCremove = smooth(sample_value - sample_value_smooth, 5)

        value = np.zeros((10, 1))
        for i in range(10):
            temp_sample = sample_value_DCremove[i:len_e:10]
            value[i] = max(temp_sample) + min(temp_sample)
        std_min = max(value)
        shift_index = np.where(value==std_min)[0][0]
        sample_wave = sample_value_DCremove[shift_index:len_e:10]
        temp_sample = sample_value_DCremove[shift_index:len_e:10]
        
        # bit_stream = sample_wave <= (max(temp_sample) + min(temp_sample)) / 2
        bit_stream = sample_wave <= np.mean(temp_sample)
        bit_stream = bit_stream.astype(int)
        result = chunk_decode(bit_stream)
        if result is None:
            result = chunk_decode(bit_stream, flip=True)

        if result is not None:
            result_ts = time.time()
            for i in result:
                print(i)


if __name__ == '__main__':
    dur = input('Duration(default is 10): ')
    dur = 10 if dur == '' else int(dur)

    # plt.legend()
    ax = plt.gca() # get most of the figure elements 
    plt.ion()
    q = Queue()
    p = Process(target=handle_data) # for display
    p.start()
    q2 = Queue()
    p2 = Process(target=handle_data2) # for display
    p2.start()
    from numpy import genfromtxt

    start = time.time()
    global_count = 0
    register_ = 0x0D
    pos_data = genfromtxt('pos_lin.csv', delimiter=',')
    pos_data2 = genfromtxt('pos2_lin.csv', delimiter=',')
    # while time.time() - start < dur:
    for timestamp, response in pos_data:
        # print((response, timestamp))
        q.put((response, timestamp))
        # timestamp2 = time.time()
        # time.sleep(0.01)
    for timestamp2, response2 in pos_data2:
        # print((response2, timestamp2))
        q2.put((response2, timestamp2))
        # global_count += 1
        # time.sleep(0.01)
    time.sleep(10)
    print('Frame rate: ' + str(global_count / (time.time() - start)))
    # f.close()

    if FORCED_EXIT:
        p.terminate()

