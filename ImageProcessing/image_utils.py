import numpy as np
from color_space_utils import *
from PIL import Image
import math

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

def update_img(img, chang_matrix):
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
    
    new_im = np.array(img)
    new_im2 = np.array(img)
    for i in range(new_im.shape[0]):
        for j in range(new_im.shape[1]):
            if chang_matrix[i][j] == 0:
                continue
            new_im[i][j][0] = max(0, int(new_im[i][j][0] * (1 - chang_matrix[i][j])))
            new_im[i][j][1] = max(0, int(new_im[i][j][1] * (1 - chang_matrix[i][j])))
            new_im[i][j][2] = max(0, int(new_im[i][j][2] * (1 - chang_matrix[i][j])))

            new_im2[i][j][0] = min(int(new_im2[i][j][0] * (1 + chang_matrix[i][j])), 255)
            new_im2[i][j][1] = min(int(new_im2[i][j][1] * (1 + chang_matrix[i][j])), 255)
            new_im2[i][j][2] = min(int(new_im2[i][j][2] * (1 + chang_matrix[i][j])), 255)
    return Image.fromarray(new_im), Image.fromarray(new_im2)

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

size = (300, 300)
cut = (0, 0, size[1], size[0] / 2)
im = read_resize_img('test-0.png', size)
# ch_mat = get_delta_lightness(im, 2)
ch_mat = get_translucency(im, cut)
new_im, new_im2 = update_img(im, ch_mat)
# new_im.save('test_0_new.png')
# new_im2.save('test_0_new2.png')
write_to_file(new_im, '../openGL/new_im')
write_to_file(new_im2, '../openGL/new_im2')

# Lab_v = convert_RGB2Lab(RGBValue(RGB=(1, 1, 1)))
# print(Lab_v.L, Lab_v.a, Lab_v.b)