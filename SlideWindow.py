from setting import *
from utils import *
from fiveBsixB_coding import *
from constants import *
import re
import math

class SlideArray:
    def __init__(self, window, size, line, draw_interval, ele_type='coordiante', location_mod=False, sample_line=None, scatter_mode=False):
        self.scatter_mode = scatter_mode
        self.sample_line = sample_line
        self.window = window
        self.draw_interval = draw_interval
        self.line = line
        self.size = size
        self.last_detected = -1
        self.location_mod = location_mod
        self.init_timestamp = None
        self.last_timestamp = None
        self.count = 0
        self.cache = []
        self.window_of_last_one = None
        self.window_of_last_zero = None
        self.least_zero_count = 10
        self.least_one_count = 10
        self.mean_zero_count = None
        self.mean_one_count = None
        self.prefer = [0.5, 0.5]
        self.continuous_one = 0
        self.continuous_zero = 0
        if location_mod:
            self.occur_times = {}
            if self.window != np.array([]):
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

    def reset_least_count(self):
        self.least_one_count *= 2
        self.least_zero_count *= 2
        self.mean_one_count = max(self.mean_one_count, self.least_one_count)
        self.mean_zero_count = max(self.mean_zero_count, self.least_zero_count)

    def push(self, chunk_or_ele): # chunk for coordinate, ele for binary bits
        assert chunk_or_ele.size <= self.size * 2
        if self.window.size + chunk_or_ele.size > self.size * 2:
            if self.location_mod:
                print(self.window)
                print(self.occur_times)
                self.occur_times[self.window[0]] -= 1
            self.window = self.window[int((chunk_or_ele.size + self.window.size) - self.size * 2):]
        if self.window.size == 0:
            self.window = chunk_or_ele
        else:
            self.window = np.concatenate((self.window, chunk_or_ele))
        if self.location_mod:
            if chunk_or_ele in self.occur_times:
                self.occur_times[chunk_or_ele] += 1
            else:
                self.occur_times[chunk_or_ele] = 1

    def is_full(self):
        if self.window.size > self.size * 2:
            print('outflow')
        return self.window.size == self.size * 2

    def most_frequent_ele(self):
        assert self.location_mod
        return max(self.occur_times, key=self.occur_times.get)

    def reset(self):
        self.window = np.array([])

    def update_line_data(self):
        if self.line is None:
            return
        if self.window.size == 0:
            return

        x, y = divide_coordinate(self.window)
        # x = x[0:x.size:5]
        # y = y[0:y.size:5]
        if x.size < self.draw_interval:
            if self.scatter_mode:
                self.line.set_offsets(self.window)
                return
            self.line.set_xdata(x)
            self.line.set_ydata(y)
        else:
            if self.scatter_mode:
                self.line.set_offsets(self.window[-self.draw_interval:,:])
                return
            self.line.set_xdata(x[-self.draw_interval:])
            self.line.set_ydata(y[-self.draw_interval:])

    def learn_len_one(self):
        # return 5
        if self.window_of_last_one is None:
            return 8
        count = 0
        x, y = divide_coordinate(self.window_of_last_one)
        for i in y.tolist():
            if i == ONE:
                count += 1
        if self.mean_one_count is None:
            self.mean_one_count = count
        else:
            self.mean_one_count = math.ceil(0.5 * count + 0.5 * self.mean_one_count)

        self.least_one_count = min(self.least_one_count, count)
        return self.mean_one_count

    def learn_len_zero(self):
        # return 3
        if self.window_of_last_zero is None:
            return 8
        count = 0
        x, y = divide_coordinate(self.window_of_last_zero)
        for i in y.tolist():
            if i == ZERO:
                count += 1
        if self.mean_zero_count is None:
            self.mean_zero_count = count
        else:
            self.mean_zero_count = math.ceil(0.5 * count + 0.5 * self.mean_zero_count)
        self.least_zero_count = min(self.least_zero_count, count)
        return self.mean_zero_count

    def find_true_index(self, index, bit):
        return index

    def get_mid_index(self, index, bit):
        x, y = divide_coordinate(self.window[:10])
        if y[index] != bit:
            return self.find_true_index(index, bit)
        bit_len = 1
        most_left = 0
        most_right = self.window[:10].shape[0] - 1
        index1 = index
        # find most right
        while True:
            index1 += 1
            if index1 == self.window[:10].shape[0]:
                break
            if y[index1] == bit:
                bit_len += 1
            else:
                most_right = index1 - 1
                break
                
        index2 = index
        # find most left
        while True:
            index2 -= 1
            if index2 == -1:
                break
            if y[index2] == bit:
                bit_len += 1
            else:
                most_left = index2 + 1
                break
        
        if bit == ZERO and self.mean_zero_count is not None:
            most_right = min(most_right, most_left + self.mean_zero_count)
        elif self.mean_one_count is not None:
            most_right = min(most_right, most_left + self.mean_one_count)
        return int((most_left + most_right) / 2)

    # def is_flat(self, arr, index1, index2):
        # bit = arr[index1]
        # for i in range(index1 + 1, index2):
        #     if arr[i] != bit:
        #         return False
        # return True

    def is_flat(self, arr, index):
        if arr[index] == arr[index + 1] and \
                arr[index] == arr[index + 2] and \
                arr[index] == arr[index - 1] and \
                arr[index] == arr[index - 2]:
            return True
        return False

    def sample(self):
        pass

    def check_bit(self, sample_slide):
        if self.init_timestamp is None:
            return self.init_sample(sample_slide)

        x, y = divide_coordinate(self.window[:10])
        mid_index = int(x.size/2)

        unit = 1.5 / FRAME_RATE / 10

        # if x[mid_index] < self.last_timestamp + 1 / FRAME_RATE: return
        # if y[mid_index] == ONE:
        #     return self.return_one(mid_index, x, sample_slide)
        # else:
        #     return self.return_zero(mid_index, x, sample_slide)


        if x[mid_index] > self.last_timestamp + 1 / FRAME_RATE - unit and \
                x[mid_index] < self.last_timestamp + 1 / FRAME_RATE + unit and \
                x[mid_index] > self.init_timestamp + self.count / FRAME_RATE - unit and \
                x[mid_index] < self.init_timestamp + self.count / FRAME_RATE + unit:
            self.cache.append(self.window[:10])
        if x[mid_index] > self.last_timestamp + 1 / FRAME_RATE + unit or \
                x[mid_index] > self.init_timestamp + self.count / FRAME_RATE + unit:
            # print(len(self.cache))
            if self.prefer == [0, 1]:
                return self.return_one(mid_index, x, sample_slide)
            elif self.prefer == [1, 0]:
                return self.return_zero(mid_index, x, sample_slide)
            zero_pct_list = []
            one_pct_list = []
            for tmp_win in self.cache:
                x, y = divide_coordinate(tmp_win)
                mid_index = int(x.size/2)
                
                num_one = 0 
                num_zero = 0
                len_zero = self.learn_len_zero() # approximate length
                len_one = self.learn_len_one() # approximate length
                
                assert len_zero != 0
                assert len_one != 0
                
                # count number of zero in the middle interval with length len_zero
                left_zero = math.floor((y.size-len_zero)/2)
                for e in y[left_zero:left_zero + len_zero].tolist():
                    if e == ZERO:
                        num_zero += 1

                # count number of one in the middle interval with length len_one
                left_one = math.floor((y.size-len_one)/2)
                for e in y[left_one:left_one + len_one].tolist():
                    if e == ONE:
                        num_one += 1

                zero_pct_list.append(num_zero / len_zero)
                one_pct_list.append(num_one / len_one)
            
            if self.cache == []:
                # raise Exception
                if self.prefer == [0, 1]:
                    return self.return_one(mid_index, x, sample_slide)
                elif self.prefer == [1, 0]:
                    return self.return_zero(mid_index, x, sample_slide)
                elif y[mid_index] == ONE:
                    return self.return_one(mid_index, x, sample_slide)
                else:
                    return self.return_zero(mid_index, x, sample_slide)

            
            index = int(len(self.cache) / 2)
            if sum(zero_pct_list) >= sum(one_pct_list):
                x, _ = divide_coordinate(self.cache[index])
                return self.return_zero(mid_index, x, sample_slide)
        
            x, _ = divide_coordinate(self.cache[index])
            return self.return_one(mid_index, x, sample_slide)
        
        

    def init_sample(self, sample_slide):
        if not self.is_full():
            return None
        x, y = divide_coordinate(self.window[:10])
        num_one = 0
        num_zero = 0
        for e in y.tolist():
            if e == ONE:
                num_one += 1
            else:
                num_zero += 1
        pct = 0.9
        if num_one / y.size == pct and y[0] == ZERO:
            self.init_timestamp = x[math.floor((x.size) / 2) + 1]
            self.last_timestamp = self.init_timestamp
            sample_slide.push(np.array([[self.init_timestamp, ONE]]))
            self.count += 1
            print('init done')
            return 'first1'
        elif num_zero / y.size == 0.9 and y[0] == ONE:
            self.init_timestamp = x[math.floor((x.size) / 2) + 1]
            self.last_timestamp = self.init_timestamp
            sample_slide.push(np.array([[self.init_timestamp, ZERO]]))
            self.count += 1
            print('init done')
            return 'first0'
        #############################################
        # if num_one / y.size == pct:
        #     self.init_timestamp = x[math.floor((x.size) / 2) - 1] if y[-1] == ZERO \
        #         else x[math.floor((x.size) / 2) + 1]
        #     self.last_timestamp = self.init_timestamp
        #     sample_slide.push(np.array([[self.init_timestamp, ONE]]))
        #     self.count += 1
        #     print('init done')
        #     return 'first1'
        # elif num_zero / y.size == 0.9:
        #     self.init_timestamp = x[math.floor((x.size) / 2) - 1] if y[-1] == ONE \
        #         else x[math.floor((x.size) / 2) + 1]
        #     self.last_timestamp = self.init_timestamp
        #     sample_slide.push(np.array([[self.init_timestamp, ZERO]]))
        #     self.count += 1
        #     print('init done')
        #     return 'first0'
        return None

    def return_zero(self, mid_index, x, sample_slide):
        # mid_index = self.get_mid_index(mid_index, ZERO)
        sample_slide.push(np.array([[x[mid_index], ZERO]]))
        self.last_timestamp = x[mid_index]
        self.window_of_last_zero = self.window[:10]

        if self.continuous_one != 0: self.continuous_one = 0
        self.continuous_zero += 1
        self.recaculate_prefer()
        self.count += 1
        self.cache = []
        return '0'
    
    def return_one(self, mid_index, x, sample_slide):
        # mid_index = self.get_mid_index(mid_index, ONE)
        sample_slide.push(np.array([[x[mid_index], ONE]]))
        self.last_timestamp = x[mid_index]
        self.window_of_last_one = self.window[:10]

        if self.continuous_zero != 0: self.continuous_zero = 0
        self.continuous_one += 1
        self.recaculate_prefer()
        self.count += 1
        self.cache = []
        return '1'
    
    def recaculate_prefer(self):
        if self.count >= 800:
            self.init_timestamp = None
            self.last_timestamp = None
            self.count = 0
            self.cache = []
            self.continuous_one = 0
            self.continuous_zero = 0
            self.prefer = [0.5, 0.5]

        tolerate_one = 2
        tolerate_zero = 2
        
        if self.continuous_one >= tolerate_one:
            self.prefer = [1, 0]
        elif self.continuous_zero >= tolerate_zero:
            self.prefer = [0, 1]
        elif self.continuous_one != 0:
            one_prob = ( tolerate_one - self.continuous_one ) / tolerate_one
            self.prefer = [one_prob, 1 - one_prob]
        elif self.continuous_zero != 0:
            zero_prob = ( tolerate_zero - self.continuous_zero ) / tolerate_zero
            self.prefer = [zero_prob, 1 - zero_prob]


