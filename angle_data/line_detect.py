from bresenham import bresenham
from cv2 import cv2
import numpy as np
import math
from preprocessing import pil2cv, cv2pil
from sklearn.cluster import KMeans
import itertools


def convert3sets21sets(sets):
    assert len(sets) == 3
    lens = []
    for s in sets:
        lens.append(len(s))
    longest = lens.index(max(lens))
    return (sets[longest], )


def convert3sets22sets(sets):
    assert len(sets) == 3
    means = []
    for s in sets:
        means.append(np.mean(s))
    min_index = means.index(min(means))
    max_index = means.index(max(means))
    assert min_index != max_index
    new_set = [i - 180 for i in sets[max_index]]
    remained_index = 3 - min_index - max_index
    return (sets[min_index] + new_set, sets[remained_index])


# return number of sets, and sets tuple
def get_one_or_two_sets(angles):
    angles = np.array(angles)
    angles = angles.reshape(-1,1)

    result = KMeans(n_clusters=2).fit(angles)
    set0 = angles[np.where(result.labels_==0)]
    set1 = angles[np.where(result.labels_==1)]
    mean0 = np.mean(set0)
    mean1 = np.mean(set1)
    if angle_in_range(abs(mean0 - mean1), 90, diff=math.degrees(3/19)):
        return 2, (set0.reshape(1, -1).tolist()[0], set1.reshape(1, -1).tolist()[0])
    if angle_in_range(abs(mean0 - mean1), 180, diff=math.degrees(3/19)) or \
            angle_in_range(abs(mean0 - mean1), 0, diff=math.degrees(3/19)):
        return 1, (set0.reshape(1, -1).tolist()[0] + set1.reshape(1, -1).tolist()[0], )
    
    result = KMeans(n_clusters=3).fit(angles)
    set0 = angles[np.where(result.labels_==0)]
    set1 = angles[np.where(result.labels_==1)]
    set2 = angles[np.where(result.labels_==2)]
    mean0 = np.mean(set0)
    mean1 = np.mean(set1)
    mean2 = np.mean(set2)

    if_2_sets = False
    if angle_in_range(abs(mean0 - mean1), 90, diff=math.degrees(3/19)) and \
            angle_in_range(abs(mean2 - mean1), 90, diff=math.degrees(3/19)):
        if_2_sets = True
    if angle_in_range(abs(mean0 - mean2), 90, diff=math.degrees(3/19)) and \
            angle_in_range(abs(mean2 - mean1), 90, diff=math.degrees(3/19)):
        if_2_sets = True
    if angle_in_range(abs(mean0 - mean1), 90, diff=math.degrees(3/19)) and \
            angle_in_range(abs(mean2 - mean0), 90, diff=math.degrees(3/19)):
        if_2_sets = True
    if if_2_sets:
        s = convert3sets22sets((set0.reshape(1, -1).tolist()[0], \
            set1.reshape(1, -1).tolist()[0], \
            set2.reshape(1, -1).tolist()[0]))
        return 2, s

    s = convert3sets21sets((set0.reshape(1, -1).tolist()[0], \
        set1.reshape(1, -1).tolist()[0], set2.reshape(1, -1).tolist()[0],))
    return 1, s


def angle_in_range(angle, ref, verticle=False, diff=math.degrees(1/19)):
    if abs(ref - angle) <= diff:
        return True
    if verticle and abs(90 - abs(ref - angle)) <= diff:
        return True
    return False


def calc_angle(x1, y1, x2, y2):
    angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    angle += 90
    if angle < 0:
        angle += 360
    if angle > 360:
        angle -= 360
    if angle > 180:
        angle -= 180
    return angle


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


def line_detect(img, edges, vote=15):
    # edges = pil2cv(edges)
    img = pil2cv(edges)
    lines = cv2.HoughLines(edges, 1, np.pi/180, vote)
    assert lines is not None
    angles = []
    lines_rmd = []
    for line in lines[:10]:
        rho, theta = line[0]
        if angle_in_range(math.degrees(theta), 45, verticle=True, diff=0.1):
            continue
        x1, y1, x2, y2 = calc_points(rho, theta)
        angle = calc_angle(x1, y1, x2, y2)
        angles.append(angle)
        lines_rmd.append(((x1, y1), (x2, y2)))
        
    return get_one_or_two_sets(angles), lines_rmd


