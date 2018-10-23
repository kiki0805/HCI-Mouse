import os
import numpy as np
from PIL import Image
import re
import math
from utils import *
from setting import *
from fiveBsixB_coding import *

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

# per bit, per x, y
def hle(size):
    assert math.log(size[0], 2) % 1 == 0
    assert math.log(size[1], 2) % 1 == 0

    width_divided = size[0]
    height_divided = size[1]

    imgs_arr = np.zeros((bits_num, size[0], size[1]), dtype=np.int16)
    [im_id, row, col] = imgs_arr.shape

    turn = True
    for n in range(im_id):
        if n < len(preamble):
            imgs_arr[n, :, :] = preamble[n] == '0'
            continue
        mod = width_divided / 2 if turn else height_divided / 2
        if turn:
            width_divided /= 2
        else:
            height_divided /= 2

        if turn:
            for j in range(col):
                imgs_arr[n, :, j] = '0' if math.floor(j / mod) % 2 == 0 else '1'
        else:
            for i in range(row):
                imgs_arr[n, i, :] = '0' if math.floor(i / mod) % 2 == 0 else '1'
                
        turn = not turn
    return imgs_arr


# per x, y, per bit
# without preamble
def hle_raw(size):
    imgs_arr = np.zeros((size[0], size[1], BITS_NUM), dtype=np.int16)
    raw_imgs_arr = hle(size)
    for i in range(size[0]):
        for j in range(size[1]):
            imgs_arr[i,j,:] = raw_imgs_arr[:,i,j][-BITS_NUM:]
    return imgs_arr
            

# with preamble
# per x,y, per bit
def fiveBsixB_encode(size, val_mode=False):
    assert BITS_NUM == 10
    raw_arr = hle_raw(size)
    imgs_arr = np.zeros((size[0], size[1], len(PREAMBLE_STR) + 12), dtype=np.int16)
    for i in range(size[0]):
        for j in range(size[1]):
            if not val_mode:
                temp_list = raw_arr[:,i,j][-BITS_NUM:].tolist()
            else:
                temp_list = list(num2bin(fixed_val, BITS_NUM))
            encoded_str = CODING_DIC[''.join(temp_list)]
            encoded_list = PREAMBLE_LIST + list(encoded_str)
            imgs_arr[i,j,:] = np.array(encoded_list)
    return imgs_arr


# crc4, without preamble
# per x,y, per bit
def crc_encode(size, val_mode=False):
    raw_arr = hle_raw(size)
    imgs_arr = np.zeros((size[0], size[1], 4 + BITS_NUM), dtype=np.int16)
    for i in range(size[0]):
        for j in range(size[1]):
            if not val_mode:
                raw_bit_str = ''.join(raw_arr[:,i,j][-BITS_NUM:].tolist())
            else:
                raw_bit_str = num2bin(fixed_val, BITS_NUM)
            crc_val_list = list(crc_cal(raw_bit_str))
            imgs_arr[i,j,:] = np.array(list(raw_bit_str) + crc_val_list)
    return imgs_arr


# per x,y per bit -> per bit per x,y
def change_order(origin):
    [row, col, im_id] = origin.shape
    new_arr = np.zeros((im_id, row, col), dtype=np.int16)
    for i in range(row):
        for j in range(col):
            new_arr[:,i,j] = origin[i,j,:]
    return new_arr

        
def replace_str_by_pixel(arr):
    [im_id, row, col] = arr.shape
    new_arr = np.zeros((im_id, row, col, 3), dtype=np.int16)
    for n in range(im_id):
        for i in range(row):
            for j in range(col):
                new_arr[n, i, j] = zero if arr[n,i,j] == '0' or arr[n,i,j] == 0 else one
    return new_arr


# def hld(bit_arr, size, bit_one, bit_zero):
#     assert len(bit_arr) == BITS_NUM

#     init_location_range = [[0, size[0]], [0, size[1]]]

#     turn = True
#     for bit in range(bit_arr):
#         if turn:
#             init_location_range[1] = [init_location_range[1][0], init_location_range[1][1] / 2] if bit == bit_zero \
#                     else [init_location_range[1][1] / 2, init_location_range[1][1]]
#         else:
#             init_location_range[0] = [init_location_range[0][0], init_location_range[0][1] / 2] if bit == bit_zero \
#                     else [init_location_range[0][1] / 2, init_location_range[0][1]]
#         turn = not turn

#     print(init_location_range)


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
        
        if (n - len(preamble)) % 2 != 0:
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
    elif CRC4:
        imgs_arr = replace_str_by_pixel(change_order(crc_encode(size)))
    elif fiveBsixB:
        imgs_arr = replace_str_by_pixel(change_order(fiveBsixB_encode(size)))
    else:
        imgs_arr = replace_str_by_pixel(hle(size))
else:
    if MANCHESTER_MODE:
        imgs_arr = naive_Manchester(size) 
    elif CRC4:
        imgs_arr = replace_str_by_pixel(change_order(crc_encode(size, val_mode=True)))
    elif fiveBsixB:
        imgs_arr = replace_str_by_pixel(change_order(fiveBsixB_encode(size, val_mode=True)))
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
    #if d == 'test.mp4':
    if d == 'test.mkv':
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
    #out_name = 'one_value_'+ val_mode + '_' + str(rate) + '_' + str(SIZE[0]) + 'x' + str(SIZE[1]) +  '_' +  str(ZOOM) + 'x.mp4' 
    out_name = 'one_value_'+ val_mode + '_' + str(rate) + '_' + str(SIZE[0]) + 'x' + str(SIZE[1]) +  '_' +  str(ZOOM) + 'x.mkv' 
else:
    #out_name = 'location_' + str(rate)+ '_' + str(SIZE[0]) + 'x' + str(SIZE[1]) +  '_' +  str(ZOOM) +  '.mp4'
    out_name = 'location_' + str(rate)+ '_' + str(SIZE[0]) + 'x' + str(SIZE[1]) +  '_' +  str(ZOOM) +  '.mkv'

if MANCHESTER_MODE:
    out_name = 'Manchester_' + out_name

if CRC4:
    out_name = 'CRC4_' + out_name

if fiveBsixB:
    out_name = 'fiveBsixB_' + out_name

#os.system('ffmpeg -r ' + str(rate) + ' -f image2  -i location__%02d.png -vcodec libx264 -crf 10 -pix_fmt yuv420p test.mp4')
#os.system('ffmpeg -f concat -i new.txt -c copy ' + out_name)
os.system('ffmpeg -framerate ' + str(rate) + ' -i location__%02d.png -vcodec copy test.mkv')
os.system('ffmpeg -f concat -i new_mkv.txt -c copy ' + out_name)
    
# ffmpeg -r 50 -stream_loop 100 -i location__%02d.png -c:v huffyuv test.avi

