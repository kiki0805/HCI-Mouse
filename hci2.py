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

idVendor = 0x046d
idProduct = 0xc077 # dell
# idProduct = 0xc019 # logitech without tag
# idProduct = 0xc05b # logitech with tag


def handle_data():
    import time
    import re
    from utils import smooth, interpl, chunk_decode
    len_e = 3000
    register = 0x0D
    last_ts = None
    plt.ion()
    ax = plt.gca()
    result_ts = time.time()
    while True:
        response, timestamp = q.get()
        if not response:
            return

        # Fix raw value
        val = int.from_bytes(response, 'big')
        val_fixed = val
        if register == 0x0D:
            if val_fixed < 128:
                val_fixed += 128
            if val_fixed > 240:
                continue

        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))
        
        
        # raw_frames_m.update_line_data()
        # ax.relim() # renew the data limits
        # ax.autoscale_view(True, True, True) # rescale plot view
        # plt.draw() # plot new figure
        # plt.pause(1e-17)

        # continue

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
            # temp_sample = sample_value_DCremove[i:len_e:5]
            temp_sample = sample_value_DCremove[i:len_e:10]
            # temp_sample2 = sample_value_DCremove[i+5:len_e:10*4]
            # temp_sample3 = sample_value_DCremove[i+10:len_e:10*4]
            # temp_sample4 = sample_value_DCremove[i+15:len_e:10*4]
            # print(temp_sample)
            # ts1 = np.hstack((temp_sample, temp_sample3))
            # print(ts1)
            # ts2 = np.hstack((temp_sample2, temp_sample4))
            value[i] = max(temp_sample) + min(temp_sample)
            # value[i] += np.std(ts2[ts2 > (max(ts2) + min(ts2)) / 2])
            # value[i]
        std_min = max(value)
        shift_index = np.where(value==std_min)[0][0]
        sample_wave = sample_value_DCremove[shift_index:len_e:10]
        temp_sample = sample_value_DCremove[shift_index:len_e:10]
        ###################### draw ########################

        # plt.cla()

        # plt.subplot(2, 1, 1)
        # plt.cla()
        # plt.plot(np.arange(len(sample_value_DCremove[shift_index:len_e])), sample_value_DCremove[shift_index:len_e])

        # plt.subplot(2, 1, 2)
        # plt.plot(np.arange(sample_wave.size), sample_value_DCremove[shift_index:len_e:5], marker='x')
        # # plt.scatter(np.arange(sample_wave.size), sample_value_DCremove[shift_index:len_e:5])
        # threshold = np.array([(max(temp_sample) + min(temp_sample)) / 2] * sample_wave.size)
        # # threshold = np.array([(max(sample_value_DCremove) + min(sample_value_DCremove)) / 2] * sample_wave.size)
        # plt.plot(np.arange(sample_wave.size), threshold)
        # # plt.scatter(sample_wave)

        # # for i in range(2, len_e, 10):
        # #     plt.plot(sample_value_DCremove[i:i + 10], '.-')
        
        # raw_frames_m.update_line_data()
        # ax.relim() # renew the data limits
        # ax.autoscale_view(True, True, True) # rescale plot view
        # plt.draw() # plot new figure
        # plt.pause(1)

        ###################### draw ########################

        # thresholding
        
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

def handle_data2():
    import time
    import re
    from utils import smooth, interpl, chunk_decode
    len_e = 3000
    register = 0x0B
    last_ts = None
    plt.ion()
    ax = plt.gca()
    result_ts = time.time()
    while True:
        response, timestamp = q2.get()
        if not response:
            return

        # Fix raw value
        val = int.from_bytes(response, 'big')
        val_fixed = val

        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))

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

#046d:c077
#046d:c05a
    device = usb.core.find(idVendor=idVendor, idProduct=idProduct)

    if device.is_kernel_driver_active(0):
        device.detach_kernel_driver(0)

    device.set_configuration()

    # plt.legend()
    ax = plt.gca() # get most of the figure elements 
    plt.ion()
    q = Queue()
    p = Process(target=handle_data) # for display
    p.start()
    q2 = Queue()
    p2 = Process(target=handle_data2) # for display
    p2.start()


    start = time.time()
    global_count = 0
    register_ = 0x0D
    while time.time() - start < dur:
        device.ctrl_transfer(bmRequestType = 0x40, #Write
                        bRequest = 0x01,
                        wValue = 0x0000,
                        wIndex = register_, #PIX_GRAB register value
                        data_or_wLength = None
                        )

        response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                        bRequest = 0x01,
                        wValue = 0x0000,
                        wIndex = register_, #PIX_GRAB register value
                        data_or_wLength = 1
                        )
        timestamp = time.time()
        q.put((response, timestamp))
        response2 = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                        bRequest = 0x01,
                        wValue = 0x0000,
                        wIndex = 0x0B, #PIX_GRAB register value
                        data_or_wLength = 1
                        )
        timestamp2 = time.time()
        q2.put((response2, timestamp2))
        global_count += 1

    print('Frame rate: ' + str(global_count / (time.time() - start)))
    f.close()

    if FORCED_EXIT:
        p.terminate()

