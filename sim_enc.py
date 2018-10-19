import os
import numpy as np
from PIL import Image
import re
import math
from utils import *
from setting import *

### Configuration

rate = FRAME_RATE 
val_mode = input('fixed value? ')
fixed_val = int(val_mode) if val_mode != '' else 0
if val_mode != '':
    print('Binary format of ' + val_mode + ': ' + num2bin(fixed_val, BITS_NUM))

test_mode = input('black & white? ')
test_mode = True if test_mode != '' else False
if test_mode:
    val_mode = '01'
    fixed_val = 10



preamble = PREAMBLE_STR
#size = get_screen_size()
size = SIZE
mode = 'RGB'
bits_num = BITS_NUM + len(preamble) # per second

zero = (255, 255, 255) if mode == 'RGB' else 255
one = (0, 0, 0) if mode == 'RGB' else 0

im0 = Image.new(mode, size)

## Naive One
def get_pixel_locaiton(size):
    pixel_block_size = max(1, math.ceil(math.sqrt(size[0] * size[1] / pow(2, BITS_NUM))))

    blocks_x = math.ceil(size[0] / pixel_block_size)
    blocks_y = math.ceil(size[1] / pixel_block_size)

    imgs_arr = np.zeros((bits_num, size[0], size[1], 3), dtype=np.int16)
    [im_id, row, col, _] = imgs_arr.shape
    str_enc_dic = {}
    for i in range(row):
        for j in range(col):
            x = math.ceil(i / pixel_block_size)
            y = math.ceil(j / pixel_block_size)
            if (x, y) in str_enc_dic:
                str2enc = str_enc_dic[(x, y)]
            else:
                num = (x - 1) * blocks_x + y
                if val_mode == '':
                    str2enc = preamble + num2bin(num, BITS_NUM)
                elif val_mode == '01':
                    str2enc = preamble + '1010101010'
                else:
                    str2enc = preamble + num2bin(fixed_val, BITS_NUM)
                str_enc_dic[(x, y)] = str2enc
            for n in range(im_id):
                imgs_arr[n, i, j] = np.array(zero) if str2enc[n] == '0' else np.array(one)
    return imgs_arr

## Hierachical Location Encoding
## HLE

def hle(size):
    assert math.log(size[0], 2) % 1 == 0
    assert math.log(size[1], 2) % 1 == 0

    width_divided = size[0]
    height_divided = size[1]

    imgs_arr = np.zeros((bits_num, size[0], size[1], 3), dtype=np.int16)
    [im_id, row, col, _] = imgs_arr.shape

    turn = True
    for n in range(im_id):
        if n < len(preamble):
            imgs_arr[n, :, :] = zero if preamble[n] == '0' else one
            continue
        mod = width_divided / 2 if turn else height_divided / 2
        if turn:
            width_divided /= 2
        else:
            height_divided /= 2

        if turn:
            for j in range(col):
                imgs_arr[n, :, j] = zero if math.floor(j / mod) % 2 == 0 else one
        else:
            for i in range(row):
                imgs_arr[n, i, :] = zero if math.floor(i / mod) % 2 == 0 else one
                
        turn = not turn
    return imgs_arr


def hld(bit_arr, size, bit_one, bit_zero):
    assert len(bit_arr) == BITS_NUM

    init_location_range = [[0, size[0]], [0, size[1]]]

    turn = True
    for bit in range(bit_arr):
        if turn:
            init_location_range[1] = [init_location_range[1][0], init_location_range[1][1] / 2] if bit == bit_zero \
                    else [init_location_range[1][1] / 2, init_location_range[1][1]]
        else:
            init_location_range[0] = [init_location_range[0][0], init_location_range[0][1] / 2] if bit == bit_zero \
                    else [init_location_range[0][1] / 2, init_location_range[0][1]]
        turn = not turn

    print(init_location_range)




