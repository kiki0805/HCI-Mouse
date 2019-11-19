import numpy as np
from PIL import Image
im = np.zeros((1366, 768, 3))
for i in range(1366):
    for j in range(768):
        im[i][j][0] = 128
        im[i][j][1] = 128
        im[i][j][2] = 128
        # if i%3==0 and j%3==0:
        #     im[i][j][0] = 255
        #     im[i][j][1] = 0
        #     im[i][j][2] = 0
        #     # for k in range(3):
        #     #     im[i][j][k] = 128
        # elif i%3==0 and j%3==1:
        #     # for k in range(3):
        #     #     im[i][j][k] = 128
        #     im[i][j][0] = 255
        #     im[i][j][1] = 0
        #     im[i][j][2] = 0
        # elif i%3==1 and j%3==0:
        #     # for k in range(3):
        #     #     im[i][j][k] = 128
        #     im[i][j][0] = 255
        #     im[i][j][1] = 0
        #     im[i][j][2] = 0
        # else:
        #     for k in range(3):
        #         im[i][j][k] = 0
im = Image.fromarray(np.uint8(im))
im.save('grey_1366_768.png')