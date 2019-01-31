import os
def get_imgs():
    dirs = os.listdir()
    angles = []
    for d in dirs:
        if d[:4] == 'red_':
            angles.append(d[4:-4])
    return angles

def red_img_name(idx_str, prefix='./'):
    return prefix + 'red_' + idx_str + '.png'

def white_img_name(idx_str, prefix='./'):
    return prefix + 'white_' + idx_str + '.png'

def img_name(idx_str, color, prefix='./'):
    return prefix + color + '_' + idx_str + '.png'

def change_mode(cur_mode):
    return 'white' if cur_mode == 'red' else 'red'
