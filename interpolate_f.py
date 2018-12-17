import numpy as np
from scipy.interpolate import interp1d
from setting import *
import math
from utils import half_ceil, half_floor

def interpolate_f(xy, mode='coordinate', longer_xy=None, interval=None):

    x = xy[:, 0]
    y = xy[:, 1]
    # if interval:
    #     inter = interp1d(x, y, kind='nearest')
    # else:
    inter = interp1d(x, y, kind='linear')
    assert interval is not None
    x_extend = np.linspace(x[0], x[0] + interval, \
        num=math.ceil(interval * FRAMES_PER_SECOND_AFTER_INTERPOLATE))
    y_extend = inter(x_extend)

    if mode == 'coordinate':
        from utils import get_coordinate
        return get_coordinate(x_extend, y_extend)
    else:
        return x_extend, y_extend

