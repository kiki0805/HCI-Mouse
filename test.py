from PIL import Image
import numpy as np

# im_arr = np.ones((1080,1080),dtype=np.uint8)
# for i in range(1080):
#     for j in range(1080):
#         if j%2:
#             im_arr[i][j] = 44
#         else:
#             im_arr[i][j] = 255
# # im_arr  = im_arr.astype(np.uint8)
# im = Image.fromarray(im_arr).convert('RGB')
# im.save('test_im.png')

# im_arr = np.ones((1080,1080),dtype=np.uint8)
# for i in range(1080):
#     for j in range(1080):
#         if j%2:
#             im_arr[i][j] = 88
#         else:
#             im_arr[i][j] = 255
# # im_arr  = im_arr.astype(np.uint8)
# im = Image.fromarray(im_arr).convert('RGB')
# im.save('test_im2.png')


# bound pixel to 20-225

# im = Image.open('test.png')
# im_arr = np.array(im)
# x, y, z = im_arr.shape
# for i in range(x):
#     for j in range(y):
#         for n in range(z):
#             im_arr[i][j][n] = 195 * (im_arr[i][j][n] / 255) + 30
# new_im = Image.fromarray(im_arr)
# new_im.save('new_test.png')

im = Image.open('new_test.png')
im_arr = np.array(im)
x, y, z = im_arr.shape
for i in range(x):
    for j in range(y):
        for n in range(z):
            assert im_arr[i][j][n] >= 30 and im_arr[i][j][n] <= 225