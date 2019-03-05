from scipy.interpolate import interp1d
from multiprocessing import Process, Queue
import numpy as np
from collections import deque


def handle_data():
    from utils import smooth, interpl, chunk_decode
    from numpy import genfromtxt
    correct_pck_num = 0
    diff_num = []
    first_detected = False
    pos_data = genfromtxt('data233.csv', delimiter=',')
    real_time = pos_data[:,1]
    real_val = pos_data[:,0]
    even_time = np.arange(real_time[0], real_time[-1], 1/2400)
    even_time = even_time[even_time < real_time[-1]]
    even_val = interpl(real_time, real_val, even_time, 'nearest')
    even_val_smooth = smooth(even_val, 41)
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

        if result is not None:
            if not first_detected: first_detected = True
            for _ in range(int(raw_frames_m.maxlen/2)):
                raw_frames_m.popleft()
            # print(result)
            correct_pck_num += 1
            diff_num.append(diff_count[0])
        elif first_detected and len(diff_num) < 100 and diff_count != []:
            diff_num.append(diff_count[0])
    print('correct_pck_num:', correct_pck_num)
    print('diff_num:', diff_num)
    diff_num = diff_num[:100]
    total_error_num = sum(diff_num) + (100 - len(diff_num)) * 62
    print('error rate:', total_error_num / (100 * 62))


if __name__ == '__main__':
    p = Process(target=handle_data)
    p.start()