def calc_compatibility(img, lines):
    im_arr = np.array(img)
    compatibility = {}
    for p1, p2 in lines:
        detailed_line = list(bresenham(*(p1 + p2)))
        val = []
        for point in detailed_line:
            if point[0] < 0 or point[0] >= 19 or point[1] < 0 or point[1] >= 19:
                continue
            val.append(im_arr[point[0]][point[1]])
        compatibility[(p1, p2)] = np.mean(val)
    return compatibility


def find_best_line(im, points):
    # points1, points2, points3, points4 = points
    lines = []
    for i in range(len(points)):
        for j in range(len(points)):
            if i == j or points[i] == [] or points[j] == []:
                continue
            lines += list(itertools.product(points[i], points[j]))

    comp = calc_compatibility(im, lines)
    comp_sorted = sorted(comp.items(), key=lambda kv: kv[1])
    # after_img = draw_lines(im, comp.keys(), color=(255, 0, 0))
    after_img = draw_lines(im, (comp_sorted[0][0],))
    print(comp_sorted[0][0])
    return after_img, comp_sorted[0][0]

def draw_lines(img, lines, color=(0, 0, 255)):
    im = pil2cv(img)
    for p1, p2 in lines:
        cv2.line(im, p1, p2, color, 1)
    return cv2pil(im)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from static_utils import get_imgs, img_name, change_mode
    from preprocessing import preprocessing, get_edges, calc_border_pct, dot_keypoints
    from PIL import Image
    fig = plt.figure()
    before_ax = fig.add_subplot(211)
    after_ax = fig.add_subplot(212)
    plt.ion()

    imgs = get_imgs()
    wrong = []
    tag = None
    large_error = []
    for img in imgs:
        print('correct:', img)
        diff = 999
        fig.suptitle('Angle: ' + img)
        for mode in ['red', 'white']:
            # before_img = Image.open(img_name(img, mode))
            # before_ax.imshow(before_img)
            # after_img, _ = preprocessing(before_img, mode)
            # rtn, im, nums, tsh, indexes = calc_border_pct(after_img, mode)
            # im, points = dot_keypoints(im, nums, mode, tsh, indexes)
            # cut_im = cv2pil(pil2cv(before_img)[indexes[2]:indexes[3],indexes[0]:indexes[1]])
            # after_img, best_line = find_best_line(cut_im, points)
            # after_ax.imshow(after_img)
            # plt.show()
            # plt.pause(1)

        ##############################################################
            before_img = Image.open(img_name(img, mode))
            processed, edges = preprocessing(before_img, mode)
            before_ax.imshow(processed)
            (set_num, sets), lines = line_detect(before_img, edges)
            ###############################################################################
            # comp = calc_compatibility(before_img, lines)
            # comp_sorted = sorted(comp.items(), key=lambda kv: kv[1])
            # # print(comp_sorted[0][0])
            # after_img = draw_lines(before_img, comp.keys(), color=(255, 0, 0))
            # after_img = draw_lines(after_img, (comp_sorted[0][0],))
            # print(comp_sorted[0][1])
            # after_ax.imshow(after_img)
            # plt.show()
            # plt.pause(1)
            ##########################################################################3
            for s in sets:
                for ang in s:
                    if abs(int(img) - ang) < diff:
                        diff = abs(int(img) - ang)
                        tag = ang
                # print(s)
            # print()
            if mode == 'red' and set_num != 1:
                print('WRONG ' + mode, end=' ')
                wrong.append(img)
                print(img, set_num)
                print(sets)
                print()
            if mode == 'white' and set_num != 2:
                print('WRONG ' + mode, end=' ')
                wrong.append(img)
                print(img, set_num)
                print(sets)
                print()
        #     after_img = draw_lines(before_img, lines)
        #     after_ax.imshow(after_img)
        #     # plt.show()
        #     # plt.pause(1)
        if not angle_in_range(diff, 0, verticle=True, diff=math.degrees(3/19)) and \
            not angle_in_range(diff, 90, verticle=True, diff=math.degrees(3/19)) and \
            not angle_in_range(diff, 180, verticle=True, diff=math.degrees(3/19)):
                if img not in large_error:
                    large_error.append(img)
                print('diff:', diff)
                print('detected:', tag)
    print('wrong(' + str(len(wrong)) + '):', wrong)
    print('large_error(' + str(len(large_error)) + '):', large_error)
