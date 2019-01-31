from PIL import Image, ImageEnhance
from cv2 import cv2
import numpy as np
from sklearn.cluster import KMeans

def pil2cv(im):
    im = np.array(im)
    return cv2.cvtColor(im, cv2.COLOR_RGB2BGR)


def cv2pil(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return Image.fromarray(im)


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


def gaussian_smoothing(img, iteration=100):
    _img = cv2pil(cv2.GaussianBlur(pil2cv(img), (5,5), 0))
    for _ in range(iteration):
        _img = cv2pil(cv2.GaussianBlur(pil2cv(_img), (5, 5), 0))
    return cv2pil(pil2cv(img) - pil2cv(_img) + np.min(_img))


def direct_smooth(img):
    return cv2pil(cv2.GaussianBlur(pil2cv(img), (5,5), 0))


def get_threshold(im, mode):
    ratio = 0.6 if mode == 'white' else 0.6
    # ratio = 0.5 if mode == 'white' else 0.7
    threshold = 10
    im = np.array(im)
    while sum(sum(sum(im > threshold))) > sum(sum(sum(im >= 0))) * ratio:
        threshold += 3
    return threshold


def binirization(im, value):
    im = np.array(im)
    new = im.copy()
    new[im < value] = 0
    new[im >= value] = 255
    return Image.fromarray(new)


def get_edges(im, value):
    im = pil2cv(im)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    new = im.copy()
    new[im < value] = 255
    new[im >= value] = 0
    return new


def remove_end(im, num):
    im = pil2cv(im)
    rows, cols, _ = im.shape
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            same_num = 0
            if im[i][j][0] != 0:
                continue
            for a in [1, -1, 0]:
                for b in [1, -1, 0]:
                    if a == 0 and b == 0:
                        continue
                    if im[i+a][j+b][0] == im[i][j][0]:
                        same_num += 1
            if same_num < num:
                for _ in range(3):
                    im[i][j][_] = 255
    return cv2pil(im)


def preprocessing(im, mode):
    im = gaussian_smoothing(im)
    im = ImageEnhance.Contrast(im).enhance(8)
    # im = ImageEnhance.Contrast(im).enhance(10)
    # im = cv2pil(cv2.blur(pil2cv(im),(5,5)))
    # kernel = np.ones((2, 2), np.uint8)
    # kernel = np.array(((1,1),), np.uint8)
    # im = dilation(im, kernel, 1)
    # kernel = np.array(((1,),(1,)), np.uint8)
    # im = dilation(im, kernel, 1)
    # threshold = get_threshold(im, mode)
    # im = direct_smooth(binirization(im, threshold))
    threshold = get_threshold(im, mode)
    # if mode == 'red':
    #     im = remove_end(binirization(im, threshold), num=4)
    # else:
    #     im = remove_end(binirization(im, threshold), num=3)
    # im = remove_end(im)
    # im = cv2pil(cv2.fastNlMeansDenoisingColored(pil2cv(binirization(im, threshold)), None, 2, 2, 7, 10))
    return binirization(im, threshold), get_edges(im, threshold)
    # return im, get_edges(im, threshold)

def output(arr, mean1, mean2, str_):
    num1 = 0
    num2 = 0
    block_num = 0
    last = None
    for i in arr:
        if block_num == 0:
            block_num += 1
        if abs(i - mean1) < abs(i - mean2):
            num1 += 1
            if last is not None:
                if last != '1':
                    block_num += 1
            last = '1'
        else:
            num2 += 1
            if last is not None:
                if last != '2':
                    block_num += 1
            last = '2'
    # print(str_, num1, num2)
    # print('block num', block_num)
    # print()
    return block_num


def calc_border_pct(img, mode):
    im = np.array(img.convert('L'))
    rows, cols = im.shape
    # left_col = im[:,0].reshape(-1, 1)
    # right_col = im[:,cols-1].reshape(-1, 1)
    # above_row = im[0,:].reshape(-1, 1)
    # below_row = im[rows-1,:].reshape(-1, 1)
    i_left, i_right, i_above, i_below = 0, cols-1, 0, rows-1
    left_col = im[:,i_left]
    right_col = im[:,i_right]
    above_row = im[i_above,:]
    below_row = im[i_below,:]

    imr = im.reshape(-1, 1)
    overall_km = KMeans(n_clusters=2).fit(imr)
    pixels1 = imr[np.where(overall_km.labels_==0)]
    pixels2 = imr[np.where(overall_km.labels_==1)]
    # print(np.mean(pixels1), np.mean(pixels2))
    mean1, mean2 = overall_km.cluster_centers_
    mean1 = mean1[0]
    mean2 = mean2[0]

    above_num = output(above_row, mean1, mean2, '↑')
    below_num = output(below_row, mean1, mean2, '↓')
    left_num = output(left_col, mean1, mean2, '←')
    right_num = output(right_col, mean1, mean2, '→')

    nice_count = (above_num >= 7) + (below_num >= 7) + (left_num >= 7) + (right_num >= 7)
    if mode == 'red':
        goal = 2
    elif mode == 'white':
        goal = 3
    block_goal = 7
    block_goal1 = 7
    block_goal2 = 7
    while nice_count < goal:
        if not (above_num < block_goal1 and abs(i_above - i_below) != 1) and \
                not (below_num < block_goal1 and abs(i_above - i_below) != 1) and \
                not (left_num < block_goal2 and abs(i_left - i_right) != 1) and \
                not (right_num < block_goal2 and abs(i_left - i_right) != 1):
            print()
            print(mode, 'FAIL TO REACH GOAL')
            print(above_num, below_num, left_num, right_num)
            print()
            nums = (above_num, below_num, left_num, right_num)
            indexes = (i_above, i_below, i_left, i_right)
            return False, cv2pil(pil2cv(img)[i_left:i_right, i_above:i_below]), \
                nums, np.mean(overall_km.cluster_centers_), indexes
        if above_num < block_goal1 and abs(i_above - i_below) != 1:
            i_above += 1
            above_row = im[i_above,:]
            above_num = output(above_row, mean1, mean2, '↑')
        if below_num < block_goal1 and abs(i_above - i_below) != 1:
            i_below -= 1
            below_row = im[i_below,:]
            below_num = output(below_row, mean1, mean2, '↓')
        if left_num < block_goal2 and abs(i_left - i_right) != 1:
            i_left += 1
            left_col = im[:,i_left]
            left_num = output(left_col, mean1, mean2, '←')
        if right_num < block_goal2 and abs(i_left - i_right) != 1:
            i_right -= 1
            right_col = im[:,i_right]
            right_num = output(right_col, mean1, mean2, '→')
        diff1 = abs(i_above - 0) + abs(i_below - rows + 1)
        diff2 = abs(i_left - 0) + abs(i_right - cols + 1)
        block_goal1 = 7 - diff2 / (19 / 7)
        block_goal2 = 7 - diff1 / (19 / 7)
        nice_count = (above_num >= block_goal1) + (below_num >= block_goal1) \
                + (left_num >= block_goal2) + (right_num >= block_goal2)
        # print('current block goal:', block_goal)

    print(above_num, below_num, left_num, right_num)
    nums = (above_num, below_num, left_num, right_num)
    indexes = (i_above, i_below, i_left, i_right)
    return True, cv2pil(pil2cv(img)[i_left:i_right, i_above:i_below]), \
        nums, np.mean(overall_km.cluster_centers_), indexes


def find_intervals():
    pass


def dot_keypoints(im, nums, mode, tsh, indexes):
    # tsh < 128
    im_colord = pil2cv(im)
    rows, cols, _ = im_colord.shape
    im_arr = cv2.cvtColor(pil2cv(im), cv2.COLOR_BGR2GRAY)
    above, below, left, right = nums
    i_a, i_b, i_l, i_r = indexes
    interval = [None, None]
    last = None
    print(7 - (abs(i_l - 0) + abs(i_r - 18)) / (19 / 7))
    draw_count = 0
    abovepoints = []
    belowpoints = []
    leftpoints = []
    rightpoints = []
    ################# ABOVE
    if above >= 7 - (abs(i_l - 0) + abs(i_r - 18)) / (19 / 7):
    # if above >= 6:
        above_arr = im_arr[0,:]
        km = KMeans(n_clusters=2).fit(above_arr.reshape(-1, 1))
        above_rst = above_arr > tsh
        mid_mean = tsh
        # print(above_rst)
        for i in range(len(above_rst)):
            cur = above_rst[i]
            if last is not None:
                if last == cur:
                    interval[1] = i
                else:
                    interval[1] = i - 1
                    if im_arr[0][int(np.mean(interval))] < 128 and interval[1] - interval[0] < 4:
                        # print(im_arr[0][int(np.mean(interval))])
                        draw_count += 1
                        abovepoints.append((0, int(np.mean(interval))))
                        # im_colord[0][int(np.mean(interval))][0] = 0
                        # im_colord[0][int(np.mean(interval))][1] = 0
                        # im_colord[0][int(np.mean(interval))][2] = 255
                    interval[0] = i
            else:
                interval[0] = i
            last = cur
    ################## BELOW
    if below >= 7 - (abs(i_l - 0) + abs(i_r - 18)) / (19 / 7):
    # if above >= 6:
        above_arr = im_arr[-1,:]
        km = KMeans(n_clusters=2).fit(above_arr.reshape(-1, 1))
        above_rst = above_arr > tsh
        mid_mean = tsh
        # print(above_rst)
        for i in range(len(above_rst)):
            cur = above_rst[i]
            if last is not None:
                if last == cur:
                    interval[1] = i
                else:
                    interval[1] = i - 1
                    if im_arr[-1][int(np.mean(interval))] < 128:
                        # print(im_arr[0][int(np.mean(interval))])
                        draw_count += 1
                        belowpoints.append((rows - 1, int(np.mean(interval))))
                        # im_colord[-1][int(np.mean(interval))][0] = 0
                        # im_colord[-1][int(np.mean(interval))][1] = 255
                        # im_colord[-1][int(np.mean(interval))][2] = 0
                    interval[0] = i
            else:
                interval[0] = i
            last = cur
    ############### LEFT
    if left >= 7 - (abs(i_a - 0) + abs(i_b - 18)) / (19 / 7):
    # if above >= 6:
        above_arr = im_arr[:,0]
        km = KMeans(n_clusters=2).fit(above_arr.reshape(-1, 1))
        above_rst = above_arr > tsh
        mid_mean = tsh
        # print(above_rst)
        for i in range(len(above_rst)):
            cur = above_rst[i]
            if last is not None:
                if last == cur:
                    interval[1] = i
                else:
                    interval[1] = i - 1
                    if im_arr[int(np.mean(interval))][0] < 128:
                        # print(im_arr[0][int(np.mean(interval))])
                        leftpoints.append((int(np.mean(interval)), 0))
                        draw_count += 1
                        # im_colord[int(np.mean(interval))][0][0] = 255
                        # im_colord[int(np.mean(interval))][0][1] = 0
                        # im_colord[int(np.mean(interval))][0][2] = 0
                    interval[0] = i
            else:
                interval[0] = i
            last = cur
    
    ########### RIGHT
    ############### LEFT
    if right >= 7 - (abs(i_a - 0) + abs(i_b - 18)) / (19 / 7):
    # if above >= 6:
        above_arr = im_arr[:,-1]
        km = KMeans(n_clusters=2).fit(above_arr.reshape(-1, 1))
        above_rst = above_arr > tsh
        mid_mean = tsh
        # print(above_rst)
        for i in range(len(above_rst)):
            cur = above_rst[i]
            if last is not None:
                if last == cur:
                    interval[1] = i
                else:
                    interval[1] = i - 1
                    if im_arr[int(np.mean(interval))][-1] < 128:
                        # print(im_arr[0][int(np.mean(interval))])
                        rightpoints.append((int(np.mean(interval)), cols - 1))
                        draw_count += 1
                        # im_colord[int(np.mean(interval))][-1][0] = 0
                        # im_colord[int(np.mean(interval))][-1][1] = 255
                        # im_colord[int(np.mean(interval))][-1][2] = 255
                    interval[0] = i
            else:
                interval[0] = i
            last = cur


    if draw_count >= 2:
        return cv2pil(im_colord), (abovepoints, belowpoints, leftpoints, rightpoints)
    return im, (abovepoints, belowpoints, leftpoints, rightpoints)
                    





if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from static_utils import get_imgs, img_name, change_mode
    fig = plt.figure()
    before_ax = fig.add_subplot(211)
    after_ax = fig.add_subplot(212)
    plt.ion()

    imgs = get_imgs()
    # imgs = ['138', '224', '225', '226', '227', '315', '317']
    # imgs = ['94'] #['138', '224', '225', '226', '227', '315', '317']
    tmp = []
    for img in imgs:
        fig.suptitle('Angle: ' + img)
        for mode in ['red', 'white']:
            before_img = Image.open(img_name(img, mode))
            before_ax.imshow(before_img)
            after_img, _ = preprocessing(before_img, mode)
            rtn, im, nums, tsh, indexes = calc_border_pct(after_img, mode)
            im, points = dot_keypoints(im, nums, mode, tsh, indexes)
            if not rtn:
                print('value', img)
                tmp.append(img)
            after_ax.imshow(im)
            plt.show()
            plt.pause(1)

    print(tmp)