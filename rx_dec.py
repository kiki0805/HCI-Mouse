import usb.core
import imageio
import matplotlib.pyplot as plt
from matplotlib import animation
import pprint
import time
import math
import numpy as np
import usb.util
from PIL import Image

times = 25
pixel_num = 19
line_num = 19
img = Image.new("L", (line_num * times, pixel_num * times))
old_img = Image.new("L", (line_num * times, pixel_num * times))

save_img = True if input('capture image and save: ') == "1" else False
f1 = plt.figure()
f2 = plt.figure()
f3 = plt.figure()
ax1 = f1.add_subplot(111)
ax2 = f2.add_subplot(111)
ax3 = f3.add_subplot(111)

device = usb.core.find(idVendor=0x046d, idProduct=0xc077)

if device.is_kernel_driver_active(0):
    device.detach_kernel_driver(0)

device.set_configuration()

def init():
    response = device.ctrl_transfer(bmRequestType = 0x40, #Write
                                         bRequest = 0x01,
                                         wValue = 0x0000,
                                         wIndex = 0x0D, #PIX_GRAB register value
                                         data_or_wLength = None
                                         )

init()

imgs = []

def draw_pixel(img, value, i, j):
    for a in range(i * times, (i + 1)* times):
        for b in range(j * times, (j + 1) * times):
           img.putpixel((a, b), int.from_bytes(value,'big'))

img_num = 0
plt.ion()
start = time.time()
l = np.array([])
max_num = 0
while True:
    count = 0
    pixList = []
    out = []
    while len(pixList) < pixel_num * line_num:
        temp = 0
        response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                         bRequest = 0x01,
                         wValue = 0x0000,
                         wIndex = 0x0D, #PIX_GRAB register value
                         data_or_wLength = 1
                         )
        pixList.append(response)
        out.append(int.from_bytes(response,'big'))
        max_num = max(max_num, int.from_bytes(response, 'big'))
        # print(max_num)
        l = np.append(l, int.from_bytes(response, 'big'))
        i = math.floor(count / pixel_num)
        j = count % pixel_num
        count += 1
        # print(int.from_bytes(response, 'big'))
        draw_pixel(img, response, i, j)
        # if save_img:
        #     time.sleep(0.005)
    
    new_out = []
    for i in range(len(out)):
        if i % pixel_num > 12.5:
            new_out.append(out[i])

    new_out = np.array(new_out)

    print('>175: ' + str(len(new_out[new_out>175])))
    print('<165: ' + str(len(new_out[new_out<165])))
    print('Var: ' + str(np.var(new_out)))
    freq_occur = {} 
    cdf = {}
    for i in range(110,250,5):
        y1 = len(new_out[np.logical_and(new_out>i, new_out<=i+5)])
        y3 = len(new_out[new_out<=i+5])
        freq_occur[i+2.5] = y1
        cdf[i+2.5] = y3

    if save_img:
        # out = [str(i) for i in out]
        # print(out)
        # print(' '.join(out))
        # img.save('test.png')
        plt.ioff()
            
        ax1.bar(range(110,250,5), list(freq_occur.values()))
        ax3.bar(range(110,250,5), list(cdf.values()))
        ax2.imshow(img)
        plt.show()
        break

    
    print('>175: ' + str(len(new_out[new_out>175])))
    print('<165: ' + str(len(new_out[new_out<165])))
    print('Var: ' + str(np.var(new_out)))
    freq_occur = {} 
    cdf = {}
    for i in range(110,250,5):
        y1 = len(new_out[np.logical_and(new_out>i, new_out<=i+5)])
        y3 = len(new_out[new_out<=i+5])
        freq_occur[i+2.5] = y1
        cdf[i+2.5] = y3
    ax1.cla()
    ax3.cla()
    # print(list(freq_occur.keys()))
    # print(list(freq_occur.values()))
    print(list(cdf.values()))

    # fix height 
    freq_occur[112.5] = 50
    cdf[112.5] = 121


    ax1.bar(range(110,250,5), list(freq_occur.values()))
    ax3.bar(range(110,250,5), list(cdf.values()))
    ax2.imshow(img)
    plt.show()
    plt.pause(0.00036)

