from setting import *
from utils import *
from fiveBsixB_coding import *
from constants import *
import re

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
        self.window_of_last_one = None
        self.window_of_last_zero = None
        if location_mod:
            self.occur_times = {}
            if self.window != np.array([]):
                for ele in self.window:
                    if ele not in self.occur_times:
                        self.occur_times[ele] = 1
                    else:
                        self.occur_times[ele] += 1

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
            return 10
        count = 0
        x, y = divide_coordinate(self.window_of_last_one)
        for i in y.tolist():
            if i == ONE:
                count += 1
        return count

    def learn_len_zero(self):
        # return 3
        if self.window_of_last_zero is None:
            return 5
        count = 0
        x, y = divide_coordinate(self.window_of_last_zero)
        for i in y.tolist():
            if i == ZERO:
                count += 1
        return count

    def get_mid_index(self, index, bit):
        x, y = divide_coordinate(self.window)
        if y[index] != bit:
            return index
        bit_len = 1
        most_left = 0
        most_right = self.window.shape[0] - 1
        index1 = index
        while True:
            index1 += 1
            if index1 == self.window.shape[0]:
                break
            if y[index1] == bit:
                bit_len += 1
            else:
                most_right = index1 - 1
                break
                
        index2 = index
        while True:
            index2 -= 1
            if index2 == -1:
                break
            if y[index2] == bit:
                bit_len += 1
            else:
                most_left = index2 + 1
                break
        return int((most_left + most_right) / 2)

    def check_bit(self, sample_slide):
        if self.init_timestamp and CHECK_BIT == 'BY_TIME':
            x, y = divide_coordinate(self.window)
            ########################### METHOD 1 ####################
            # if x[-1] >= self.init_timestamp + 1 / FRAME_RATE:
            #     bit = '1' if y[-1] == ONE else '0'
            #     if bit == '1':
            #         sample_slide.push(np.array([[x[-1], ONE]]))
            #     else:
            #         sample_slide.push(np.array([[x[-1], ZERO]]))
            #     self.init_timestamp = x[-1]
            #     return bit
            
            ########################## METHOD 2 #####################
            mid_index = int(x.size/2)
            # if x[mid_index] >= self.init_timestamp + 1 / FRAME_RATE * 0.9:
            if x[mid_index] >= self.init_timestamp + 1 / FRAME_RATE:
            ########################## METHOD 2.1 #####################
                # bit = '1' if y[mid_index] == ONE else '0'
                # if bit == '1':
                #     sample_slide.push(np.array([[x[mid_index], ONE]]))
                # else:
                #     sample_slide.push(np.array([[x[mid_index], ZERO]]))
                # self.init_timestamp = x[mid_index]
                # return bit
            ######################## METHOD 2.2 ############################
                # num_one = 0
                # num_zero = 0
                # l = 3
                # r = 8
                # for e in y[l:r].tolist():
                #     if e == ONE:
                #         num_one += 1
                #     else:
                #         num_zero += 1

                # pct = 0.6 if r - l == 3 else 0.7
                # if num_one / (r-l) >= pct:
                #     sample_slide.push(np.array([[x[mid_index], one]]))
                #     self.init_timestamp = x[mid_index]
                #     return '1'
                # elif num_zero / (r-l) >= pct:
                #     sample_slide.push(np.array([[x[mid_index], zero]]))
                #     self.init_timestamp = x[mid_index]
                #     return '0'
            ############################ METHOD 2.3 #########################
                # num_one = 0 
                # num_zero = 0
                # len_zero = 5
                # len_one = 10
                # pct = 0.7

                # left_zero = math.floor((y.size-len_zero)/2)
                # for e in y[left_zero:left_zero + len_zero].tolist():
                #     if e == ZERO:
                #         num_zero += 1

                # left_one = math.floor((y.size-len_one)/2)
                # for e in y[left_one:left_one + len_one].tolist():
                #     if e == ONE:
                #         num_one += 1

                # if num_one / len_one >= pct:
                #     sample_slide.push(np.array([[x[mid_index], ONE]]))
                #     self.init_timestamp = x[mid_index]
                #     return '1'
                # elif num_zero / len_zero >= pct:
                #     sample_slide.push(np.array([[x[mid_index], ZERO]]))
                #     self.init_timestamp = x[mid_index]
                #     return '0'
            ###################### METHOD 2.4 ##################################
            # learn last bit occupies how many samples
            # len_zero: min(between [5,10])
            # len_one: min(between [8,13])
                num_one = 0 
                num_zero = 0
                len_zero = self.learn_len_zero() - 1
                len_one = self.learn_len_one()
                assert len_zero != 0
                assert len_one != 0
                pct = 0.8

                left_zero = math.floor((y.size-len_zero)/2)
                for e in y[left_zero:left_zero + len_zero].tolist():
                    if e == ZERO:
                        num_zero += 1

                left_one = math.floor((y.size-len_one)/2)
                for e in y[left_one:left_one + len_one].tolist():
                    if e == ONE:
                        num_one += 1

                if num_one / len_one >= pct:
                    mid_index = self.get_mid_index(mid_index, ONE)
                    sample_slide.push(np.array([[x[mid_index], ONE]]))
                    self.init_timestamp = x[mid_index]
                    self.window_of_last_one = self.window
                    return '1'
                elif num_zero / len_zero >= pct:
                    mid_index = self.get_mid_index(mid_index, ZERO)
                    sample_slide.push(np.array([[x[mid_index], ZERO]]))
                    self.init_timestamp = x[mid_index]
                    self.window_of_last_zero = self.window
                    return '0'
            ####################################################################
            return



        if not self.is_full():
            return None
        x, y = divide_coordinate(self.window)
        num_one = 0
        num_zero = 0
        for e in y.tolist():
            if e == ONE:
                num_one += 1
            else:
                num_zero += 1

        pct = 0.9
        if num_one / y.size == pct:
            self.init_timestamp = x[math.floor((x.size - 1) / 2) - 1] if y[-1] == ZERO \
                else x[math.floor((x.size - 1) / 2) + 1]
            sample_slide.push(np.array([[self.init_timestamp, ONE]]))
            return '1'
        elif not self.init_timestamp and num_zero / y.size == 0.9:
            self.init_timestamp = x[math.floor((x.size - 1) / 2) - 1] if y[-1] == ONE \
                else x[math.floor((x.size - 1) / 2) + 1]
            sample_slide.push(np.array([[self.init_timestamp, ZERO]]))
            return '0'
        return None

