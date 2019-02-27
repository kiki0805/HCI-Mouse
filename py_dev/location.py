import numpy as np
from collections import deque
from setting import MOUSE_FRAME_RATE, PREAMBLE_LIST, BITS_NUM, FRAME_RATE
from utils import smooth, interpl, chunk_decode

class Localizer:
    def __init__(self):
        self.frames = deque(maxlen=MOUSE_FRAME_RATE * 2)
        self.len_e = 1000
        self.last_ts = None
    
    def update(self, val_tuple):
        tuple1, tuple2 = val_tuple
        rlt = self.resolve(tuple1) # 0x0D
        if not rlt:
            return self.resolve(tuple2, fix=False) # 0x0B
        return rlt
    
    def reset(self):
        self.frames = deque(maxlen=MOUSE_FRAME_RATE * 2)
        self.last_ts = None

    def resolve(self, val_tuple, fix=True):
        timestamp, val = val_tuple
        val_fixed = val
        if fix:
            # print(val_fixed)
            if val_fixed < 128:
                val_fixed += 128
            if val_fixed > 240:
                return

        self.frames.append((timestamp, val_fixed))
        if self.last_ts is None:
            self.last_ts = self.frames[0][0]
        
        if self.frames[-1][0] - self.last_ts < 0.6:
            return

        M = np.array(self.frames)
        M = M[np.logical_and(M[:,0] > self.last_ts - 0.5, M[:,0] < self.last_ts + 0.5)]
        Mtime = M[:,0]
        value = M[:,1]
        self.last_ts = Mtime[-1]
        sample_time = np.arange(Mtime[0], Mtime[-1], 1 / 2400)
        sample_value = interpl(Mtime, value, sample_time[:-1], 'nearest')
        sample_time = sample_time[:-1]
        sample_value_smooth = smooth(sample_value, 41)
        sample_value_DCremove = smooth(sample_value - sample_value_smooth, 5)

        value = np.zeros((10, 1))
        for i in range(10):
            temp_sample = sample_value_DCremove[i:self.len_e:10]
            value[i] = max(temp_sample) + min(temp_sample)
        std_min = max(value)
        shift_index = np.where(value==std_min)[0][0]
        sample_wave = sample_value_DCremove[shift_index:self.len_e:10]
        temp_sample = sample_value_DCremove[shift_index:self.len_e:10]

        bit_stream = sample_wave <= np.mean(temp_sample)
        bit_stream = bit_stream.astype(int)
        result = chunk_decode(bit_stream)
        if result is None:
            result = chunk_decode(bit_stream, flip=True)

        if result is not None:
            print(result)
            return result
    