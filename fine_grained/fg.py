import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal
from multiprocessing import Queue, Process
from scipy.interpolate import interp1d
import time
import usb.util
import usb.core
from collections import deque

def handle_data():
    raw_frames_m = deque(maxlen=1500)
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

        
        raw_frames_m.append([val_fixed, timestamp])
        if raw_frames_m[-1][1] - raw_frames_m[0][1] < 0.3:
            continue
        a = np.array(raw_frames_m)
        x_sample = np.arange(a[0,1], a[-1,1], 1/1200)
        inter = interp1d(a[:,1], a[:,0], kind='nearest')
        a_intered = inter(x_sample)

        threshold = 200
        points_index = np.where(a_intered>threshold)[0]
        final_window = []
        while len(final_window) < 8:
            threshold -= 10
            points_index = np.where(a_intered>threshold)[0]
            left = points_index[0] - 25
            right = points_index[-1] + 25
            to_draw = a_intered[left:right]
            points_index = np.where(to_draw>threshold)[0]
            groups = []
            window = []
            for i in points_index:
                if window == [] or window[-1] == i - 1:
                    window.append(i)
                else:
                    groups.append(window)
                    window = [i]
            if window != []:
                groups.append(window)
            final_window = []
            for group in groups:
            #     print(group)
            #     print(np.median(group))
                if len(group) > 5:
                    l = len(group)
                    final_window.append(group[0])
                    final_window.append(group[-1])
                else:
                    final_window.append(np.median(group))
        assert len(final_window) == 8
        final_window = [int(i) for i in final_window]
        time_uint = 5
        tmp = final_window[2:-2]
        x = 8 - (tmp[1] - tmp[0] - time_uint) / (time_uint * 2)
        y = 8 - (tmp[3] - tmp[2] - time_uint) / (time_uint * 2)
        print(round(1+8-x),round(y))
        


if __name__ == '__main__':
    dur = input('Duration(default is 10): ')
    dur = 60 if dur == '' else int(dur)

    device = usb.core.find(idVendor=idVendor, idProduct=idProduct)

    if device.is_kernel_driver_active(0):
        device.detach_kernel_driver(0)

    device.set_configuration()
    idVendor = 0x046d
    idProduct = 0xc077
    q = Queue()
    p = Process(target=handle_data) # for display
    p.start()
    start = time.time()
    global_count = 0
    register = 0x0D
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
        global_count += 1

    print('Frame rate: ' + str(global_count / (time.time() - start)))

    p.terminate()