
import os
import numpy as np
from skimage.transform import hough_line, hough_line_peaks
from PIL import Image, ImageEnhance
import math
from cv2 import cv2
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
import time
import usb.util
import usb.core
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

def get_threshold(im, ratio=0.8):
    # ratio = 0.5 if mode == 'white' else 0.7
    threshold = 10
    im = np.array(im)
    while sum(sum(im > threshold)) > sum(sum(im >= 0)) * ratio:
        threshold += 1
    return threshold

def calc_angle(im_raw, mode, ref=None):
    BORDER = 6
    if mode == 'white':
        im = im_raw
        GAUSSIAN_STRENGTH = 1.5
        MIN_DISTANCE = 0
        MIN_ANGLE = 0
        NUM_PEAKS = 20
        TOLERATE_DIFF = 2
    elif mode == 'red':
        im = ImageEnhance.Contrast(im_raw).enhance(4)
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
    points = calc_points(rho, theta)
    rtn = I_copy
    rtn = draw_lines(I_copy, (((points[0], points[1]), (points[2], points[3])),))

    ag = theta
    if ref is not None:
        ag = ref
    rows, cols = H.shape
    rhos = [[], []]
    votes = [[], []]
    for i in range(rows):
        for j in range(cols):
            if math.degrees(abs(T[j] - ag)) < 1 and H[i][j] > 4:
                # print('same angle')
                rhos[0].append(R[i])
                votes[0].append(H[i][j])
            if abs(180 - math.degrees(abs(T[j] - ag))) < 1 and H[i][j] > 4:
                # print('same angle')
                rhos[0].append(R[i])
                votes[0].append(H[i][j])
            if abs(90 - math.degrees(abs(T[j] - ag))) < 2 and H[i][j] > 4:
                # print('verticle angle')
                rhos[1].append(R[i])
                votes[1].append(H[i][j])
    # rhos[0]: rhos of the similar angle as returned one
    # rhos[1]: rhos of the verticle angle as returned one
    return ang, rtn, rhos, votes, x, BW, H, rho


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
    x1 = int(x0 + 50*(-b))
    y1 = int(y0 + 50*(a))
    x2 = int(x0 - 50*(-b))
    y2 = int(y0 - 50*(a))
    return x1, y1, x2, y2
def draw_lines(img, lines, color=(0, 0, 255)):
    im = pil2cv(img)
    for p1, p2 in lines:
        # print(p1, p2)
        cv2.line(im, p1, p2, color, 1)
    return cv2pil(im)
def red_img_name(idx_str, prefix='./'):
    return prefix + 'red_' + idx_str + '.png'
def change_cur(cur):
    if cur == 'red':
        print('changing to white...')
        time.sleep(1.5)
        print('done')
        return 'white'
    elif cur == 'white':
        print('changing to red2...')
        time.sleep(1.5)
        print('done')
        return 'red2'
    else:
        print('changing to red...')
        time.sleep(1.5)
        print('done')
        return 'red'

