#!/usr/bin/env python
# coding: utf-8

# import skimage
import numpy as np
from cv2 import cv2
from skimage.transform import hough_line, hough_line_peaks
from PIL import Image, ImageEnhance
import os
import math
from scipy.ndimage.filters import gaussian_filter

import matplotlib.pyplot as plt
BORDER = 6

def get_imgs():
    dirs = os.listdir()
    angles = []
    for d in dirs:
        if d[:4] == 'red_':
            angles.append(d[4:-4])
    return angles

# def red_img_name(idx_str, prefix='./'):
#     return prefix + 'red_' + idx_str + '.png'

def white_img_name(idx_str, prefix='./'):
    return prefix + 'white_' + idx_str + '.png'

# def img_name(idx_str, color, prefix='./'):
#     return prefix + color + '_' + idx_str + '.png'

# def change_mode(cur_mode):
#     return 'white' if cur_mode == 'red' else 'red'
def get_threshold(im):
    ratio = 0.8
    # ratio = 0.5 if mode == 'white' else 0.7
    threshold = 10
    im = np.array(im)
    while sum(sum(im > threshold)) > sum(sum(im >= 0)) * ratio:
        threshold += 1
    return threshold

def calc_angle(im):
    im = ImageEnhance.Contrast(im).enhance(3)
    im = np.array(im.convert('L'))
    I_copy = np.zeros((19+BORDER,19+BORDER), np.uint8) #; % add a container; seems it really works; I_copy is only used for plot, see the real container in BW
    I_copy[int(BORDER/2):19+BORDER-int(BORDER/2),int(BORDER/2):19+BORDER-int(BORDER/2)] = im
#     im_tmp = im/255
    I_DC = gaussian_filter(im, 3)
    # I_DC = (gaussian(im, 1.5)*255).astype(np.uint8)
#     I_DC = (I_DC*255).astype(np.uint8)
    I_DC = I_DC - np.min(I_DC)
    I_DCremove = im - I_DC
    th = get_threshold(im)
    BW_temp = I_DCremove < th
    BW = np.zeros((19+BORDER, 19+BORDER))
#     print(BW.shape)
    BW[int(BORDER/2):19+BORDER-int(BORDER/2),int(BORDER/2):19+BORDER-int(BORDER/2)] = BW_temp
    H, T, R = hough_line(BW * 255)
    hspace, angles, dists = hough_line_peaks(H, T, R, min_distance=2, min_angle=1, num_peaks=10)
#     hspace, angles, dists = hough_line_peaks(H, T, R, num_peaks=30)
    H_weight = hspace.copy()
    
    top = min(max(5, sum(H_weight==max(H_weight))), len(angles))
    for i in range(top):
        for j in range(len(hspace)):
            if j == i:
                continue
            a1 = math.degrees(angles[i])
            a2 = math.degrees(angles[j])
            if abs(a1 - a2) < 3 or abs(abs(a1 - a2) - 90) < 3:
            # if abs(a1 - a2) < 3:
                H_weight[i] = H_weight[i] + hspace[j]
    
    tmp = H_weight.tolist()
    index = tmp.index(max(tmp))
    x = math.degrees(angles[index])
    rho = dists[index]
    theta = angles[index]
    ang = - x + 90
    points = calc_points(rho, theta)

    rtn = draw_lines(I_copy, (((points[0], points[1]), (points[2], points[3])),))
#     if ang > 180:
#         ang -= 180
    return ang, rtn, BW*255
def pil2cv(im):
    im = np.array(im)
    return cv2.cvtColor(im, cv2.COLOR_RGB2BGR)


def cv2pil(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return Image.fromarray(im)

def calc_points(rho, theta):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + 28*(-b))
    y1 = int(y0 + 28*(a))
    x2 = int(x0 - 28*(-b))
    y2 = int(y0 - 28*(a))
    return x1, y1, x2, y2
def draw_lines(img, lines, color=(0, 0, 255)):
    im = pil2cv(img)
    for p1, p2 in lines:
        # print(p1, p2)
        cv2.line(im, p1, p2, color, 1)
    return cv2pil(im)
def red_img_name(idx_str, prefix='./'):
    return prefix + 'red_' + idx_str + '.png'

imgs_val = get_imgs()
# imgs_val = ['122', '187', '199', '224', '313', '340', '37', '49', '51', '88']
# imgs_val = ['104']
# imgs_val = ['166', '174', '74', '81', '88']
plt.ion()
f = plt.figure()
ax = f.add_subplot(211)
ax2 = f.add_subplot(212)
t=[]
d=[]
for i in imgs_val:
    f.suptitle('Angle: '+i)
    r_im = Image.open(red_img_name(i))
    # r_im = ImageEnhance.Contrast(r_im).enhance(3)
    w_im = Image.open(white_img_name(i))
    # w_im = ImageEnhance.Contrast(w_im).enhance(1)
    ang, r_line, bim = calc_angle(r_im)
    w_ang, w_line, _ = calc_angle(w_im)
    # ax.imshow(r_line)
    # ax2.imshow(bim)
    # plt.show()
    # plt.pause(3)
    # if abs(r_ang - w_ang) <= 45:
    #     ang = w_ang
    # else:
    #     ang = w_ang + 90
    # if ang > 180:
    #     ang -= 180
#     print(i, ang)
    # ax.imshow(ang)
    # plt.show()
    # plt.pause(1)
    # continue
    correct = int(i)
    if correct > 180:
        correct -= 180
    diff1= abs(ang-correct)
    diff2 = abs(90-abs(ang-correct))
    diff3 = abs(180-abs(ang-correct))
    min_diff = min([diff1,diff2,diff3])
    if min_diff > 3:
        t.append(i)
        d.append(min_diff)
        print(i, ang, min_diff)
#     break
print(len(t))
print(t)
print(np.mean(d))



# import matlab.engine
# import numpy as np
# from Image
# eng = matlab.engine.start_matlab()
# while True:
#     value = int(input('test: '))
#     arr = np.
#     print(eng.calc_angle(value))