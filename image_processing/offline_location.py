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

PREFIX = 'fremo_'

def draw_block(im_arr, i, j, block_size, value, rawColor):
    raw = value
    fluc30 = 30 / 255
    for k1 in range(block_size):
        for k2 in range(block_size):
            if i+k1 >= HEIGHT: continue
            if j+k2 >= WIDTH: continue
            for n in range(3):
                temp = rawColor[k1][k2][n] / 255
                tempv = temp + fluc30*(1.0/0.3)*(1 - raw * 2)
                # assert (255 - tempv * 255 >= 0 and 255 - tempv * 255 <= 255)
                if not (255 - tempv * 255 >= 0 and 255 - tempv * 255 <= 255):
                    print(tempv)
                    print(temp*255, raw)
                    print(i, j)
                    print('===')
                im_arr[i + k1][j + k2][n] = tempv * 255
    return im_arr

def draw_process(start, end, data, off, real):
    shiftn = start / real
    if shiftn == 0:
        shift = [0, 0]
    elif shiftn == 1:
        shift = [14, 0]
    elif shiftn == 2:
        shift = [14, 14]
    elif shiftn == 3:
        shift = [0, 14]
    print(shift)
    shiftn += 1
    start = 0
    end = real
    print(start, end)
    im = Image.open('new_test.png')
    im = np.array(im)
    ori_im_arr = im[:1080, :1080, :]
    # im_arr = np.zeros((HEIGHT, WIDTH, 3))
    for n in range(int(start), int(end)):
        im_arr = ori_im_arr.copy()
        for i in range(0, HEIGHT, BLOCK_SIZE):
            for j in range(0, WIDTH, BLOCK_SIZE):
                x = math.floor(i / DATA_BLOCK_SIZE) % DATA_BLOCK_SIZE
                y = math.floor(j / DATA_BLOCK_SIZE) % DATA_BLOCK_SIZE
                # if n < 5:
                #     print(x,y, data[x][y][n])
                filtered_data = data[x][y][(n + off[(x,y)]) % ((BITS_NUM +4) * EXPEND + PREAMBLE_NP.size )]
                rawColor = im_arr[i:i+BLOCK_SIZE,j:j+BLOCK_SIZE,:]
                
                # filtered_data = data[x][y][(n) % (BITS_NUM * EXPEND + PREAMBLE_NP.size)]
                # # print(data[x][y])
                # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data * 255)
                if (i / BLOCK_SIZE) % 2 == 0:
                    if (j / BLOCK_SIZE) % 2 == 0:
                        im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data, rawColor)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data + 128)
                    else:
                        im_arr = draw_block(im_arr,  i, j, BLOCK_SIZE, (1 - filtered_data), rawColor)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255 - filtered_data + 128)
                    
                else:
                    if (j / BLOCK_SIZE) % 2 == 0:
                        im_arr = draw_block(im_arr,  i, j, BLOCK_SIZE, (1 - filtered_data), rawColor)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255 - filtered_data + 128)
                    else:
                        im_arr = draw_block(im_arr,  i, j, BLOCK_SIZE, filtered_data, rawColor)
                        # im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data + 128)
        im = Image.fromarray(im_arr)
        width, height = im.size
        c = ImageChops.offset(im, shift[0], shift[1])
        # c.paste((0,0,0),(0,0,shift[0],height))
        # c.paste((0,0,0),(0,0,width,shift[1]))
        
        c.save('../display/data/' + PREFIX + str(int(n+(shiftn-1)*real)) + '.png')

WIDTH = 1080
HEIGHT = 1080
BLOCK_SIZE = 4
DATA_BLOCK_SIZE = 32

if __name__ == '__main__':
    # raw_data = designed_location_encode(SIZE)
    raw_data = raw_random_location(SIZE)
    # print(raw_data)
    data = np.zeros((DATA_BLOCK_SIZE, DATA_BLOCK_SIZE, (BITS_NUM +4) * EXPEND + PREAMBLE_NP.size ))
    # data = np.zeros((DATA_BLOCK_SIZE, DATA_BLOCK_SIZE, BITS_NUM * EXPEND + PREAMBLE_NP.size))
    print('Using ' + CODING_METHOD + '...')
    # quiet = True
    quiet = False
    off = {}
    if FILTER:
        for i in range(DATA_BLOCK_SIZE):
            for j in range(DATA_BLOCK_SIZE):
                # off[(i,j)] = random.randint(1, BITS_NUM * EXPEND + PREAMBLE_NP.size + 4)
                off[(i,j)] = random.randint(1, (BITS_NUM +4) * EXPEND + PREAMBLE_NP.size)
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