from scipy.interpolate import interp1d
from multiprocessing import Process, Queue
import numpy as np
from collections import deque
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt
import pandas as pd
import os

def handle_data(pos_data):
    from utils import smooth, interpl, chunk_decode
    from numpy import genfromtxt
    correct_pck_num = 0
    diff_num = []
    first_detected = False
    # plt.ion()
    # f = plt.figure()
    # ax = f.add_subplot(311)
    # ax2 = f.add_subplot(312)
    # ax3 = f.add_subplot(313)
    # pos_data = genfromtxt(FILE_NAME, delimiter=',')
    real_time = pos_data[:,1]
    real_val = pos_data[:,0]
    even_time = np.arange(real_time[0], real_time[-1], 1/2400)
    even_time = even_time[even_time < real_time[-1]]
    even_val = interpl(real_time, real_val, even_time, 'nearest')
    even_val_smooth = smooth(even_val, 21)
    even_val_DCremove = smooth(even_val - even_val_smooth, 5)
    # np.savetxt('even_val_DCremove.csv', even_val_DCremove, delimiter=',')

    total_points = len(even_time)
    # maintain slide window within 0.3s
    raw_frames_m = deque(maxlen=int(2400*0.3))
    for i in range(total_points):
        val = even_val_DCremove[i]
        ts = even_time[i]
        raw_frames_m.append([ts, val])
        
        if len(raw_frames_m) != raw_frames_m.maxlen:
            continue

        sample_value_DCremove = np.array(raw_frames_m)[:,1]
        value = np.zeros((10, 1))
        for i in range(10):
            temp_sample = sample_value_DCremove[i:raw_frames_m.maxlen:10]
            value[i] = max(temp_sample) - min(temp_sample)
        std_min = max(value)
        shift_index = np.where(value==std_min)[0][0]
        sample_wave = sample_value_DCremove[shift_index:raw_frames_m.maxlen:10]
        temp_sample = sample_value_DCremove[shift_index:raw_frames_m.maxlen:10]
        
        # bit_stream = sample_wave <= (max(temp_sample) + min(temp_sample)) / 2
        bit_stream = sample_wave <= np.mean(temp_sample)
        bit_stream = bit_stream.astype(int)
        result, diff_count = chunk_decode(bit_stream)
        if result is None:
            result, diff_count = chunk_decode(bit_stream, flip=True)
        if result is not None:
            if not first_detected: first_detected = True
            for _ in range(int(raw_frames_m.maxlen/2)):
                raw_frames_m.popleft()
            # print(result)
            start_ts = np.array(raw_frames_m)[0,0]
            end_ts = np.array(raw_frames_m)[-1,0]
            to_plot = pos_data[np.logical_and(pos_data[:,1] > start_ts, pos_data[:,1] < end_ts)][:,0]
            to_plot_FFT = fft(to_plot[:250])
            l = 30
            to_plot_FFT[1+l:to_plot_FFT.size-l] = 0

            # ax.plot(to_plot[:250])
            # ax2.plot(ifft(to_plot_FFT))
            # ax3.plot(to_plot_FFT[1:])
            # plt.pause(10)
            # plt.show()
            correct_pck_num += 1
            diff_num.append(diff_count[0])
        elif first_detected and diff_count != []:
            diff_num.append(diff_count[0])
    print('correct_pck_num:', correct_pck_num)
    # print('diff_num:', diff_num)
    diff_num = sorted(diff_num)
    diff_num = diff_num[:100]
    # print(diff_num)
    total_error_num = sum(diff_num) + (100 - len(diff_num)) * 62
    # print('error rate:', total_error_num / (100 * 62))
    # input()
    # plt.ioff()


if __name__ == '__main__':
    dirs = os.listdir('D:\\kiki\\Documents\\Nutstore\\shift_test')
    valid_dirs = []
    for i in dirs:
        if i[:4] == 'test':
            valid_dirs.append(i)
    values = []
    for i in valid_dirs:
        tmp = i.split('_')[1:]
        last_one = tmp[-1]
        tmp.remove(last_one)
        tmp.append(last_one.split('.')[0])
        values.append(tmp)
    for i in range(len(valid_dirs)):
        print(valid_dirs[i], end=' ')
        print(values[i])
        raw = pd.read_csv('D:\\kiki\\Documents\\Nutstore\\shift_test\\' + valid_dirs[i])
        raw.columns = pd.Index(['texture_name', 'mouse_id', 'position_id', 'packet_id', 'rgb_data', 'ave_data', 'timestamp'], dtype='object')
        v_arr = np.array(raw['rgb_data'])
        v_arr[v_arr<128] += 128
        # v_arr = np.array(raw['ave_data'])
        v_arr = v_arr.reshape((-1,1))
        ts_arr = np.array(raw['timestamp'])
        ts_arr = ts_arr.reshape((-1,1))
        v_ts = np.concatenate((v_arr, ts_arr), axis=1)
        print('Single: ', end=' ')
        handle_data(v_ts)

        if values[i][-1] == '0':
            v_arr = np.array(raw['ave_data'])
            v_arr = v_arr.reshape((-1,1))
            ts_arr = np.array(raw['timestamp'])
            ts_arr = ts_arr.reshape((-1,1))
            v_ts = np.concatenate((v_arr, ts_arr), axis=1)
            print('Average: ', end=' ')
            handle_data(v_ts)

        print('=================================================')
