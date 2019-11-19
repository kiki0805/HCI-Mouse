from PIL import Image
import numpy as np
file_name = input('file_name: ')
im = Image.open(file_name)
im_arr = np.array(im)
print(im_arr.shape)
for i in range(im.size[1]):
    for j in range(im.size[0]):
        mean = im_arr[i][j].mean()
        im_arr[i][j][0] = mean
        im_arr[i][j][1] = mean
        im_arr[i][j][2] = mean
im_new = Image.fromarray(im_arr)
im_new.save(file_name + '_grey.png')
