from PIL import Image
import numpy as np

diff = [10, 50]

base = np.zeros((1080, 960, 3), dtype=np.uint8)
base += 128

left0 = base.copy()
left0 -= diff[0]
Image.fromarray(left0).save('../display/data/left0.png')
left1 = base.copy()
left1 += diff[0]
Image.fromarray(left1).save('../display/data/left1.png')

right0 = base.copy()
right0 -= diff[1]
Image.fromarray(right0).save('../display/data/right0.png')
right1 = base.copy()
right1 += diff[1]
Image.fromarray(right1).save('../display/data/right1.png')

