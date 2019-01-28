import numpy as np
from collections import deque
from setting import MOUSE_FRAME_RATE, PREAMBLE_LIST, BITS_NUM, FRAME_RATE
from utils import smooth, interpl, chunk_decode

class Localizer:
    def __init__(self):
        self.frames = deque(maxlen=MOUSE_FRAME_RATE * 2)
        self.len_e = 1000
    
    def update(self, val_tuple):
        timestamp, val = val_tuple
        val_fixed = val
        if val_fixed < 128:
            val_fixed += 128
        if val_fixed > 240:
            return

        self.frames.append((timestamp, val_fixed))
        if last_ts is None:
            last_ts = self.frames[0][0]
        
        if self.frames[-1][0] - last_ts < (self.len_e + 100) / FRAME_RATE / 5:
            return

        M = np.array(self.frames)
        M = M[np.logical_and(M[:,0] > last_ts, M[:,0] < last_ts + self.len_e / FRAME_RATE / 5)]
        Mtime = M[:,0]
        value = M[:,1]
        last_ts = Mtime[-1]
        sample_time = np.arange(Mtime[0], Mtime[-1], 1 / FRAME_RATE / 5)
        sample_value = interpl(Mtime, value, sample_time, 'nearest')
        sample_value_smooth = smooth(sample_value, 21)
        sample_value_DCremove = smooth(sample_value - sample_value_smooth, 5)

        value = np.zeros((5, 1))
        for i in range(5):
            temp_sample = sample_value_DCremove[i:self.len_e:5]
            value[i] = np.std(temp_sample[temp_sample > (max(temp_sample) + min(temp_sample)) / 2])
        std_min = min(value)
        shift_index = np.where(value==std_min)[0][0]
        sample_wave = sample_value_DCremove[shift_index:self.len_e:5]

        # thresholding
        bit_stream = sample_wave <= (max(temp_sample) + min(temp_sample)) / 2
        bit_stream = bit_stream.astype(int)
        result = chunk_decode(bit_stream)
        if result is None:
            result = chunk_decode(bit_stream, flip=True)

        if result is not None:
            return result
    