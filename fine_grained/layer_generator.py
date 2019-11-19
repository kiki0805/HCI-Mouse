from PIL import Image
import re

scale = 30
image_size = [32*scale,32*scale]
line_size = 4*scale
for i in range(image_size[1]//line_size):
    im = Image.new('RGB', (image_size[0],image_size[1]) , (255,255,255))
    pixelMap = im.load()
    for j in range(image_size[0]):
        for k in range(line_size):
            pixelMap[j,i*line_size+k] = (0,0,0)
    im.save("Large_Hor_{0}.jpg".format(i))
    
for i in range(image_size[0]//line_size):
    im = Image.new('RGB', (image_size[0],image_size[1]) , (255,255,255))
    pixelMap = im.load()
    for j in range(image_size[1]):
        for k in range(line_size):
            pixelMap[i*line_size+k,j] = (0,0,0)
    im.save("Large_Ver_{0}.jpg".format(i))    
    