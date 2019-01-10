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
from constants import *
from Report import Report
from main_variables import *


def handle_data():
    max_pixel = 200
    min_pixel = 100
    lasttime_interpolated = 0
    cont = 0
    back_desire = 0
    f = open('data_single_813.csv','w')
    start = time.time()
    while time.time() - start < 30:
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
        f.write(str(timestamp) + ',' + str(val_fixed)+'\n')
        continue

        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))

        if lasttime_interpolated == 0:
            frames_m.push(np.array([raw_frames_m.window[0]]))
            lasttime_interpolated = raw_frames_m.window[0][0]
        elif raw_frames_m.window[-1][0] - lasttime_interpolated > END_INTERVAL:
            end_probe = lasttime_interpolated + INTERPOLATION_INTERVAL
            condition = np.logical_and(raw_frames_m.window[:, 0] > lasttime_interpolated, \
                raw_frames_m.window[:, 0] <= end_probe + EXTRA_LEN)
            lasttime_interpolated = end_probe
            raw_frames_m_not_interpolated = raw_frames_m.window[condition]
            
            assert EXTRA_LEN != 0
            frames_m_interpolated = interpolate_f(raw_frames_m_not_interpolated, interval=INTERPOLATION_INTERVAL)

            #l = len(frames_m_interpolated)
            l = int(INTERPOLATION_INTERVAL * FRAMES_PER_SECOND_AFTER_INTERPOLATE)
            # assert frames_m_interpolated[0][0] >= frames_m.window[-1][0]
            # if frames_m_interpolated[0][0] == frames_m.window[-1][0]:
            #     frames_m_interpolated[0][1] = frames_m.window[-1][1]
            #     frames_m.window[-1][1] = frames_m_interpolated[0][1]
            temp_x = np.array([])
            temp_y = np.array([])
            for i in range(l + 1):
                if i >= 2:
                    max_pixel = frames_m.window[-50:, 1].max()
                    min_pixel = frames_m.window[-50:, 1].min()

                if i < l:
                    if frames_m_interpolated[i][0] < frames_m.window[-1][0]:
                        continue
                    temp_x = np.append(temp_x, frames_m_interpolated[i][0])
                    temp_y = np.append(temp_y, frames_m_interpolated[i][1])
                if temp_x.size % POINTS_TO_COMBINE == 0 or i == l:
                    if temp_x.size == 0:
                        continue
                    # assert temp_x.mean() >= frames_m.window[-1][0]
                    frames_m.push(np.array([[temp_x.mean(), temp_y.mean()]]))
                    temp_x = np.array([])
                    temp_y = np.array([])

                    ######################################################
                    x, y = divide_coordinate(frames_m.window)
                    # y_mean.push(np.array([[x[-1], (max_pixel + min_pixel) / 2]]))
                    y_mean.push(np.array([[x[-1], y[-MEAN_WIDTH:].mean()]]))

                    if y_mean.window.shape[0] == 0:
                        one_bit.push(np.array([[x[-1], ONE]]))
                    elif y_mean.window[-1][1] < y[-1]:
                        one_bit.push(np.array([[x[-1], ZERO]]))
                    else:
                        one_bit.push(np.array([[x[-1], ONE]]))
                    ############################################
                    # elif y_mean.window[-1][1] < y[-1]:
                    #     if cont == 0 or cont == 10:
                    #         one_bit.push(np.array([[x[-1], ZERO]]))
                    #         back_desire = 0
                    #     # elif one_bit.window[-1].tolist()[1] == ZERO:
                    #     #     one_bit.push(np.array([[x[-1], ZERO]]))
                    #     elif cont < 4:
                    #         one_bit.push(np.array([[x[-1], ZERO]]))
                    #         one_bit.window[-cont-1:,1] = ZERO
                    #         back_desire = 0
                    #     else:
                    #         last_bit = one_bit.window[-1].tolist()[1]
                    #         one_bit.push(np.array([[x[-1], last_bit]]))
                    #         back_desire += 1
                    # else:
                    #     if cont == 0 or cont == 10:
                    #         one_bit.push(np.array([[x[-1], ONE]]))
                    #         back_desire = 0
                    #     # elif one_bit.window[-1].tolist()[1] == ONE:
                    #     #     one_bit.push(np.array([[x[-1], ONE]]))
                    #     elif cont < 4:
                    #         one_bit.push(np.array([[x[-1], ONE]]))
                    #         one_bit.window[-cont-1:,1] = ONE
                    #         back_desire = 0
                    #     else:
                    #         last_bit = one_bit.window[-1].tolist()[1]
                    #         one_bit.push(np.array([[x[-1], last_bit]]))
                    #         back_desire += 1
                    
                    # if back_desire > 6:
                    #     # print('back')
                    #     if one_bit.window[-1].tolist()[1] == ONE:
                    #         one_bit.window[-cont-1:,1] = ZERO
                    #     else:
                    #         one_bit.window[-cont-1:,1] = ONE

                    # if cont != 0:
                    #     cont = cont + 1 if cont != 10 else 1
                    #     if cont == 1:
                    #         back_desire = 0

                    binary_arr.push(np.array([[x[-1], one_bit.window[-1].tolist()[1]]]))
                    cut = min([one_bit.window.shape[0], binary_arr.window.shape[0], 10])
                    binary_arr.window[-cut:] = one_bit.window[-cut:]
                    # Fix one bit error
                    if one_bit.window.shape[0] > 2:
                        if one_bit.window[-2][1] != one_bit.window[-1][1] and \
                                one_bit.window[-2][1] != one_bit.window[-3][1]:
                                    one_bit.window[-2][1] = one_bit.window[-1][1]
                                    binary_arr.window[-2][1] = binary_arr.window[-1][1]
                    
                    result = bit_arr.update(one_bit, sample_arr)
                    if result == 'first' and cont == 0:
                        print('first sample')
                        cont = 5
                        
                    if result and result != 'first':
                        possible_dataB = result[0]
                        possible_dataD = result[1]
                        if possible_dataB != []:
                            if TESTING_MODE:
                                report.get_test_report(one_bit, possible_dataB, possible_dataD, fixed_bit_arr, fixed_val)
                            
                    ###############################################

                    if GRAPHICS and not raw_frames_m.line:
                        one_bit.update_line_data()
                        binary_arr.update_line_data()
                        y_mean.update_line_data()
                        sample_arr.update_line_data()
                        frames_m.update_line_data()
                        ax.relim() # renew the data limits
                        ax.autoscale_view(True, True, True) # rescale plot view
                        plt.draw() # plot new figure
                        plt.pause(1e-17)


if __name__ == '__main__':
    dur = input('Duration(default is 10): ')
    dur = 10 if dur == '' else int(dur)

    if TESTING_MODE:
        fixed_val = int(input('[ TESTING MODE ] Fixed value: '))
        fixed_bit_arr = num2bin(fixed_val, BITS_NUM)
        report = Report(dur, fixed_val, fixed_bit_arr)
        if DETAILS:
            report.show_detail()

#046d:c077
#046d:c05a
    device = usb.core.find(idVendor=0x046d, idProduct=0xc077)

    if device.is_kernel_driver_active(0):
        device.detach_kernel_driver(0)

    device.set_configuration()


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
                        wIndex = 0x0D, #PIX_GRAB register value
                        data_or_wLength = None
                        )

        response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                        bRequest = 0x01,
                        wValue = 0x0000,
                        wIndex = 0x0D, #PIX_GRAB register value
                        data_or_wLength = 1
                        )
        q.put((response, time.time()))
        global_count += 1

    print('Frame rate: ' + str(global_count / (time.time() - start)))

    if TESTING_MODE:
        report.get_final_report()


    if FORCED_EXIT:
        p.terminate()

