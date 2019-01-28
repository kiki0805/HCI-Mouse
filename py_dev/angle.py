import numpy as np
import math
import time
from collections import Counter
from cv2 import cv2
from PIL import Image
from direction_judge import move_direction
from comm_handler import TypeName


RESOLUTION = (19, 19)
COLOR_CHANGE_INTERVAL = 1.5 # seconds


def pil2cv(im):
    im = np.array(im)
    return cv2.cvtColor(im, cv2.COLOR_RGB2BGR)


def cv2pil(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return Image.fromarray(im)


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

    for l in remained_lines:
        (x1,y1), (x2,y2) = l
        cv2.line(img, (x1,y1), (x2,y2), (0,0,255), 1) # red line

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


def change_cur(cur):
    if cur == 'red':
        print('changing to white...')
        time.sleep(COLOR_CHANGE_INTERVAL)
        print('done')
        return 'white'
    else:
        print('changing to red...')
        time.sleep(COLOR_CHANGE_INTERVAL)
        print('done')
        return 'red'


def get_threshold(im, mode):
    ratio = 3 / 2 if mode == 'white' else 2.5 / 2
    threshold = 10
    im = np.array(im)
    while sum(sum(sum(im > threshold))) > sum(sum(sum(im >= 0))) / ratio:
        threshold += 10
    return threshold


class AngleMeasurer:
    def __init__(self):
        self.img = Image.new("RGB", RESOLUTION)
        self.collect = 0
        self.cur = 'red'
        self.red_angle = None
        self.red_lines = None
        # self.white_angle = None
        # self.white_lines = None
    
    def update_red_mode(self, threshold):
        _, angles, remained_lines = detect_line(self.img, threshold, 'red')
        
        if angles == []:
            return
        most_comm_ele = Counter(angles).most_common()[0][0]
        if remained_lines is None:
            return
        self.red_angle = most_comm_ele
        self.red_lines = remained_lines
        self.cur = change_cur(self.cur)
        self.collect = 3
        return TypeName.ANGLE_COLOR2WHITE, 0

    def update_white_mode(self, threshold):
        _, angles, remained_lines = detect_line(self.img, threshold, 'white', self.red_angle)
        while angles == []:
            threshold += 5
            _, angles, remained_lines = detect_line(self.img, threshold, 'white', self.red_angle)
        if len(angles) == 0 or remained_lines is None:
            return
        most_comm_ele = Counter(angles).most_common()[0][0]
        white_angle = most_comm_ele
        white_lines = remained_lines
        md = move_direction(self.red_lines, white_lines)
        if md == '↑':
            print(md, 180 - white_angle)
            return TypeName.ANGLE, 180 - white_angle
        elif md == '↓':
            print(md, 360 - white_angle)
            return TypeName.ANGLE, 360 - white_angle
        elif type(md) == int:
            print(md)
            return TypeName.ANGLE, md
        self.cur = change_cur(self.cur)
        self.collect = 3
        return TypeName.ANGLE_COLOR2RED, 0


    def update(self, vals):
        count = 0
        for v in vals:
            i = math.floor(count / RESOLUTION[0])
            j = count % RESOLUTION[1]
            self.img.putpixel((i, j), (v, ) * 3)
            count += 1
        
        if self.collect != 0:
            self.collect -= 1
            return
        
        threshold = get_threshold(self.img, self.cur)
        
        if self.cur == 'red':
            return self.update_red_mode(threshold)
        else:
            return self.update_white_mode(threshold)
            