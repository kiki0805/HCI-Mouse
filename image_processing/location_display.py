from PIL import Image, ImageChops
import numpy as np
import random
import sys
import matplotlib.pyplot as plt
from scipy.fftpack import fft,ifft
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue
import threading
sys.path.append("..")
from setting import *
from utils import *

PREFIX = 'frem36_6_3_9_'

def draw_block(im_arr, i, j, block_size, value):
    for k1 in range(block_size):
        for k2 in range(block_size):
            if i+k1 >= HEIGHT: continue
            if j+k2 >= WIDTH: continue
            for n in range(3):
                im_arr[i + k1][j + k2][n] = value
    return im_arr

def draw_process(start, end, data, off, real):
    shiftn = start / real
    shift_pixels = 14#15 # 14
    if shiftn == 0:
        shift = [0, 0]
    elif shiftn == 1:
        shift = [shift_pixels, 0]
    elif shiftn == 2:
        shift = [shift_pixels, shift_pixels]
    elif shiftn == 3:
        shift = [0, shift_pixels]
    print(shift)
    shiftn += 1
    start = 0
    end = real
    print(start, end)
    im_arr = np.zeros((HEIGHT, WIDTH, 3))
    for n in range(int(start), int(end)):
        for i in range(0, HEIGHT, BLOCK_SIZE):
            for j in range(0, WIDTH, BLOCK_SIZE):
                x = math.floor(i / DATA_BLOCK_SIZE) % DATA_BLOCK_SIZE
                y = math.floor(j / DATA_BLOCK_SIZE) % DATA_BLOCK_SIZE
                # if n < 5:
                #     print(x,y, data[x][y][n])
                filtered_data = data[x][y][(n + off[(x,y)]) % ((BITS_NUM +4) * EXPEND + PREAMBLE_NP.size )]
                # if (i >= 1080 or j >= 1080) and n < 6:
                #     filtered_data = 0.5
                # filtered_data = data[x][y][(n) % (BITS_NUM * EXPEND + PREAMBLE_NP.size)]
                # # print(data[x][y])
                # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data * 255)
                if (i / BLOCK_SIZE) % 2 == 0:
                    if (j / BLOCK_SIZE) % 2 == 0:
                        im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data * 255)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data + 128)
                    else:
                        im_arr = draw_block(im_arr,  i, j, BLOCK_SIZE, (1 - filtered_data) * 255)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255 - filtered_data + 128)
                    
                else:
                    if (j / BLOCK_SIZE) % 2 == 0:
                        im_arr = draw_block(im_arr,  i, j, BLOCK_SIZE, (1 - filtered_data) * 255)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255 - filtered_data + 128)
                    else:
                        im_arr = draw_block(im_arr,  i, j, BLOCK_SIZE, filtered_data * 255)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data + 128)
        im = Image.fromarray(np.uint8(im_arr))
        width, height = im.size
        c = ImageChops.offset(im, shift[0], shift[1])
        # c = c.resize((1920, 1080), Image.ANTIALIAS)
        # c.paste((0,0,0),(0,0,shift[0],height))
        # c.paste((0,0,0),(0,0,width,shift[1]))
        
        c.save('../display/data/' + PREFIX + str(int(n+(shiftn-1)*real)) + '.png')

WIDTH = 1080
HEIGHT = 1080
BLOCK_SIZE = 4#6
DATA_BLOCK_SIZE = 32#36

if __name__ == '__main__':
    # raw_data = designed_location_encode(SIZE)
    raw_data = raw_random_location(SIZE)
    # print(raw_data)
    data = np.zeros((DATA_BLOCK_SIZE,  DATA_BLOCK_SIZE, (BITS_NUM +4) * EXPEND + PREAMBLE_NP.size ))

    # data = np.zeros((int(WIDTH / DATA_BLOCK_SIZE), int(HEIGHT / DATA_BLOCK_SIZE), (BITS_NUM +4) * EXPEND + PREAMBLE_NP.size ))
    # data = np.zeros((DATA_BLOCK_SIZE, DATA_BLOCK_SIZE, BITS_NUM * EXPEND + PREAMBLE_NP.size))
    print('Using ' + CODING_METHOD + '...')
    # quiet = True
    quiet = False
    off = {}
    if FILTER:
        for i in range(DATA_BLOCK_SIZE):
            for j in range(DATA_BLOCK_SIZE):
        # for i in range(int(WIDTH / DATA_BLOCK_SIZE)):
        #     for j in range(int(HEIGHT / DATA_BLOCK_SIZE)):
                # off[(i,j)] = random.randint(1, BITS_NUM * EXPEND + PREAMBLE_NP.size + 4)
                off[(i,j)] = random.randint(1, (BITS_NUM + 4) * EXPEND + PREAMBLE_NP.size)
                if not quiet:
                    data[i][j] = np.array(filter_normalize(raw_data[i][j].tolist()))
                    quiet = input('quiet? ')
                    quiet = False if quiet == '' else True
                else:
                    data[i][j] = np.array(filter_normalize(raw_data[i][j].tolist(), quiet=True))
    else:
        for i in range(DATA_BLOCK_SIZE):
            for j in range(DATA_BLOCK_SIZE):
                off[(i,j)] = random.randint(1, (BITS_NUM +4) * EXPEND + PREAMBLE_NP.size)
                # data[i][j] = raw_data[i][j]
                if not quiet:
                    data[i][j] = np.array(filter_normalize(raw_data[i][j].tolist(), nothing=True))
                    quiet = input('quiet? ')
                    quiet = False if quiet == '' else True
                else:
                    data[i][j] = np.array(filter_normalize(raw_data[i][j].tolist(), nothing=True, quiet=True))

    process_num = 4
    pl = []
    for n in range(process_num):
        total_bits_num = ((BITS_NUM +4) * EXPEND + PREAMBLE_NP.size) * 4
        real_bits_num = (BITS_NUM +4) * EXPEND + PREAMBLE_NP.size
        # total_bits_num = BITS_NUM * EXPEND + PREAMBLE_NP.size
        end_index = (n + 1) * math.floor(total_bits_num / process_num)
        if n == process_num - 1:
            end_index = total_bits_num
        print((n * math.floor(total_bits_num / process_num), \
            end_index))
        p = Process(target=draw_process, \
            args=(n * math.floor(total_bits_num / process_num), \
            end_index, \
            data, off, real_bits_num))
        p.start()
        pl.append(p)
    for p in pl:
        p.join()
    plt.show()