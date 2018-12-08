import numpy as np
from color_space_utils import *
from PIL import Image
import math

LOW_PREFER_COLOR_AREA = []
HIGH_PERFER_COLOR_AREA = []

def in_area(area, pixel_RGB):
    # area: ((r,g,b),(r,g,b))
    if pixel_RGB[0] < area[0][0] or pixel_RGB[0] > area[1][0]:
        return False
    if pixel_RGB[1] < area[0][1] or pixel_RGB[1] > area[1][1]:
        return False
    if pixel_RGB[2] < area[0][2] or pixel_RGB[2] > area[1][2]:
        return False
    return True

def bind_colors(im):
    # 64 - 192
    span = 255 * 0.25
    im_arr = np.array(im)
    r, c, n = im_arr.shape
    for i in range(r):
        for j in range(c):
            im_arr[i][j][0] = int((205 - 50) * (im_arr[i][j][0] / 255) + 50)
            im_arr[i][j][1] = int((255 - 2 * span) * (im_arr[i][j][1] / 255) + span)
            # im_arr[i][j][0] = int((255 - 2 * span) * (im_arr[i][j][0] / 255) + span)
            # if im_arr[i][j][0] <= 63 or im_arr[i][j][0] >= 193 or \
            #     im_arr[i][j][1] <= 63 or im_arr[i][j][1] >= 193 or \
            #     im_arr[i][j][2] <= 63 or im_arr[i][j][2] >= 193:
            #     for k in range(3):
            #         im_arr[i][j][k] = int((255 - 2 * span) * (im_arr[i][j][k] / 255) + span)
    return Image.fromarray(im_arr)

def get_best_colors(RGB_color):
    # min_diff = min(255-RGB_color[1],RGB_color[1]-0)
    # return (RGB_color[0], RGB_color[1] - min_diff, RGB_color[2]), \
    #     (RGB_color[0], RGB_color[1] + min_diff, RGB_color[2])

    # min_diff = min(255-RGB_color[0],RGB_color[0]-0)
    # return (RGB_color[0] - min_diff, RGB_color[1], RGB_color[2]), \
    #     (RGB_color[0] + min_diff, RGB_color[1], RGB_color[2])

    # min_diff = min(255-RGB_color[2],RGB_color[2]-0)
    # return (RGB_color[0], RGB_color[1], RGB_color[2] - min_diff), \
    #     (RGB_color[0], RGB_color[1], RGB_color[2] + min_diff)

    min_diff = min([255-RGB_color[2],RGB_color[2]-0,255-RGB_color[0],\
        RGB_color[0]-0,255-RGB_color[1],RGB_color[1]-0])
    return (RGB_color[0] - min_diff, RGB_color[1]- min_diff, RGB_color[2] - min_diff), \
        (RGB_color[0] + min_diff, RGB_color[1]+ min_diff, RGB_color[2] + min_diff)

def read_resize_img(img_name, size):
    from PIL import Image
    img = Image.open(img_name)
    img = img.resize(size)
    return img

def change_fixed_lightness(img):
    pass

def get_texture_matrix(img, cut_area=None):
    pass

def get_delta_lightness(img, color_diff, cut_area=None):
    # color diff: [2, 3]
    # cut_area: [x0, y0, x1, y1]
    im_arr = np.array(img)
    l_arr = np.zeros((im_arr.shape[0], im_arr.shape[1]))
    r, c, _ = im_arr.shape
    for i in range(r):
        if cut_area:
            if i < cut_area[0] or i >= cut_area[2]:
                continue
        for j in range(c):
            if cut_area:
                if j < cut_area[2] or j >= cut_area[3]:
                    continue
            RGB_ij = RGBValue(RGB=im_arr[i][j])
            Lab_ij = convert_RGB2Lab(RGB_ij)
            l_arr[i][j] = (1 + (0.015 * pow(Lab_ij.L - 50.0, 2)) / \
                (math.sqrt(20 + pow(Lab_ij.L - 50.0, 2)))) * color_diff
    return l_arr

def get_translucency(img, cut_area=None):
    # color diff: [2, 3]
    # cut_area: [x0, y0, x1, y1]
    im_arr = np.array(img)
    trans_arr = np.zeros((im_arr.shape[0], im_arr.shape[1]))
    r, c, _ = im_arr.shape
    for i in range(r):
        if cut_area:
            if i < cut_area[0] or i >= cut_area[2]:
                continue
        for j in range(c):
            if cut_area:
                if j < cut_area[1] or j >= cut_area[3]:
                    continue
            intensity = im_arr[i][j].mean()
            # trans_arr[i][j] = 0.3
            if intensity <= 79:
                trans_arr[i][j] = 0.12
            elif intensity >= 170:
                trans_arr[i][j] = 0.05
            else:
                trans_arr[i][j] = 0.07
    return trans_arr

