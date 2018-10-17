import numpy as np
from scipy.interpolate import interp1d
from setting import *
import math

def interpolate_f(xy, mode='coordinate'):

    x = xy[:, 0]
    y = xy[:, 1]
    inter = interp1d(x, y, kind='linear')
    x_extend = np.linspace(x[0], x[-1], num=math.ceil(x[-1] - x[0]) * FRAMES_PER_SECOND_AFTER_INTERPOLATE)
    y_extend = inter(x_extend)

    if mode == 'coordinate':
        from utils import get_coordinate
        return get_coordinate(x_extend, y_extend)
    else:
        return x_extend, y_extend

