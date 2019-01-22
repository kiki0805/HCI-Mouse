from PIL import Image
import numpy as np
import math
file_name = input('file_name: ')
min_v = int(input('min(77): ')) 
max_v = int(input('max(179): '))
im = Image.open(file_name)
im_arr = np.array(im)
print(im_arr.shape)
for i in range(im.size[1]):
    for j in range(im.size[0]):
        for k in range(3):
            # im_arr[i][j][k] = math.ceil(min_v + (max_v - min_v) * im_arr[i][j][k] / 255)
            im_arr[i][j][k] = 0.7 * im_arr[i][j][k]
im_new = Image.fromarray(im_arr)
im_new.save(file_name[:-4] + '_bound_new.png')
