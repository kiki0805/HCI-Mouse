from PIL import Image
import numpy as np
import random
import sys
import matplotlib.pyplot as plt
from scipy.fftpack import fft,ifft
sys.path.append("..")
from setting import *
from utils import *

val = input("Fixed value(682): ")
if val == '':
    raw_data = input('Binary format: ')
else:
    raw_data = num2bin(int(val), BITS_NUM)

data = raw_data
NRZI = input('If use NRZI? ')
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
        data = Manchester_encode(raw_data)
elif FREQ:
    print('Using FREQ...')
    data = []
    for i in raw_data:
        if i == '0': # 0.714 0.714 -0.714 -0.714
            #data += [0.866, 0, -0.866]
            data += [0.707, 0.707, -0.707, -0.707]
        else: # 1 -1
            data += [1, -1]

import matplotlib.pyplot as plt
#plt.plot(list(range(len(data))), data)
#plt.show()

print('Raw data(' +  str(len(raw_data)) + '): ' + raw_data)
print('Decoded data(' +  str(len(data)) + '): ' + str(data))

if FILTER_H:
    filtered_data = filter_high_f(np.array(list(data)))
elif FILTER:
    if not FREQ:
        filtered_data = filter_normalize(np.array(list(data)))
    else:
        # filtered_data = filter_normalize(np.array(data * 10))
        filtered_data = filter_normalize(np.array(data))
        #filtered_data = filter_normalize(np.array([1, -1, 1, -1] + data + [1, -1, 1, -1])) 
        #filtered_data = filter_normalize(np.array([-1, 1, -1, 1, 1, -1, -1, -1, 1, -1] + data + [1, -1, 1])) 
else:
    filtered_data = data
    filtered_data = [int(i) for i in filtered_data]
#print('Filtered data(' + str(len(filtered_data)) + '): \n\t', end='')
print(filtered_data)

# plt.plot(list(range(len(filtered_data))), abs(fft(filtered_data)))
# plt.show()
bits = list(data)
WIDTH = 480
HEIGHT = 1080

im_arr = np.zeros((HEIGHT, WIDTH, 3))
off = {}
BLOCK_SIZE = 4

def draw_block(im_arr, i, j, block_size, value):
    for k1 in range(block_size):
        for k2 in range(block_size):
            for n in range(3):
                im_arr[i+k1][(j+k2+2)%480][n] = value
    return im_arr

# for i in range(0,1080,BLOCK_SIZE):
#     for j in range(0,480,BLOCK_SIZE):
#         if (i / BLOCK_SIZE) % 2 == 0:
#             if (j / BLOCK_SIZE) % 2 == 0:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
#             else:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
            
#         else:
#             if (j / BLOCK_SIZE) % 2 == 0:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
#             else:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
                        
# im = Image.fromarray(np.uint8(im_arr))
# im.save('space_test_1.png')

# for i in range(0,1080,BLOCK_SIZE):
#     for j in range(0,480,BLOCK_SIZE):
#         if (i / BLOCK_SIZE) % 2 == 0:
#             if (j / BLOCK_SIZE) % 2 == 0:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
#             else:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
            
#         else:
#             if (j / BLOCK_SIZE) % 2 == 0:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
#             else:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
                        
# im = Image.fromarray(np.uint8(im_arr))
# im.save('space_test_2.png')

# for n in range(len(bits)):
#     for i in range(HEIGHT):
#         for j in range(WIDTH):
#             if (i, j) not in off:
#                 off[(i, j)] = random.randint(0, len(bits))
#             bit = bits[(n + off[(i,j)]) % len(bits)]
#             if bit == 0:
#                 im_arr[i][j][0] = 0
#                 im_arr[i][j][1] = 0
#                 im_arr[i][j][2] = 0
#             else:
#                 im_arr[i][j][0] = 255
#                 im_arr[i][j][1] = 255
#                 im_arr[i][j][2] = 255
#     im = Image.fromarray(np.uint8(im_arr))
#     im.save('random_off_' + str(n) + '.png')

for n in range(len(filtered_data)):
    for i in range(0, HEIGHT, BLOCK_SIZE):
        for j in range(0, WIDTH, BLOCK_SIZE):
            if (i / BLOCK_SIZE) % 2 == 0:
                if (j / BLOCK_SIZE) % 2 == 0:
                    #if filtered_data[n] > 0.5:
                    #    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
                    #else:
                    #    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)

                    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n] * 255)
                else:
                    #if 1 - filtered_data[n] > 0.5:
                    #    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
                    #else:
                    #    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
                    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, (1 - filtered_data[n]) * 255)
                
            else:
                if (j / BLOCK_SIZE) % 2 == 0:
                    #if 1 - filtered_data[n] > 0.5:
                    #    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
                    #else:
                    #    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
                    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, (1 - filtered_data[n]) * 255)
                else:
                    #if filtered_data[n] > 0.5:
                    #    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
                    #else:
                    #    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
                    im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n] * 255)
    im = Image.fromarray(np.uint8(im_arr))
    #im.save('../display/data/freq_' + str(val) + '_' + str(n) + '.png')
    im.save('../display/data/freq_' + str(n) + '.png')

# for n in range(len(filtered_data)):
#     for i in range(0, HEIGHT, BLOCK_SIZE):
#         for j in range(0, WIDTH, BLOCK_SIZE):
#             im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, filtered_data[n] * 255)
#     im = Image.fromarray(np.uint8(im_arr))
#     im.save('pure_' + str(n) + '.png')

# for i in range(0,1080,BLOCK_SIZE):
#     for j in range(0,480,BLOCK_SIZE):
#         if (i / BLOCK_SIZE) % 2 == 0:
#             if (j / BLOCK_SIZE) % 2 == 0:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
#             else:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
            
#         else:
#             if (j / BLOCK_SIZE) % 2 == 0:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 0)
#             else:
#                 im_arr = draw_block(im_arr, i, j, BLOCK_SIZE, 255)
