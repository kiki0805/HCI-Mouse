import usb.core
import matplotlib.pyplot as plt
from collections import Counter, deque
import time
import math
from cv2 import cv2
import numpy as np
import usb.util
from PIL import Image, ImageEnhance, ImageOps  
from direction_judge import move_direction

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


def detect_line(im, threshold, mode, ref=None, vote=1):
    img = pil2cv(im)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = gray.copy()
    edges[gray<threshold] = 255
    edges[gray>threshold] = 0
    
    lines = cv2.HoughLines(edges, 1, np.pi/180, vote)
    if lines is None:
        return im, [], None

    remained_lines, angles = _detect_line(lines, ref)
    if remained_lines is None and mode=='red':
        return detect_line(im, threshold, mode, ref, vote+1)
        # return cv2pil(img), angles, remained_lines

    for l in remained_lines:
        (x1,y1), (x2,y2) = l
        cv2.line(img, (x1,y1), (x2,y2),(0,0,255),1)

    return cv2pil(img), angles, remained_lines

def _detect_line(lines, ref=None):
    angles = []
    ls = []
    for line in lines[:10]:
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
            ls.append(((x1,y1), (x2,y2)))
            
    if ref is not None:
        # print('ref: ' + str(ref))
        valid_angle = []
        remained_index = []
        for i in range(len(angles)):
            ag = angles[i]
            if abs(ag - ref) < 6:
                valid_angle.append(ag)
                remained_index.append(i)
        if valid_angle != []:
            angles = valid_angle
        remained_lines = [ls[i] for i in remained_index]
        return remained_lines, angles
        
    most_comm_ele = Counter(angles).most_common()[0][0]
    remained_index = [[], []]
    two_set_angles = [[], []]
    for i in range(len(angles)):
        ag = angles[i]
        if abs(ag - most_comm_ele) < 6:
            remained_index[0].append(i)
            two_set_angles[0].append(ag)
        if abs(90 - abs(ag - most_comm_ele)) < 6:
            remained_index[1].append(i)
            two_set_angles[1].append(ag)

    if ref is not None:
        remained_lines = [ls[i] for i in remained_index[0]]
        return remained_lines, two_set_angles[0]
    elif two_set_angles[0] == []:
        remained_lines = [ls[i] for i in remained_index[1]]
        return remained_lines, two_set_angles[1]
    elif two_set_angles[1] == []:
        remained_lines = [ls[i] for i in remained_index[0]]
        return remained_lines, two_set_angles[0]
    else:
        return None, []

def binirization(im, value):
    im = np.array(im)
    new = im.copy()
    new[im < value] = 0
    new[im >= value] = 255
    return Image.fromarray(new)

def erode(img, kernel, iterations):
    img = cv2.erode(pil2cv(img),kernel,iterations = iterations)
    return cv2pil(img)

def openning(img, kernel):
    opening = cv2.morphologyEx(pil2cv(img), cv2.MORPH_OPEN, kernel)
    return cv2pil(opening)

def closing(img, kernel):
    img = cv2.morphologyEx(pil2cv(img), cv2.MORPH_CLOSE, kernel)
    return cv2pil(img)


def change_cur(cur):
    if cur == 'red':
        print('changing to white...')
        time.sleep(1.5)
        print('done')
        return 'white'
    else:
        print('changing to red...')
        time.sleep(1.5)
        print('done')
        return 'red'

def get_threshold(im, mode):
    ratio = 3 / 2 if mode == 'white' else 2.5 / 2
    threshold = 10
    im = np.array(im)
    while sum(sum(sum(im > threshold))) > sum(sum(sum(im >= 0))) / ratio:
        threshold += 10
    return threshold

cur = 'red'

red_angle = None
red_lines = None
white_angle = None
white_lines = None
collect = 0
while True:
    count = 0
    # cur='red'
    while count < pixel_num * line_num:
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

    if collect != 0:
        collect -= 1
        continue

    # img = ImageEnhance.Contrast(img).enhance(5)
    # img = binirization(img, 60)
    # ax2.imshow(img)
    # plt.show()
    # plt.pause(1e-16)
    # img = ImageOps.invert(img)

    # threshold = 60 if cur == 'red' else 170
    threshold = get_threshold(img, cur)
    img2 = binirization(img, threshold)
    
    if cur == 'red':
        # img = ImageEnhance.Contrast(img).enhance(5)
        # img = binirization(img, threshold)
        # kernel = np.ones(((2,2)),np.uint8)
        # img = openning(img, kernel)
        img, angles, remained_lines = detect_line(img, threshold, 'red')
        
        if angles == []:
            continue
        most_comm_ele = Counter(angles).most_common()[0][0]
        if remained_lines is not None:
            red_angle = most_comm_ele
            red_lines = remained_lines
            cur = change_cur(cur)
            collect = 3
    else:
        # img = ImageEnhance.Contrast(img).enhance(5)
        # img = binirization(img, threshold)
        # kernel2 = np.zeros((2,2), np.uint8)
        # img = erode(img, kernel2, 1) # maybe 2
        img, angles, remained_lines = detect_line(img, threshold, 'white', red_angle)
        while angles == []:
            threshold += 5
            img, angles, remained_lines = detect_line(img, threshold, 'white', red_angle)
        if len(angles) > 1 and remained_lines is not None:
            most_comm_ele = Counter(angles).most_common()[0][0]
            white_angle = most_comm_ele
            white_lines = remained_lines
            md = move_direction(red_lines, white_lines)
            if md == '↑':
                print(md, 180 - white_angle)
            elif md == '↓':
                print(md, 360 - white_angle)
            elif type(md) == int:
                print(md)
            cur = change_cur(cur)
            collect = 3
    ax.imshow(img2)
    ax2.imshow(img)
    plt.show()
    plt.pause(1e-16)

