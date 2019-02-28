from PIL import Image
import numpy as np
import random
import sys
import matplotlib.pyplot as plt
from scipy.fftpack import fft,ifft
from multiprocessing import Process, Queue
sys.path.append("..")
from setting import *
from utils import *

PREFIX = 'freq_'
WIDTH = 1080
HEIGHT = 1080


off = {}
BLOCK_SIZE = 4

def draw_block(im_arr, i, j, block_size, value):
    for k1 in range(block_size):
        for k2 in range(block_size):
            for n in range(3):
                im_arr[i + k1][j + k2][n] = value
    return im_arr

def draw_process(start, end, filtered_data, filtered_data2):
    im_arr = np.zeros((HEIGHT, WIDTH, 3))
    for n in range(int(start), int(end)):
        for i in range(0, HEIGHT, BLOCK_SIZE):
            for j in range(0, WIDTH, BLOCK_SIZE):
                # if i < int(HEIGHT / 2):
                #     im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n] * 255)
                #     # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n]+128)
                # else:
                #     im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data2[n] * 255)
                    # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data2[n]+128)
                if (i / BLOCK_SIZE) % 2 == 0:
                    if (j / BLOCK_SIZE) % 2 == 0:
                        im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n] * 255)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n]+128)
                    else:
                       im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, (1 - filtered_data[n]) * 255)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255 - filtered_data[n] + 128)
                    
                else:
                    if (j / BLOCK_SIZE) % 2 == 0:
                        im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, (1 - filtered_data[n]) * 255)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255 - filtered_data[n] + 128)
                    else:
                        im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n] * 255)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n]+128)
        im = Image.fromarray(np.uint8(im_arr))
        im.save('../display/data/' + PREFIX + str(n) + '.png')

if __name__ == '__main__':
    val = input("Fixed value(682): ")
    direct_data = -1
    if val == '':
        raw_data = input('Binary format: ')
        if raw_data == '':
            direct_data = input('Direct data: ')
    else:
        raw_data = num2bin(int(val), BITS_NUM)

    data = raw_data

    # NRZI = input('If use NRZI? ')
    NRZI = ''
    NRZI = False if NRZI == '' else True
    if fiveBsixB:
        from fiveBsixB_coding import *
        print('Using 10B/12B...')
        # data = PREAMBLE_STR + CODING_DIC[raw_data]
        if NRZI:
            # print(add_NRZI(raw_data, fixed_len=True))
            print(CODING_DIC[raw_data])
            data = add_NRZI(CODING_DIC[raw_data])
        else:
            data = CODING_DIC[raw_data[-BITS_NUM:]]
    elif MANCHESTER_MODE:
        print('Using Manchester...')
        # data = PREAMBLE_STR + Manchester_encode(raw_data)
        if NRZI:
            print(add_NRZI(raw_data))
            data = Manchester_encode(add_NRZI(raw_data))
        else:
            data = PREAMBLE_STR + Manchester_encode(raw_data)
    elif FREQ:
        print('Using FREQ...')
        data = list(freq_encode(raw_data))
    elif DESIGNED_CODE:
        print('Using DESIGNED CODE...')
        # data = designed_code(Manchester_encode(raw_data))
        data = designed_code(raw_data)
    elif INFRAMEPP:
        print('Using INFRAME++...')
        data = inframe_encode(raw_data)
    data = [str(i) for i in data]
    # data = data + list(crc_cal(raw_data))
    # if DESIGNED_CODE:
    #     tmp = []
    #     for i in data:
    #         if i == '0':
    #             tmp.append(-1)
    #         elif i == '-1':
    #             tmp.append(-1)
    #         else:
    #             tmp.append(1)
    #     data = tmp
    # crc
    # data = data + list(crc_cal(raw_data))

    import matplotlib.pyplot as plt
    # plt.plot(list(range(len(data))), data)
    # plt.show()

    if direct_data != -1:
        raw_data = direct_data
        data = direct_data

    print('Raw data(' +  str(len(raw_data)) + '): ' + raw_data)
    print('Decoded data(' +  str(len(data)) + '): ' + str(data))


    data = [float(i) for i in data]
    quiet = False
    if FILTER:
        if quiet:
            filtered_data = filter_normalize(np.array(list(data)), quiet=True)
        else:
            filtered_data = filter_normalize(np.array(list(data)))
            quiet = input('quiet? ')
            quiet = False if quiet == '' else True
    else:
        if quiet:
            filtered_data = filter_normalize(np.array(list(data)), quiet=True, nothing=True)
        else:
            filtered_data = filter_normalize(np.array(list(data)), nothing=True)
            quiet = input('quiet? ')
            quiet = False if quiet == '' else True
        # filtered_data = data
        # filtered_data = [int(i) for i in filtered_data]
    #print('Filtered data(' + str(len(filtered_data)) + '): \n\t', end='')
    print(filtered_data)
    # filtered_data = filtered_data[:4] + [i * 0.99 for i in filtered_data[4:]]
    # print(filtered_data)
    filtered_data2 = filtered_data[:]
    # filtered_data = [1, 0, 1, 0, 1, 0, 1, 0]
    # filtered_data2 = [0.99,0.99,0,0,0.99,0.99,0,0]
    # filtered_data2 = [i * 0.92 for i in filtered_data2]

    # filtered_data = [(0.7 + (1.3 - 0.7) * (i -0)/(1)) / 2 for i in filtered_data]
    # filtered_data2 = [(0.7 + (1.3 - 0.7) * (i -0)/(1)) / 2 for i in filtered_data2]
    # print(filtered_data)
    # print(filtered_data2)
    plt.plot(list(range(len(data))), data)
    plt.plot(list(range(len(filtered_data))), filtered_data)
    # plt.plot(list(range(len(filtered_data))), abs(fft(filtered_data)))
    plt.show()
    process_num = 4

    for n in range(process_num):
        total_bits_num = len(data)
        end_index = (n + 1) * math.floor(total_bits_num / process_num)
        if n == process_num - 1:
            end_index = total_bits_num
        print((n * math.floor(total_bits_num / process_num), \
            end_index))
        p = Process(target=draw_process, \
            args=(n * math.floor(total_bits_num / process_num), \
            end_index, \
            filtered_data, filtered_data2))
        p.start()
