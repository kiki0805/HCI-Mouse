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
if idProduct == 0xc077:
    register = 0x0D # 0x0B
else:
    register = 0x0B

def handle_data():
    import time
    import re
    from utils import smooth, interpl, chunk_decode
    len_e = 1000
    
    last_ts = None
    plt.ion()
    ax = plt.gca()
    while True:
        response, timestamp = q.get()
        if not response:
            return

        # Fix raw value
        val = int.from_bytes(response, 'big')
        val_fixed = val
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

        continue

        if last_ts is None:
            last_ts = raw_frames_m.window[0][0]
        
        if raw_frames_m.window[-1][0] - last_ts < (len_e + 100) / 1200:
            continue

        M = raw_frames_m.window
        M = M[np.logical_and(M[:,0] > last_ts, M[:,0] < last_ts + len_e / 1200)]
        Mtime = M[:,0]
        value = M[:,1]
        last_ts = Mtime[-1]
        sample_time = np.arange(Mtime[0], Mtime[-1], 1/1200)
        sample_value = interpl(Mtime, value, sample_time, 'nearest')
        sample_value_smooth = smooth(sample_value, 21)
        sample_value_DCremove = smooth(sample_value - sample_value_smooth, 5)

        value = np.zeros((5, 1))
        for i in range(5):
            temp_sample = sample_value_DCremove[i:len_e:5]
            value[i] = np.std(temp_sample[temp_sample > (max(temp_sample) + min(temp_sample)) / 2])
        std_min = min(value)
        shift_index = np.where(value==std_min)[0][0]
        sample_wave = sample_value_DCremove[shift_index:len_e:5]

        ###################### draw ########################

        # plt.cla()

        # plt.subplot(2, 1, 1)
        # plt.cla()
        # plt.plot(np.arange(len(sample_value_DCremove[shift_index:len_e])), sample_value_DCremove[shift_index:len_e])

        # plt.subplot(2, 1, 2)
        # plt.scatter(np.arange(sample_wave.size), sample_value_DCremove[shift_index:len_e:5])
        # threshold = np.array([(max(temp_sample) + min(temp_sample)) / 2] * sample_wave.size)
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
        bit_stream = sample_wave <= (max(temp_sample) + min(temp_sample)) / 2
        bit_stream = bit_stream.astype(int)
        result = chunk_decode(bit_stream)
        if result is None:
            result = chunk_decode(bit_stream, flip=True)

        if result is not None:
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
    f = open('without_plot.csv', 'w')

    # plt.legend()
    ax = plt.gca() # get most of the figure elements 
    plt.ion()
    q = Queue()
    p = Process(target=handle_data) # for display
    p.start()


    start = time.time()
    global_count = 0

    while time.time() - start < dur:
        device.ctrl_transfer(bmRequestType = 0x40, #Write
                        bRequest = 0x01,
                        wValue = 0x0000,
                        wIndex = register, #PIX_GRAB register value
                        data_or_wLength = None
                        )

        response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                        bRequest = 0x01,
                        wValue = 0x0000,
                        wIndex = register, #PIX_GRAB register value
                        data_or_wLength = 1
                        )
        timestamp = time.time()
        q.put((response, timestamp))
        f.write(str(timestamp) + '\n')
        global_count += 1

    print('Frame rate: ' + str(global_count / (time.time() - start)))
    f.close()

    if FORCED_EXIT:
        p.terminate()

