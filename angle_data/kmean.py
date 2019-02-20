
import os
import numpy as np
from skimage.transform import hough_line, hough_line_peaks
from PIL import Image, ImageEnhance
import math
from cv2 import cv2
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt
import collections
from sklearn.cluster import KMeans

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

def erode(img, kernel, iterations):
    img = cv2.erode(img,kernel,iterations = iterations)
    return img
def get_threshold(im, ratio=0.8):
    # ratio = 0.5 if mode == 'white' else 0.7
    threshold = 3
    im = np.array(im)
    while sum(sum(im > threshold)) > sum(sum(im >= 0)) * ratio:
        threshold += 1
    return threshold
def closing(img, kernel):
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    return img
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

fig = plt.figure()
ax = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)
plt.ion()
imgs_val = get_imgs()
# imgs_val = ['130','135','138','140']
imgs_val = ['135']
t=[]

d=[]
c=[0, 0, 0, 0]
for i in imgs_val:
    r_im = Image.open(red_img_name(i))
    w_im = Image.open(white_img_name(i))
    # r_im = Image.open('test_r.png')
    # w_im = Image.open('test_w.png')
    r_ang, rtn_r, r_rhos, r_votes, raw_rx, b_r, H_r, rho_raw_r = calc_angle(r_im, 'red')
    w_ang, rtn_w, w_rhos, w_votes, raw_wx, b_w, H_w, rho_raw_w = calc_angle(w_im, 'white')
    
    
    # points = calc_points(r)
    # ax.imshow(rtn)
    # plt.show()
    # plt.pause(3)
#     ax3.imshow(b_r)
#     ax4.imshow(b_w)
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
    r_ang, rtn_r, r_rhos, r_votes, raw_rx, b_r, H_r, rho_raw_r = calc_angle(r_im, 'red', ref=ref)
    rhos = rhos + [r_rhos[0]]
    votes = votes + [r_votes[0]]
    # print(rhos, votes)

    assert rhos[0] != [] and rhos[1] != []

    white_rho_blocks = []
    tmp = []
    for rho_i in range(len(rhos[0])):
        # vs = list(dic_white.keys())
        # rs = list(dic_white.values())
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
        # vs = list(dic_white.keys())
        # rs = list(dic_white.values())
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
    mid_r_record = None
    mid_w_record = None
    for w_block in white_rho_blocks:
        for r_block in red_rho_blocks:
            mid_w = (max(w_block)+min(w_block)) / 2
            mid_r = (max(r_block) + min(r_block)) / 2
            # mid_w = min(w_block)
            # mid_r = max(r_block)
            if abs(mid_w - mid_r) < 3 and mid_w != mid_r:
                min_dists.append(mid_w - mid_r)
    
    # continue
    if min_dists == []:
        for w_block in white_rho_blocks:
            for r_block in red_rho_blocks:
                # mid_w = (max(w_block)+min(w_block)) / 2
                # mid_r = (max(r_block) + min(r_block)) / 2
                mid_w = min(w_block)
                mid_r = max(r_block)
                if abs(mid_w - mid_r) < 3 and mid_w != mid_r:
                    min_dists.append(mid_w - mid_r)
    print('white blocks:', white_rho_blocks)
    print('red blocks:', red_rho_blocks)
    print(min_dists)
    print()

    assert min_dists != []
    abs_min_dists = [abs(i) for i in min_dists]
    # min_abs = min(abs_min_dists)
    # if min_abs < 2:
    #     for ele in min_dists:
    #         if abs(ele) > 2:
    #             min_dists.remove(ele)
    # abs_min_dists = [abs(i) for i in min_dists]
    positive_num, negative_num = 0, 0
    for num in min_dists:
        if num > 0:
            positive_num += 1
        else:
            negative_num += 1
    # if abs(positive_num - negative_num) == 0:
    #     min_index = abs_min_dists.index(min(abs_min_dists))
    #     positive = min_dists[min_index] > 0
    # else:
    # print(min_dists)
    positive = np.mean(min_dists) > 0
    # if white_rho is None:
    #     max_index = votes[0].index(max(votes[0]))
    #     white_rho = rhos[0][max_index]

    # red_rho = []
    # for rho_i in range(len(rhos[1])):
    #     r = rhos[1][rho_i]
    #     if abs(r - white_rho) < 1.5 and r * white_rho > 0:
    #         red_rho.append(r)
    #         print(votes[1][rho_i])

    # if red_rho == []:
    #     for white_rho in rhos[0]:
    #         red_rho = []
    #         for rho_i in range(len(rhos[1])):
    #             r = rhos[1][rho_i]
    #             if abs(r - white_rho) < 1.5 and r * white_rho > 0:
    #                 red_rho.append(r)
    #         if len(red_rho) > 1:
    #             print(votes[1][rho_i])
    #             break
    # red_rho = (max(red_rho) + min(red_rho)) / 2
    # points = calc_points(red_rho, math.radians(raw_rx))
    # red_drawed = draw_lines(Image.fromarray(b_r*255).convert('RGB'), (((points[0], points[1]), (points[2], points[3])),))
    # points = calc_points(white_rho, math.radians(raw_rx))
    # white_drawed = draw_lines(Image.fromarray(b_w*255).convert('RGB'), (((points[0], points[1]), (points[2], points[3])),))


    if ang > 180:
        ang -= 180
    ang -= 90
    if ang < 0:
        ang += 180
    # positive = white_rho - red_rho > 0
    theta_positive = raw_wx > 0
    print(positive, theta_positive, int(i), ang, raw_wx)
    error = False
    if theta_positive and positive:
        assert1 = abs(180 - abs(int(i) - ang)) < 10
        if assert1:
            c[0] += 1
        else:
            # print(i)
            error = True
            
    elif theta_positive and not positive:
        assert2 = abs(int(i) - ang) < 10
        if assert2:
            c[1] += 1
        else:
            error = True
    elif not theta_positive and not positive:
        assert1 = abs(180 - abs(int(i) - ang)) < 10
        if assert1:
            c[2] += 1
        else:
            # print(i)
            error = True
            
    elif not theta_positive and positive:
        assert2 = abs(int(i) - ang) < 10
        if assert2:
            c[3] += 1
        else:
            error = True
    # else:
    #     c+=1
    # elif (not theta_positive) and not positive:

    #temp
    ax.imshow(H_r)
    ax2.imshow(H_w)
    ax3.imshow(rtn_r)
    ax4.imshow(rtn_w)
    plt.show()
    plt.pause(3)
    input()

    if error:
        t.append(int(i))
        ax.imshow(H_r)
        ax2.imshow(H_w)
        ax3.imshow(rtn_r)
        ax4.imshow(rtn_w)
        plt.show()
        plt.pause(3)
        input()
print(len(t))
print(c)
print(sum(c))
print('error list:', t)
