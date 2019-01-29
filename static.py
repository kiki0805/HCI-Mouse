import usb.core
import matplotlib.pyplot as plt
from collections import Counter, deque
import time
import math
from cv2 import cv2
import numpy as np
import usb.util
import os
import scipy.ndimage as ndimage
import statistics
from PIL import Image, ImageEnhance, ImageOps  
from direction_judge import move_direction

def get_imgs():
    dirs = os.listdir()
    angles = []
    for d in dirs:
        if d[:4] == 'red_':
            angles.append(d[4:-4])
    return angles

def pil2cv(im):
    im = np.array(im)
    return cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

def cv2pil(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return Image.fromarray(im)

f2 = plt.figure()
ax2 = f2.add_subplot(211)
ax = f2.add_subplot(212)

plt.ion()


def detect_line(im, threshold, mode, ref=None, vote=7):
    if vote > 1:
        pass
        # print('vote: ', vote)
        # return im, [], None, None, None
    img = pil2cv(im)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = gray.copy()
    edges[gray<=threshold] = 255
    edges[gray>threshold] = 0
    
    lines = cv2.HoughLines(edges, 1, np.pi/180, vote)
    if lines is None:
        return im, [], None, None, None, None

    remained_lines, angles, rmd_rhos, rmd_thetas, v_angles = _detect_line(lines, ref)
    if remained_lines is None and mode=='red':
        return detect_line(im, threshold, mode, ref, vote+1)
        # return cv2pil(img), angles, remained_lines

    color = (0, 0, 255) if mode == 'red' else (255, 0, 0)
    # print('Draw: ', end='')
    # print(remained_lines)
    if remained_lines is None:
        return im, [], None, None, None, None
    for l in remained_lines:
        (x1,y1), (x2,y2) = l
        cv2.line(img, (x1,y1), (x2,y2), color, 1)

    return cv2pil(img), angles, remained_lines, rmd_rhos, rmd_thetas, v_angles


def _detect_line(lines, ref=None, tolerate_diff=2):
    if tolerate_diff != 3:
        pass
        # print('tolerate_diff: ', tolerate_diff)
        
    angles = []
    ls = []
    rhos = []
    thetas = []
    for line in lines[:10]:
        for rho, theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            # print('rho: %f; theta: %f; (x0,y0):(%d,%d)' % (rho, math.degrees(theta), x0, y0))
            # print((x0, y0))
            # x1 = int(x0 + (19-x0)*(-b))
            # y1 = int(y0 + (y0)*(a))
            # x2 = int(x0 - x0*(-b))
            # y2 = int(y0 - (19-y0)*(a))
            # print((x1, y1), (x2, y2))
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            angle += 90
            if angle < 0:
                angle += 360
            if angle > 360:
                angle -= 360
            if angle > 180:
                angle -= 180
            # if angle == 45 or angle == 135:
            #     continue
            angles.append(angle)
            ls.append(((x1,y1), (x2,y2)))
            rhos.append(rho)
            thetas.append(theta)
            
    if ref is not None:
        # print('ref: ' + str(ref))
        valid_angle = []
        remained_index = []
        v_angles = []
        for i in range(len(angles)):
            ag = angles[i]
            # print(abs(ag - ref))
            if abs(ag - ref) < tolerate_diff:
                valid_angle.append(ag)
                remained_index.append(i)
            elif abs(90 - abs(ag - ref)) < tolerate_diff:
                v_angles.append(ag)
        while valid_angle == [] and tolerate_diff < 5:
            return _detect_line(lines, ref, tolerate_diff + 1)
        if valid_angle == []:
            return None, [], None, None, []
        angles = valid_angle
        rmd_rhos = [rhos[i] for i in remained_index]
        rmd_thetas = [thetas[i] for i in remained_index]
        remained_lines = [ls[i] for i in remained_index]
        return remained_lines, angles, rmd_rhos, rmd_thetas, v_angles
        
    most_comm_ele = Counter(angles).most_common()[0][0]
    remained_index = [[], []]
    two_set_angles = [[], []]
    i = 0
    while i < len(angles):
        ag = angles[i]
        if abs(ag - most_comm_ele) < 3:
            remained_index[0].append(i)
            two_set_angles[0].append(ag)
        elif abs(90 - abs(ag - most_comm_ele)) < 3:
            remained_index[1].append(i)
            two_set_angles[1].append(ag)
        # elif abs(ag - 45) < 2 or abs(ag - 135) < 2:
        #     ag.remove
        #     most_comm_ele = Counter(angles).most_common()[1][0]
        #     remained_index = [[], []]
        #     two_set_angles = [[], []]
        #     i = 0
        i += 1
    
    if two_set_angles[0] == []:
        rmd_rhos = [rhos[i] for i in remained_index[1]]
        rmd_thetas = [thetas[i] for i in remained_index[1]]
        remained_lines = [ls[i] for i in remained_index[1]]
        return remained_lines, two_set_angles[1], rmd_rhos, rmd_thetas, None
    elif two_set_angles[1] == []:
        rmd_rhos = [rhos[i] for i in remained_index[0]]
        rmd_thetas = [thetas[i] for i in remained_index[0]]
        remained_lines = [ls[i] for i in remained_index[0]]
        return remained_lines, two_set_angles[0], rmd_rhos, rmd_thetas, None
    else:
        return None, [], None, None, None

def binirization(im, value):
    im = np.array(im)
    new = im.copy()
    new[im < value] = 0
    # new[im >= value] = 255
    new[im >= value] = 1
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

def dilation(img, kernel, iterations):
    dilation = cv2.dilate(pil2cv(img),kernel,iterations = iterations)
    return cv2pil(dilation)
def change_cur(cur):
    if cur == 'red':
        return 'white'
    else:
        return 'red'


def get_threshold(im, mode):
    ratio = 0.7 if mode == 'white' else 0.95
    threshold = 10
    im = np.array(im)
    # while sum(sum(im > threshold)) > sum(sum(im >= 0)) * ratio:
    while sum(sum(sum(im > threshold))) > sum(sum(sum(im >= 0))) * ratio:
        threshold += 3
    return threshold

cur = 'red'
imgs = get_imgs()
# imgs = ['282']
# imgs = ['175', '107', '56', '81', '108']
# imgs = ['175', '140', '56', '81', '199', '108', '282']
# imgs = ['140', '56', '282']
graphics = True
imgs = ['12']
# graphics = False
STOP_INTERVAL = 1e-6
# imgs = ['175', '158', '144', '172']
# imgs = ['158']
# imgs = ['107', '144', '205']

red_angle = None
red_lines = None
red_rhos = None
red_thetas = None
white_angle = None
white_lines = None
white_rhos = None
white_thetas = None
collect = 0
idx = 0
wrong_count = 0
wrong_list = []
error_list = []
large_error = []
threshold_increase_count = 0
red_threshold_increase = 0
white_threshold_increase = 0
threshold_increase = 0

while True:
    count = 0
    # cur='red'
    if idx == len(imgs):
        break
    img = Image.open(cur + '_' + imgs[idx] + '.png')
    
    # img = ImageEnhance.Contrast(img).enhance(5)
    # threshold = get_threshold(img, cur)
    ######################

    ax2.imshow(img)
    # img2 = cv2pil(cv2.GaussianBlur(pil2cv(img) ,(5,5),0))
    # for i in range(100):
    #     img2 = cv2pil(cv2.GaussianBlur(pil2cv(img2) ,(5,5),0))

    # img = cv2pil(pil2cv(img) - pil2cv(img2) + np.min(img2))
    kernel = np.ones((2,2, 3))
    kernel3 = np.zeros((2,2), np.uint8)
    kernel2 = np.array((1, 0), np.uint8)
    # img = dilation(img, kernel, 1)
    # img = ndimage.grey_closing(np.array(ImageOps.invert(img)), structure=kernel)
    # img = Image.fromarray(img)
    threshold = get_threshold(img, cur)
    img = binirization(img, threshold)
    img = ndimage.binary_closing(np.array(ImageOps.invert(img)), structure=kernel)
    img = Image.fromarray(img)
    # img = ndimage.binary_closing(np.array(ImageOps.invert(img)), structure=kernel)
    # img = Image.fromarray(img)
    # img = closing(ImageOps.invert(img), kernel)
    # img = erode(img, kernel2, 1)
    img = ImageOps.invert(img)
    print(threshold)
    ax.imshow(img)
    plt.show()
    plt.pause(STOP_INTERVAL)

    input('continue')
    cur = change_cur(cur)
    
    # if cur == 'red':
    #     threshold += red_threshold_increase
    #     im, angles, remained_lines, rmd_rhos, rmd_thetas, _ = detect_line(img, threshold, 'red')
    #     img2 = binirization(img, threshold)
    #     if remained_lines is None:
    #         print('FAIL')
    #         if graphics:
    #             ax.imshow(img2)
    #             ax2.imshow(im)
    #             plt.show()
    #             plt.pause(STOP_INTERVAL)
    #         input('FAIL now')
    #     # while remained_lines is None:
    #     #     threshold += 5
    #     #     # print('RED: increase threshold')
    #     #     img2 = binirization(img, threshold)
    #     #     im, angles, remained_lines, rmd_rhos, rmd_thetas, _ = detect_line(img, threshold, 'red')
    #     #     if graphics:
    #     #         ax.imshow(img2)
    #     #         ax2.imshow(im)
    #     #         plt.show()
    #     #         plt.pause(STOP_INTERVAL)
    #     most_comm_ele = Counter(angles).most_common()[0][0]
    #     red_angle = most_comm_ele
    #     red_lines = remained_lines
    #     red_rhos = rmd_rhos
    #     red_thetas = rmd_thetas
    #     cur = change_cur(cur)

    # else:
    #     threshold += white_threshold_increase
    #     img2 = binirization(img, threshold)
    #     im, angles, remained_lines, rmd_rhos, rmd_thetas, v_angles = detect_line(img, threshold, 'white', red_angle)
    #     if remained_lines is None:
    #         print('FAIL')
    #         if graphics:
    #             ax.imshow(img2)
    #             ax2.imshow(im)
    #             plt.show()
    #             plt.pause(STOP_INTERVAL)
    #         input('FAIL now')
    #     # if remained_lines is None:
    #     #     if threshold_increase_count > 15:
    #     #         white_threshold_increase = 0
    #     #         red_threshold_increase += 3
    #     #         threshold_increase_count = 0
    #     #         # print('RED: increase threshold')
    #     #         cur = change_cur(cur)
    #     #         if graphics:
    #     #             ax.imshow(img2)
    #     #             ax2.imshow(im)
    #     #             plt.show()
    #     #             plt.pause(STOP_INTERVAL)
    #     #         continue
    #     #     white_threshold_increase += 3
    #     #     threshold_increase_count += 1
    #     #     # print('WHITE: increase threshold')
    #     #     if graphics:
    #     #         ax.imshow(img2)
    #     #         ax2.imshow(im)
    #     #         plt.show()
    #     #         plt.pause(STOP_INTERVAL)
    #     #     continue

    #     most_comm_ele = Counter(angles).most_common()[0][0]
    #     white_angle = most_comm_ele
    #     white_lines = remained_lines
    #     white_rhos = rmd_rhos
    #     white_thetas = rmd_thetas
    #     if v_angles != []:
    #         v_most_comm_ele = Counter(v_angles).most_common()[0][0]
    #         # tmp = 90 - v_most_comm_ele
    #         # if tmp < 0:
    #         #     tmp += 360
    #         # white_angle = (white_angle + tmp) / 2
    #     # most_comm_ele = statistics.mean(angles)
    #     md = move_direction((red_lines, white_lines, red_rhos, white_rhos, red_thetas, white_thetas))
    #     # print(red_lines, white_lines)
    #     # print(v_most_comm_ele)
    #     decoded_angle = None
    #     # v_decoded_angle = None
    #     if md == '↑':
    #         decoded_angle = 180 - white_angle
    #         # v_decoded_angle = 270 - statistics.mean(v_angles)
    #     elif md == '↓':
    #         decoded_angle = 360 - white_angle
    #         # v_decoded_angle = 270 - statistics.mean(v_angles)

    #     elif type(md) == int:
    #         decoded_angle = md
    #         v_decoded_angle = md + 90
            
    #     else:
    #         print('FAIL')
    #         if graphics:
    #             ax.imshow(img2)
    #             ax2.imshow(im)
    #             plt.show()
    #             plt.pause(STOP_INTERVAL)
    #         input('FAIL')
    #         if threshold_increase_count > 15:
    #             white_threshold_increase = 0
    #             red_threshold_increase += 3
    #             threshold_increase_count = 0
    #             # print('RED: increase threshold')
    #             cur = change_cur(cur)
    #             if graphics:
    #                 ax.imshow(img2)
    #                 ax2.imshow(im)
    #                 plt.show()
    #                 plt.pause(STOP_INTERVAL)
    #             continue
    #         white_threshold_increase += 3
    #         threshold_increase_count += 1
    #         # print('WHITE: increase threshold')
    #         if graphics:
    #             ax.imshow(img2)
    #             ax2.imshow(im)
    #             plt.show()
    #             plt.pause(STOP_INTERVAL)
    #         continue
        
    #     if decoded_angle is not None:
    #         print('correct: ' + imgs[idx])
    #         print(md, decoded_angle)
    #         if abs(decoded_angle - int(imgs[idx])) > 10 and abs(decoded_angle - int(imgs[idx])) < 350:
    #             print('!!!!!!!!!!!WRONG!!!!!!!!!')
    #             wrong_list.append(imgs[idx])
    #             wrong_count += 1
    #         else:
    #             error = decoded_angle - int(imgs[idx])
    #             if error > 10:
    #                 error -= 360
    #             elif error < -10:
    #                 error += 360
    #             print('error: ', abs(error))
    #             error_list.append(abs(error))
    #             if abs(error) > 3.2:
    #                 large_error.append(imgs[idx])
    #         print()
    #         idx += 1
    #         white_threshold_increase = 0
    #         red_threshold_increase = 0
    #         threshold_increase_count = 0
    #     cur = change_cur(cur)
        
    # if graphics:
    #     ax.imshow(img2)
    #     ax2.imshow(im)
    #     plt.show()
    #     plt.pause(STOP_INTERVAL)
    #     input('continue')

if error_list == []:
    print('All WRONG!')
else:
    print('Total wrong(' + str(wrong_count) + '): ', wrong_list)
    # print('Error list: ', error_list)
    print('Large error(' + str(len(large_error)) + '): ', large_error)
    print('Mean error: ' + str(statistics.mean(error_list)))
