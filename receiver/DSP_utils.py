import collections
import settings
import numpy as np
from statistics import mean
from scipy.interpolate import interp1d


"""
Note: 
    1. Skip values larger than 240.
    2. Add 128 to values less than 128.
"""
def fix_raw_value(response):
    if not response:
        return
    val = int.from_bytes(response, 'big')
    val_fixed = val
    if val_fixed < 128:
        val_fixed += 128
    if val_fixed > 240:
        return
    return val_fixed


class DataManager:
    def __init__(self, graphics):
        self.data = {} # deque
        self.inter_data = {} # numpy.array
        self.shared_data = {} # list
        self.last_interpolate_ts = None
        self.init_shared_data()
        self.graphics = graphics
    
    def init_shared_data(self):
        self.shared_data['uniform_data'] = []
        self.shared_data['mean'] = []
        self.shared_data['binary_data'] = []
        self.shared_data['samples'] = []
    
    def register(self):
        self.register_data('raw_data', settings.CUT_INTERVAL * settings.POINTS_AFTER_INTERPOLATION * 2)
        self.register_data('uniform_data', settings.POINTS_PER_SAMPLE + settings.MEAN_WIDTH)
        self.register_data('binary_data', settings.POINTS_PER_SAMPLE) # One Bit

    def register_data(self, label, max_len):
        self.data[label] = collections.deque(maxlen=int(max_len))

    # append mean of the points
    def update(self, label, point):
        np_point = np.array(point)
        self.update_data(label, (np_point[:,0].mean(), np_point[:,1].mean()))

    def update_data(self, label, point):
        self.data[label].append(point)
        if label == 'raw_data':
            self.update_inter_data(label, point, share=False)
        else: # uniform_data, binary_data
            self.update_inter_data(label, point)

    def update_inter_data(self, label, point, share=True):
        if np.array(point).size == 2:
            # single point
            np_point = np.array([point])
        else:
            # list of points
            np_point = np.array(point)
        if label in self.inter_data:
            if np_point.size == 1:
                self.inter_data[label] = np.append(self.inter_data[label], np_point)
            else:
                self.inter_data[label] = np.concatenate((self.inter_data[label], np_point))
        else:
            self.inter_data[label] = np_point
        if share and self.graphics:
            self.shared_data_gk(label, point)

    def shared_data_gk(self, label, point):
        if point == []: return
        self.shared_data[label].append(point)

    def get_span(self, label, index=None):
        if index is None:
            return self.data[label][-1] - self.data[label][0]
        else:
            return self.data[label][-1][index] - self.data[label][0][index]

    def get_interpolation_span(self, label, index=None):
        if not self.last_interpolate_ts:
            return self.get_span(label, index)
        if index is None:
            return self.data[label][-1] - self.last_interpolate_ts
        return self.data[label][-1][index] - self.last_interpolate_ts
    
    def clear_inter_data(self):
        if 'uniform_data' not in self.inter_data:
            return
        if 'binary_data' not in self.inter_data:
            return
        size = len(self.inter_data['uniform_data'])
        self.inter_data['uniform_data'] = self.inter_data['uniform_data'][max(-size, -settings.MEAN_WIDTH):]
        size = len(self.inter_data['binary_data'])
        self.inter_data['binary_data'] = self.inter_data['binary_data'][max(-size, -3):]

    def processing(self, label):
        self.clear_inter_data()
        self.init_shared_data()

        # Interpolation
        interpolated = self.interpolate(label)
        if interpolated is None:
            return
        self.update_inter_data('interpolated', interpolated, share=False)

        # Averaging
        interpolated = self.inter_data['interpolated']
        num = int(len(interpolated) / settings.POINTS_TO_COMBINE)
        num = max(num, 1)
        for _ in range(num):
            self.update('uniform_data', interpolated[:settings.POINTS_TO_COMBINE])
            interpolated = interpolated[settings.POINTS_TO_COMBINE:]
        self.inter_data['interpolated'] = interpolated

        # Update Threshold & Binarization
        mean_np = np.array([[]])
        for i in self.inter_data['uniform_data']:
            if mean_np.size == 0:
                mean_np = np.array([i])
            else:
                mean_np = np.concatenate((mean_np, np.array([i])))
            cur_mean = mean_np[-settings.MEAN_WIDTH:]
            if self.graphics:
                self.shared_data_gk('mean', (cur_mean[:,0].mean(), cur_mean[:,1].mean()))
            bit2 = i > cur_mean[:,1].mean()
            self.update_data('binary_data', bit2)

            # fix one bit error
            if 'binary_data' not in self.inter_data:
                continue
            elif len(self.inter_data['binary_data']) < 3:
                continue
            bit0 = self.inter_data['binary_data'][-3]
            bit1 = self.inter_data['binary_data'][-2]
            if bit0[1] != bit1[1] and bit1[1] != bit2[1]:
                self.inter_data['binary_data'][-2][1] = bit2[1]

        # Sampling
        sample = self.sampling('binary_data')
        self.update_inter_data('samples', sample)

    def interpolate(self, label): # 0: timestamp; 1: value
        interval = settings.INTERPOLATION_INTERVAL
        cut_itv = settings.CUT_INTERVAL
        if self.get_span(label, 0) < cut_itv:
            return
        if self.get_interpolation_span(label, 0) < cut_itv:
            return
        if not self.last_interpolate_ts:
            self.last_interpolate_ts = self.data[label][0][0]
        
        np_data = np.array(self.data[label])
        np_data = np_data[np.logical_and(np_data[:, 0] > self.last_interpolate_ts, \
            np_data[:, 0] <= self.last_interpolate_ts + cut_itv)]
        self.last_interpolate_ts += interval
        
        x = np_data[:, 0]
        y = np_data[:, 1]
        if x[-1] <= x[0] + interval:
            print(x[-1] - x[0])
            return
        inter = interp1d(x, y, kind='linear')
        num = interval * settings.POINTS_AFTER_INTERPOLATION
        assert int(num) == num
        x_extend = np.linspace(x[0], x[0] + interval, num=num)
        y_extend = inter(x_extend)
        return np.concatenate((x_extend.reshape(x_extend.size, 1), \
            y_extend.reshape(y_extend.size, 1)), axis=1)
    
    def sampling(self, input_label):
        return self.inter_data[input_label][-1]
        pass