def get_angle(r_ang, w_ang, r_rhos, w_rhos, raw_rx, raw_wx, im):
    rhos = [] # 0: white 1: red
    votes = [] # 0: white 1: red
    # white_rho = None
    if abs(r_ang - w_ang) <= 45 or abs(180 - abs(r_ang - w_ang)) <= 45:
        ang = w_ang
        rhos = [w_rhos[0]]
        votes = [w_votes[0]]
        ref = math.radians(raw_wx)
        # white_rho = rho_raw_w
    else:
        ang = w_ang + 90
        raw_wx = raw_wx + 90 if raw_wx < 0 else raw_wx - 90
        rhos = [w_rhos[1]]
        votes = [w_votes[1]]
        ref = raw_wx # + 90 if raw_wx < 0 else raw_wx - 90
        ref = math.radians(ref)
    r_ang, _, r_rhos, r_votes, raw_rx, _, _, _ = calc_angle(im, 'red', ref=ref)
    rhos = rhos + [r_rhos[0]]
    votes = votes + [r_votes[0]]

    assert rhos[0] != [] and rhos[1] != []

    white_rho_blocks = []
    tmp = []
    for rho_i in range(len(rhos[0])):
        r = rhos[0][rho_i]
        v = votes[0][rho_i]
        if v > 8:
            if len(tmp) > 0:
                if abs(r -tmp[-1]) < 2:
                    tmp.append(r)
                else:
                    white_rho_blocks.append(tmp)
                    tmp = []
            else:
                tmp.append(r)
        elif tmp != []:
            white_rho_blocks.append(tmp)
            tmp = []

    red_rho_blocks = []
    tmp = []
    for rho_i in range(len(rhos[1])):
        r = rhos[1][rho_i]
        v = votes[1][rho_i]
        if v > 8:
            if len(tmp) > 0:
                if abs(r -tmp[-1]) < 2:
                    tmp.append(r)
                else:
                    if red_rho_blocks != []:
                        if np.mean(tmp) != np.mean(red_rho_blocks[-1]):
                            red_rho_blocks.append(tmp)
                    else:
                        red_rho_blocks.append(tmp)
                    tmp = []
            else:
                tmp.append(r)
        elif tmp != []:
            if red_rho_blocks != []:
                if np.mean(tmp) != np.mean(red_rho_blocks[-1]):
                    red_rho_blocks.append(tmp)
            else:
                red_rho_blocks.append(tmp)
            tmp = []
   
    min_dists = []
    for w_block in white_rho_blocks:
        for r_block in red_rho_blocks:
            mid_w = (max(w_block)+min(w_block)) / 2
            mid_r = (max(r_block) + min(r_block)) / 2
            if abs(mid_w - mid_r) < 3 and mid_w != mid_r:
                min_dists.append(mid_w - mid_r)
    
    if min_dists == []:
        for w_block in white_rho_blocks:
            for r_block in red_rho_blocks:
                mid_w = min(w_block)
                mid_r = max(r_block)
                if abs(mid_w - mid_r) < 3 and mid_w != mid_r:
                    min_dists.append(mid_w - mid_r)

    assert min_dists != []
    positive = np.mean(min_dists) > 0

    if ang > 180:
        ang -= 180
    ang -= 90
    if ang < 0:
        ang += 180
    theta_positive = raw_wx > 0
    if theta_positive and positive:
        return ang + 180
    elif theta_positive and not positive:
        return ang
    elif not theta_positive and not positive:
        return ang + 180
    elif not theta_positive and positive:
        return ang

def draw_pixel(img, value, i, j):
    img.putpixel((i, j), (value, )*3)
times = 1
pixel_num = 19
line_num = 19
cur = 'red'
img = Image.new("RGB", (line_num * times, pixel_num * times))
collect = 0
ang = None
r_ang, w_ang, r_rhos, w_rhos, raw_rx, raw_wx = None, None, None, None, None, None
plt.ion()
f = plt.figure()
ax = f.add_subplot(111)
while True:
    count = 0
    # cur='red'
    while count < 19 * 19:
        temp = 0
        response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                         bRequest = 0x01,
                         wValue = 0x0000,
                         wIndex = 0x0D, #PIX_GRAB register value
                         data_or_wLength = 1
                         )
        val = int.from_bytes(response,'big')
        i = math.floor(count / 19)
        j = count % 19
        count += 1
        draw_pixel(img, val, i, j)
        time.sleep(0.001)


    if collect != 0:
        collect -= 1
        continue

    ax.imshow(img)
    plt.show()
    plt.pause(1e-6)
    if cur == 'red':
        r_ang, rtn_r, r_rhos, r_votes, raw_rx, b_r, H_r, rho_raw_r = calc_angle(img, 'red')
        cur = change_cur(cur)
        collect = 3
    elif cur == 'red2':
        ang = get_angle(r_ang, w_ang, r_rhos, w_rhos, raw_rx, raw_wx, img)
        collect = 3
        print(ang)
        cur = change_cur(cur)
        input('continue: ')
    else:
        w_ang, rtn_w, w_rhos, w_votes, raw_wx, b_w, H_w, rho_raw_w = calc_angle(img, 'white')
        # ang = get_angle(r_ang, w_ang, r_rhos, w_rhos, raw_rx)
        cur = change_cur(cur)
        collect = 3
        