def hle_Manchester(size):
    assert math.log(size[0], 2) % 1 == 0
    assert math.log(size[1], 2) % 1 == 0

    width_divided = size[0]
    height_divided = size[1]

    imgs_arr = np.zeros((len(preamble) + BITS_NUM * 2, size[0], size[1], 3), dtype=np.int16)
    [im_id, row, col, _] = imgs_arr.shape

    turn = True
    for n in range(im_id):
        if n < len(preamble):
            imgs_arr[n, :, :] = zero if preamble[n] == '0' else one
            continue
        
        if (n - preamble) % 2 != 0:
            continue

        mod = width_divided / 2 if turn else height_divided / 2
        if turn:
            width_divided /= 2
        else:
            height_divided /= 2

        if turn:
            for j in range(col):
                imgs_arr[n, :, j] = zero if math.floor(j / mod) % 2 == 0 else one
                imgs_arr[n + 1, :, j] = one if math.floor(j / mod) % 2 == 0 else zero
        else:
            for i in range(row):
                imgs_arr[n, i, :] = zero if math.floor(i / mod) % 2 == 0 else one
                imgs_arr[n + 1, i, :] = one if math.floor(i / mod) % 2 == 0 else zero
                
        turn = not turn
    return imgs_arr


def naive_Manchester(size):
    pixel_block_size = max(1, math.ceil(math.sqrt(size[0] * size[1] / pow(2, BITS_NUM))))

    blocks_x = math.ceil(size[0] / pixel_block_size)
    blocks_y = math.ceil(size[1] / pixel_block_size)

    imgs_arr = np.zeros((len(preamble) + BITS_NUM * 2, size[0], size[1], 3), dtype=np.int16)
    [im_id, row, col, _] = imgs_arr.shape
    str_enc_dic = {}
    for i in range(row):
        for j in range(col):
            x = math.ceil(i / pixel_block_size)
            y = math.ceil(j / pixel_block_size)
            if (x, y) in str_enc_dic:
                str2enc = str_enc_dic[(x, y)]
            else:
                num = (x - 1) * blocks_x + y
                if val_mode == '':
                    str2enc = preamble + num2bin(num, BITS_NUM)
                elif val_mode == '01':
                    str2enc = preamble + Manchester_encode('1010101010')
                else:
                    str2enc = preamble + Manchester_encode(num2bin(fixed_val, BITS_NUM))
                str_enc_dic[(x, y)] = str2enc
            for n in range(im_id):
                imgs_arr[n, i, j] = np.array(zero) if str2enc[n] == '0' else np.array(one)
    return imgs_arr

#imgs_arr = get_pixel_locaiton(size)
assert math.log(ZOOM, 2) % 1 == 0
if val_mode == '':
    if MANCHESTER_MODE:
        imgs_arr = hle_Manchester(size)
    else:
        imgs_arr = hle(size)
else:
    if MANCHESTER_MODE:
        imgs_arr = naive_Manchester(size) 
    else:
        imgs_arr = get_pixel_locaiton(size)

if test_mode:
    imgs_arr = imgs_arr[len(PREAMBLE_STR):]
[im_id, row, col, _] = imgs_arr.shape

def draw_pixel(img, value, i, j):
    for a in range(i * ZOOM, (i + 1)* ZOOM):
        for b in range(j * ZOOM, (j + 1) * ZOOM):
           img.putpixel((a, b), int.from_bytes(value,'big'))

dirs = os.listdir()
for d in dirs:
    if d[:min(10, len(d))] == 'location__':
        os.remove(d)
    if d == 'test.mp4':
        os.remove(d)

for n in range(im_id):
    im = Image.new('RGB', (row * ZOOM, col * ZOOM))
    for i in range(row):
        for j in range(col):
            draw_pixel(im, tuple(imgs_arr[n][i][j].tolist()), i, j)
            #im.putpixel((i, j), tuple(imgs_arr[n][i][j].tolist()))
    #im.save('./encoded_imgs/im_encoded' + str(n) + '.png')
    num = str(n+1)
    im.save('location__' + num.zfill(2) + '.png')

if val_mode != '':
    out_name = 'one_value_'+ val_mode + '_' + str(rate) + '_' + str(SIZE[0]) + 'x' + str(SIZE[1]) +  '_' +  str(ZOOM) + 'x.mp4' 
else:
    out_name = 'location_' + str(rate)+ '_' + str(SIZE[0]) + 'x' + str(SIZE[1]) +  '_' +  str(ZOOM) +  '.mp4'

if MANCHESTER_MODE:
    out_name = 'Manchester_' + out_name
os.system('ffmpeg -r ' + str(rate) + ' -f image2  -i location__%02d.png -vcodec libx264 -crf 10 -pix_fmt yuv420p test.mp4')
os.system('ffmpeg -f concat -i new.txt -c copy ' + out_name)
    
# ffmpeg -r 50 -stream_loop 100 -i location__%02d.png -c:v huffyuv test.avi

