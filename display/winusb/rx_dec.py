import matplotlib.pyplot as plt
from collections import Counter, deque
import time
import math
import numpy as np
from PIL import Image, ImageEnhance, ImageOps  
def draw_pixel(img, value, i, j):
    for a in range(i * times, (i + 1)* times):
        for b in range(j * times, (j + 1) * times):
           img.putpixel((a, b), (value, )*3)

import win32file
import win32pipe
if __name__ == '__main__':
    times = 1
    pixel_num = 19
    line_num = 19
    img = Image.new("RGB", (line_num * times, pixel_num * times))

    f2 = plt.figure()
    ax2 = f2.add_subplot(111)
    # ax = f2.add_subplot(311)
    # ax3 = f2.add_subplot(313)


    plt.ion()
    imgs = []

    PIPE_NAME = r'\\.\pipe\test_pipe'
    PIPE_BUFFER_SIZE = 1

    named_pipe = win32pipe.CreateNamedPipe(PIPE_NAME,
                                            win32pipe.PIPE_ACCESS_DUPLEX,
                                            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT | win32pipe.PIPE_READMODE_MESSAGE,
                                            win32pipe.PIPE_UNLIMITED_INSTANCES,
                                            PIPE_BUFFER_SIZE,
                                            PIPE_BUFFER_SIZE, 500, None)

    while True:
        count = 0
        try:
            while count < pixel_num * line_num:
                win32pipe.ConnectNamedPipe(named_pipe, None)
                data = win32file.ReadFile(named_pipe, PIPE_BUFFER_SIZE, None)

                val = int.from_bytes(data[1], 'big')
                
                i = math.floor(count / pixel_num)
                j = count % pixel_num
                count += 1
                draw_pixel(img, val, i, j)

            ax2.imshow(img)
            plt.show()
            plt.pause(1e-16)
        except BaseException as e:
            print ("exception:", e)
            break
    win32pipe.DisconnectNamedPipe(named_pipe)

