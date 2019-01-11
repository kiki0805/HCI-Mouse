import usb.core
import matplotlib.pyplot as plt
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

save_img = True if input('capture image and save: ') == "1" else False
f2 = plt.figure()
ax2 = f2.add_subplot(111)

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


def detect_line(im):
    img = pil2cv(im)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = gray.copy()
    edges[gray<150] = 255
    edges[gray>150] = 0
    # print(edges)
    # edges = cv2.Canny(gray,150,230,apertureSize=3)
    # print(edges)
    # return cv2pil(edges)
    # edges = gray < 120
    # edges = edges.astype(int)
    # edges[edges == 1] = 255
    # edges[edges == 0] = 0
    # print(edges)
    # minLineLength = 19
    # maxLineGap = 2
    # lines = cv2.HoughLinesP(edges,1,np.pi/180,10,minLineLength,maxLineGap)
    # for line in lines[:3]:
    #     for x1,y1,x2,y2 in line:
    #         cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 1)
    if lines is None:
        return im, None
    angles = []
    for line in lines[:1]:
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
            angles.append(angle)
            cv2.line(img, (x1,y1), (x2,y2),(0,0,255),1)
    median_angle = np.median(angles)
    return cv2pil(img), median_angle

def binirization(im, value):
    im = np.array(im)
    new = im.copy()
    new[im < value] = 0
    new[im > value] = 255
    return Image.fromarray(new)

while True:
    count = 0
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

    img = ImageEnhance.Contrast(img).enhance(5) # 5 for first step, 3 for second step
    # img = binirization(img, 180)
    # img = ImageOps.invert(img)
    img, angle = detect_line(img)
    # if angle is not None:
        # print(angle)

    if save_img:
        # out = [str(i) for i in out]
        # print(out)
        # print(' '.join(out))
        img.save('test.png')
        plt.ioff()
        ax2.imshow(img)
        plt.show()
        break

    
    ax2.imshow(img)
    plt.show()
    plt.pause(1e-16)