class BitSlideArray:
    def __init__(self, window, size, location_mod=False):
        if MANCHESTER_MODE:
            self.pattern = PREAMBLE_STR + '\d{' + str(BITS_NUM * 2) + '}'
        elif fiveBsixB:
            # only for 10b12b
            self.pattern = PREAMBLE_STR + '\d{12}'
        elif CRC4:
            self.pattern = None
            self.pending_count = 0
        else:
            self.pattern = PREAMBLE_STR + '\d{' + str(BITS_NUM) + '}'  
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
        self.push(bit_detected)
        return self.decode()

    def decode(self):
        if MANCHESTER_MODE:
            temp_str = ''.join(self.window)[-len(PREAMBLE_STR) - BITS_NUM * 2:]
            #if DETAILS:
            #    print(temp_str)
            sub_str = re.findall(self.pattern, temp_str)
            if sub_str == []:
                return
            possible_dataB = []
            possible_dataD = []
            for i in sub_str:
                i_removed_preamble = sim_fix(i[len(PREAMBLE_STR):])
                if len(i_removed_preamble) != 2 * BITS_NUM:
                    continue
                bit_str = Manchester_decode(i_removed_preamble)
                if not bit_str:
                    continue
                decoded_num = bit_str2num(bit_str)
                if DETAILS:
                    print(bit_str)
                    print(decoded_num)
                possible_dataB.append(bit_str)
                possible_dataD.append(decoded_num)
            return possible_dataB, possible_dataD
        elif CRC4:
            #if DETAILS:
            #    print(temp_str)
            if self.pending_count != 0:
                self.pending_count -= 1
                return
            if len(self.window) < BITS_NUM + 4:
                return
            possible_dataB = []
            possible_dataD = []
            i_removed_preamble = ''.join(self.window)[-BITS_NUM-4:]
            if not crc_validate(i_removed_preamble[:BITS_NUM], i_removed_preamble[-4:]):
                return
            bit_str = i_removed_preamble[:BITS_NUM]
            decoded_num = bit_str2num(bit_str)
            if DETAILS:
                print(bit_str)
                print(decoded_num)
            possible_dataB.append(bit_str)
            possible_dataD.append(decoded_num)
            if possible_dataB != [] and possible_dataD != []:
                self.pending_count = BITS_NUM + 4
            return possible_dataB, possible_dataD
        elif fiveBsixB:
            # only for 10b12b
            if len(self.window) < len(PREAMBLE_STR) + BITS_NUM + 2:
                return
            temp_str = ''.join(self.window)[-len(PREAMBLE_STR) - BITS_NUM - 2:]
            #if DETAILS:
            #    print(temp_str)
            sub_str = re.findall(self.pattern, temp_str)
            if sub_str == []:
                return
            possible_dataB = []
            possible_dataD = []
            for i in sub_str:
                i_removed_preamble = i[len(PREAMBLE_STR):]
                if len(i_removed_preamble) != 2 + BITS_NUM:
                    continue
                try:
                    bit_str = REVERSE_DIC[i_removed_preamble]
                except:
                    continue
                if not bit_str:
                    continue
                decoded_num = bit_str2num(bit_str)
                if DETAILS:
                    print(bit_str)
                    print(decoded_num)
                possible_dataB.append(bit_str)
                possible_dataD.append(decoded_num)
            return possible_dataB, possible_dataD
        else:
            bit_str = ''.join(self.window)[-len(PREAMBLE_STR) - BITS_NUM:]
            if DETAILS:
                print(bit_str)
            sub_str = re.findall(self.pattern, bit_str)
            decoded_data = [i[len(PREAMBLE_STR):] for i in sub_str]
            decoded_num = [bit_str2num(i) for i in decoded_data]
            if decoded_data != []:
                if DETAILS:
                    print(decoded_data)
                    print(decoded_num)
                return decoded_data, decoded_num
            

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
