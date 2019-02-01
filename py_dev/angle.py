import numpy as np
import math
import time
from collections import Counter
from cv2 import cv2
from PIL import Image
from direction_judge import move_direction
from skimage.transform import hough_line, hough_line_peaks
from PIL import Image, ImageEnhance
from scipy.ndimage.filters import gaussian_filter
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


# def get_threshold(im, mode):
#     ratio = 3 / 2 if mode == 'white' else 2.5 / 2
#     threshold = 10
#     im = np.array(im)
#     while sum(sum(sum(im > threshold))) > sum(sum(sum(im >= 0))) / ratio:
#         threshold += 10
#     return threshold
def get_threshold(im, ratio=0.8):
    # ratio = 0.5 if mode == 'white' else 0.7
    threshold = 10
    im = np.array(im)
    while sum(sum(im > threshold)) > sum(sum(im >= 0)) * ratio:
        threshold += 1
    return threshold

class AngleMeasurer:
    def __init__(self):
        self.img = Image.new("RGB", RESOLUTION)
        self.collect = 0
        self.cur = 'red'
        self.red_angle = None
        self.red_lines = None
        self.r_ang = None
        self.w_ang = None
        self.raw_rx = None
        self.r_rhos = None
        self.w_rhos = None
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

    def calc_angle(self, im):
        mode = self.cur
        BORDER = 6
        if mode == 'white':
            GAUSSIAN_STRENGTH = 1.5
            MIN_DISTANCE = 0
            MIN_ANGLE = 0
            NUM_PEAKS = 20
            TOLERATE_DIFF = 2
        elif mode == 'red':
            im = ImageEnhance.Contrast(im).enhance(4)
            GAUSSIAN_STRENGTH = 3
            MIN_DISTANCE = 2
            MIN_ANGLE = 1
            NUM_PEAKS = 10
            TOLERATE_DIFF = 3

        im = np.array(im.convert('L'))
        I_DC = gaussian_filter(im, GAUSSIAN_STRENGTH)
        I_DC = I_DC - np.min(I_DC)
        I_copy = np.zeros((19+BORDER,19+BORDER), np.uint8)
        I_copy[int(BORDER/2):19+BORDER-int(BORDER/2),int(BORDER/2):19+BORDER-int(BORDER/2)] = im
        I_DCremove = im - I_DC
        
        if mode == 'white':
            th = np.median(I_DCremove) - 6
        elif mode == 'red':
            th = get_threshold(I_DCremove)

        BW_temp = I_DCremove < th
        BW = np.zeros((19+BORDER, 19+BORDER))
        BW[int(BORDER/2):19+BORDER-int(BORDER/2),int(BORDER/2):19+BORDER-int(BORDER/2)] = BW_temp
        H, T, R = hough_line(BW * 255)
        hspace, angles, dists = hough_line_peaks(H, T, R, min_distance=MIN_DISTANCE, min_angle=MIN_ANGLE, num_peaks=NUM_PEAKS)
        H_weight = hspace.copy()
        top = min(max(5, sum(H_weight==max(H_weight))), len(angles))
        for i in range(top):
            for j in range(len(hspace)):
                if j == i:
                    continue
                a1 = math.degrees(angles[i])
                a2 = math.degrees(angles[j])
                if mode == 'red':
                    if abs(a1 - a2) < TOLERATE_DIFF:
                        H_weight[i] = H_weight[i] + hspace[j]
                elif mode == 'white':
                    if abs(a1 - a2) < TOLERATE_DIFF or abs(abs(a1 - a2) - 90) < TOLERATE_DIFF:
                        H_weight[i] = H_weight[i] + hspace[j]
        tmp = H_weight.tolist()
        index = tmp.index(max(tmp))
        x = math.degrees(angles[index])
        rho = dists[index]
        theta = angles[index]
        ang = - x + 90
        # points = calc_points(rho, theta)
        rtn = I_copy
        # rtn = draw_lines(I_copy, (((points[0], points[1]), (points[2], points[3])),))

        ag = angles[index]
        # if mode == 'red':
        #     th = get_threshold(I_DCremove, 0.6)
        #     BW_temp = I_DCremove < th
        # BW[int(BORDER/2):19+BORDER-int(BORDER/2),int(BORDER/2):19+BORDER-int(BORDER/2)] = BW_temp
        H, T, R = hough_line(BW * 255)
        hspace, angles, dists = hough_line_peaks(H, T, R, min_distance=1, min_angle=1, num_peaks=NUM_PEAKS*50)
        rhos = [[], []]
        for i in range(len(angles)):
            if math.degrees(abs(angles[i] - ag)) < TOLERATE_DIFF*2:
                # print('same angle')
                rhos[0].append(dists[i])
            if abs(90 - math.degrees(abs(angles[i] - ag))) < TOLERATE_DIFF*2:
                # print('verticle angle')
                rhos[1].append(dists[i])
        # rhos[0]: rhos of the similar angle as returned one
        # rhos[1]: rhos of the verticle angle as returned one
        return ang, rtn, rhos, x

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
        
        # threshold = get_threshold(self.img, self.cur)
        
        if self.cur == 'red':
            # return self.update_red_mode(threshold)
            self.r_ang, _, self.r_rhos, self.raw_rx = self.calc_angle(self.img)
            return TypeName.ANGLE_COLOR2WHITE, 0
        else:
            self.w_ang, _, self.w_rhos, _ = self.calc_angle(self.img)
            ang = self.get_angle()
            return TypeName.ANGLE, ang
            # return self.update_white_mode(threshold)
    
    def get_angle(self):
        r_ang=self.r_ang
        w_ang=self.w_ang
        raw_rx=self.raw_rx
        r_rhos=self.r_rhos
        w_rhos=self.w_rhos
        rhos = []
        if abs(r_ang - w_ang) <= 45:
            ang = w_ang
            rhos.append(w_rhos[0])
            rhos.append(r_rhos[0])
        else:
            ang = w_ang + 90
            rhos.append(w_rhos[1])
            rhos.append(r_rhos[0])
        min_dist = 999
        min_dist_r = [[], []]
        for r1 in rhos[0]:
            for r2 in rhos[1]:
                if r1 == r2:
                    continue
                if abs(r1-r2) < min_dist:
                    min_dist = abs(r1-r2)
                    min_dist_r[0] = [r1]
                    min_dist_r[1] = [r2]
                elif abs(r1-r2) == min_dist:
                    if abs(np.mean(min_dist_r[1]) - r2) < min_dist:
                        min_dist_r[1].append(r2)
                        min_dist = abs(np.mean(min_dist_r[0]) - np.mean(min_dist_r[1]))
            
        min_dist_r = [np.mean(min_dist_r[0]), np.mean(min_dist_r[1])]
        raw_rx = math.radians(raw_rx)

        positive = min_dist_r[0] - min_dist_r[1] > 0
        if ang > 180:
            ang -= 180
        ang -= 90
        if ang < 0:
            ang += 180
        theta_positive = raw_rx > 0
        if positive == theta_positive:
            return ang + 180
        else:
            return ang