class BitSlideArray:
    def __init__(self, window, size, location_mod=False):
        self.window = window
        self.size = size
        self.last_detected = -1
        self.location_mod = location_mod
        if location_mod:
            self.occur_times = {}
            if self.window != np.array([]):
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

    def update(self, one_bit, sample_arr):
        bit_detected = one_bit.check_bit(sample_arr)
        if not bit_detected:
           # if self.window.size != 0:
           #     self.reset()
            return
        if len(bit_detected) > 1:
            self.push(bit_detected[-1])
            return bit_detected[:-1]
        
        self.push(bit_detected)
        ret = self.decode()
        if ret[0] == []:
            ret = self.decode(flip=True)
        return ret
    
    def flip(self):
        for i in range(self.window.shape[0]):
            self.window[i] = '0' if self.window[i] == '1' else '1'

    def decode(self, flip=False):
        assert DESIGNED_CODE
        if len(self.window) < len(PREAMBLE_LIST) + BITS_NUM * EXPEND:
            return [], []
        bit_str = ''.join(self.window)[-len(PREAMBLE_LIST) - BITS_NUM * EXPEND:]
        if flip:
            sub_str = re.findall('0101' + '\d{30}', bit_str)
        else:
            sub_str = re.findall('1010' + '\d{30}', bit_str)
        possible_dataB = []
        possible_dataD = []
        for i in sub_str:
            i_removed_preamble = i[len(PREAMBLE_LIST):]
            bit_str = designed_decode(i_removed_preamble, flip=True)
            if not bit_str:
                return possible_dataB, possible_dataD
            if len(bit_str) != BITS_NUM:
                return possible_dataB, possible_dataD
            
            decoded_num = bit_str2num(bit_str)
            if DETAILS:
                print(bit_str)
                print(decoded_num)
            possible_dataB.append(bit_str)
            possible_dataD.append(decoded_num)
        return possible_dataB, possible_dataD

    def push(self, ele):
        if self.window.size >= self.size:
            if self.location_mod:
                print(self.window)
                print(self.occur_times)
                self.occur_times.pop(self.window[0])
            self.window = np.delete(self.window, 0, axis=0)
        self.window = np.append(self.window, ele)
        if self.location_mod:
            if ele in self.occur_times:
                self.occur_times[ele] += 1
            else:
                self.occur_times[ele] = 1

    def is_full(self):
        return self.window.size == self.size

    def most_frequent_ele(self):
        assert self.location_mod
        return max(self.occur_times, key=self.occur_times.get)

    def reset(self):
        self.window = np.array([])


class TupleSlideArray:
    def __init__(self, window, size, location_mod=False):
        self.window = window
        self.size = size
        self.location_mod = location_mod
        if location_mod:
            self.occur_times = {}
            if self.window != []:
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

    def push(self, ele):
        if len(self.window) >= self.size * 2:
            if self.location_mod:
                self.occur_times[self.window[0]] -= 1
            del self.window[0]
        self.window.append(ele)
        if self.location_mod:
            if ele in self.occur_times:
                self.occur_times[ele] += 1
            else:
                self.occur_times[ele] = 1

    def is_full(self):
        return len(self.window) == self.size * 2

    def most_frequent_ele(self):
        assert self.location_mod
        return max(self.occur_times, key=self.occur_times.get)

    def reset(self):
        self.window = np.array([])