def get_complement_imgs(img,cut_area=None):
    # cut_area: [x0, y0, x1, y1]
    im_arr = np.array(img)
    r, c, n = im_arr.shape
    im_arr1 = np.array(img)
    im_arr2 = np.array(img)
    for i in range(r):
        if cut_area:
            if i < cut_area[0] or i >= cut_area[2]:
                continue
        for j in range(c):
            if cut_area:
                if j < cut_area[1] or j >= cut_area[3]:
                    continue
            color1, color2 = get_best_colors((im_arr[i][j][0], im_arr[i][j][1], im_arr[i][j][2]))
            im_arr1[i][j][0] = color1[0]
            im_arr1[i][j][1] = color1[1]
            im_arr1[i][j][2] = color1[2]
            im_arr2[i][j][0] = color2[0]
            im_arr2[i][j][1] = color2[1]
            im_arr2[i][j][2] = color2[2]
            # sR = im_arr[i][j][0] / 255
            # sG = im_arr[i][j][1] / 255
            # sB = im_arr[i][j][2] / 255
            # if intensity <= 79:
            #     trans_arr[i][j] = 0.12
            # elif intensity >= 170:
            #     trans_arr[i][j] = 0.05
            # else:
            #     trans_arr[i][j] = 0.07
    return Image.fromarray(im_arr1), Image.fromarray(im_arr2)

def update_img(img, chang_matrix):
    pass
    ############# change delta lightness
    # new_im = np.array(img)
    # for i in range(new_im.shape[0]):
    #     for j in range(new_im.shape[1]):
    #         RGB_ij = RGBValue(RGB=new_im[i][j])
    #         Lab_ij = convert_RGB2Lab(RGB_ij)
    #         Lab_ij.L += chang_matrix[i][j]
    #         # print(chang_matrix[i][j])
    #         new_RGB_ij = convert_Lab2RGB(Lab_ij)
    #         new_im[i][j] = np.array([new_RGB_ij.R, new_RGB_ij.G, new_RGB_ij.B])
    # new_im2 = np.array(img)
    # for i in range(new_im2.shape[0]):
    #     for j in range(new_im2.shape[1]):
    #         RGB_ij = RGBValue(RGB=new_im2[i][j])
    #         Lab_ij = convert_RGB2Lab(RGB_ij)
    #         Lab_ij.L -= chang_matrix[i][j]
    #         # print(chang_matrix[i][j])
    #         new_RGB_ij = convert_Lab2RGB(Lab_ij)
    #         new_im2[i][j] = np.array([new_RGB_ij.R, new_RGB_ij.G, new_RGB_ij.B])
    # return Image.fromarray(new_im), Image.fromarray(new_im2)
    

    ################# change translucency
    # new_im = np.array(img)
    # new_im2 = np.array(img)
    # for i in range(new_im.shape[0]):
    #     for j in range(new_im.shape[1]):
    #         if chang_matrix[i][j] == 0:
    #             continue
    #         new_im[i][j][0] = max(0, int(new_im[i][j][0] * (1 - chang_matrix[i][j])))
    #         new_im[i][j][1] = max(0, int(new_im[i][j][1] * (1 - chang_matrix[i][j])))
    #         new_im[i][j][2] = max(0, int(new_im[i][j][2] * (1 - chang_matrix[i][j])))

    #         new_im2[i][j][0] = min(int(new_im2[i][j][0] * (1 + chang_matrix[i][j])), 255)
    #         new_im2[i][j][1] = min(int(new_im2[i][j][1] * (1 + chang_matrix[i][j])), 255)
    #         new_im2[i][j][2] = min(int(new_im2[i][j][2] * (1 + chang_matrix[i][j])), 255)
    # return Image.fromarray(new_im), Image.fromarray(new_im2)

def write_to_file(img, name):
    # 16bit x, 16bit y
    # 8bit R 8bit G 8bit B
    import struct
    im_arr = np.array(img)
    r, c, _ = im_arr.shape
    with open(name, 'wb') as f:
        count = 0
        for i in range(r):
            for j in range(c):
                for k in range(3):
                    f.write(struct.pack('B', im_arr[i][j][k]))
                    # print(count, im_arr[i][j][k])
                    count += 1

# size = (300, 300)
# cut = (0, 0, size[1], size[0] / 2)
im = read_resize_img('test-0.png', (1080, 1080))
new_im = bind_colors(im)
im1, im2 = get_complement_imgs(new_im)
new_im.save('new.png')
im1.save('im1.png')
im2.save('im2.png')
# delta_lightness
# ch_mat = get_delta_lightness(im, 2)

# translucency
# ch_mat = get_translucency(im, cut)
# new_im, new_im2 = update_img(im, ch_mat)
# new_im.save('test_0_new.png')
# new_im2.save('test_0_new2.png')
write_to_file(im1, '../openGL/new_im_1080_rgb')
write_to_file(im2, '../openGL/new_im2_1080_rgb')

# Lab_v = convert_RGB2Lab(RGBValue(RGB=(1, 1, 1)))
# print(Lab_v.L, Lab_v.a, Lab_v.b)