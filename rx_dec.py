import usb.core
import matplotlib.pyplot as plt
from collections import Counter, deque
import time
import math
from cv2 import cv2
import numpy as np
import usb.util
from PIL import Image, ImageEnhance, ImageOps  

def pil2cv(im):
    im = np.array(im)
    return cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

def cv2pil(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return Image.fromarray(im)

times = 1
pixel_num = 19
line_num = 19
img = Image.new("RGB", (line_num * times, pixel_num * times))

f2 = plt.figure()
ax2 = f2.add_subplot(211)
ax = f2.add_subplot(212)
# ax2 = f2.add_subplot(312)
# ax = f2.add_subplot(311)
# ax3 = f2.add_subplot(313)

device = usb.core.find(idVendor=0x046d, idProduct=0xc077)

if device.is_kernel_driver_active(0):
    device.detach_kernel_driver(0)

device.set_configuration()

def init():
    device.ctrl_transfer(bmRequestType = 0x40, #Write
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
           img.putpixel((a, b), (value, )*3)

plt.ion()


def detect_line(im, threshold):
    img = pil2cv(im)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = gray.copy()
    edges[gray<threshold] = 255
    edges[gray>threshold] = 0

    # edges2 = gray.copy()
    # edges2[gray<170] = 255
    # edges2[gray>170] = 0

    lines = cv2.HoughLines(edges, 1, np.pi/180, 1)
    # lines2 = cv2.HoughLines(edges2, 1, np.pi/180, 1)
    if lines is None:
        return im, None

    remained_lines, most_comm_ele = _detect_line(lines)
    # print('red: ', end='')
    # print(remained_lines)
    for l in remained_lines:
        (x1,y1), (x2,y2) = l
        cv2.line(img, (x1,y1), (x2,y2),(0,0,255),1)
    
    # remained_lines2, most_comm_ele = _detect_line(lines2, ref_angle)
    # remained_lines2, most_comm_ele = _detect_line(lines2)
    # print('white: ', end='')
    # print(remained_lines2)
    # for l in remained_lines2:
    #     (x1,y1), (x2,y2) = l
    #     cv2.line(img, (x1,y1), (x2,y2),(255,0,0),1)

    # print(ref_angle)
    # print(most_comm_ele)

    return cv2pil(img), most_comm_ele

def _detect_line(lines, ref=None):
    angles = []
    ls = []
    for line in lines[:20]:
        for rho,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            angle += 90
            if angle < 0:
                angle += 360
            if angle > 360:
                angle -= 360
            if angle > 180:
                angle -= 180
            angles.append(angle)
            
            ########## MATH ##########
            # if x2 != x1:
            #     k = (y2-y1) / (x2-x1)
            #     b = y1 - k * x1
            # kx - y + b = 0
            # A = k, B = -1, C = b
            # |c1-c2| / (A^2+B^2)

            ls.append(((x1,y1), (x2,y2)))
    
    if ref is not None:
        valid_angle = []
        for i in range(len(angles)):
            ag = angles[i]
            if abs(ag - ref) < 3:
                valid_angle.append(ag)
        if valid_angle != []:
            angles = valid_angle
    
    most_comm_ele = Counter(angles).most_common()[0][0]
    remained_index = []
    for i in range(len(angles)):
        ag = angles[i]
        if abs(ag - most_comm_ele) < 0.5 or \
                abs(90 - abs(ag - most_comm_ele)) < 3.5:
            remained_index.append(i)

    remained_lines = [ls[i] for i in remained_index]
    return remained_lines, most_comm_ele

    
def erode(img, kernel, iterations):
    img = cv2.erode(pil2cv(img),kernel,iterations = iterations)
    return cv2pil(img)

def openning(img, kernel):
    opening = cv2.morphologyEx(pil2cv(img), cv2.MORPH_OPEN, kernel)
    return cv2pil(opening)

def closing(img, kernel):
    img = cv2.morphologyEx(pil2cv(img), cv2.MORPH_CLOSE, kernel)
    return cv2pil(img)

def binirization(im, value):
    im = np.array(im)
    new = im.copy()
    new[im <= value] = 0
    new[im > value] = 255
    return Image.fromarray(new)

def get_threshold(im):
    # ratio = 3 / 2
    ratio = 2.5 / 2
    threshold = 10
    im = np.array(im)
    while sum(sum(sum(im > threshold))) > sum(sum(sum(im >= 0))) / ratio:
        threshold += 10
    return threshold

while True:
    count = 0
    while count < pixel_num * line_num:
        # start = time.time()
        temp = 0
        response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                         bRequest = 0x01,
                         wValue = 0x0000,
                         wIndex = 0x0D, #PIX_GRAB register value
                         data_or_wLength = 1
                         )
        val = int.from_bytes(response,'big')
        i = math.floor(count / pixel_num)
        j = count % pixel_num
        count += 1
        draw_pixel(img, val, i, j)
        time.sleep(0.001)
        # print(time.time() - start)

    # ax.imshow(img)
    # print(get_threshold(img))
    threshold = get_threshold(img)
    # img = ImageEnhance.Contrast(img).enhance(5) # 5 for first step, 3 for second step
    
    # img = binirization(img, threshold)
    # # img = binirization(img, 170)
    # kernel = np.ones(((2,2)), np.uint8)
    # # img = openning(img, kernel)
    # img2 = openning(img, kernel)
    img2 = binirization(img, threshold)
    ax.imshow(img2)
    # # img = closing(img, kernel)
    # # kernel2 = np.zeros((2,2), np.uint8)
    # # img2 = erode(img, kernel2, 2)
    # # img = closing(img, kernel)
    # # img2, angle = detect_line(img2)
    # ax3.imshow(img2)
    img, angle = detect_line(img, threshold)
    ax2.imshow(img)
    

    plt.show()
    plt.pause(1e-16)

