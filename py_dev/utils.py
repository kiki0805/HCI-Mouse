from crccheck.crc import Crc4Itu
from setting import BITS_NUM, PREAMBLE_LIST, TOTAL_LEN, CRC_LEN, PREAMBLE_LEN, EXPEND, SIZE
import numpy as np


def chunk_decode(np_chunk, flip=False):
    chunk = [str(i) for i in np_chunk]
    chunk = ''.join(chunk)
    if flip:
        pat = '0101'
    else:
        pat = '1010'
    rtn = []

    for i in range(len(chunk)):
        if chunk[i:i + PREAMBLE_LEN] == pat:
            bit_str = designed_decode(chunk[i + PREAMBLE_LEN:i + PREAMBLE_LEN + BITS_NUM * EXPEND], flip=flip)
            crc_str = chunk[i + TOTAL_LEN - CRC_LEN:i + TOTAL_LEN]
            if not bit_str:
                continue
            if len(bit_str) != BITS_NUM:
                continue
            decoded_num = bit_str2num(bit_str)
            if crc_validate(bit_str, crc_str):
                rtn.append([decoded_num, bit_str, naive_location(decoded_num)])

    if rtn != []:
        return rtn


def naive_location(data):
    return (int(data / SIZE[0]), data % SIZE[0])
    # return ()


def designed_decode(received, recurse=True, flip=False):
    if flip:
        one = '011'
        zero = '001'
    else:
        one = '100'
        zero = '110'
    decoded = ''
    for i in range(0, len(received), EXPEND):
        sub_data = received[i:i + EXPEND]
        if sub_data == one:
            decoded += '1'
        elif sub_data == zero:
            decoded += '0'
        else:
            return
    return decoded


def designed_code(raw):
    new_code = []
    for i in raw:
        if int(i) == 1:
            new_code += [1, -1, -1]
        else:
            new_code += [1, 1, -1]
    return PREAMBLE_LIST + new_code


from scipy.interpolate import interp1d
def interpl(x, y, x_sample, method='nearest'):
    inter = interp1d(x, y, kind=method)
    return inter(x_sample)


def smooth(a,WSZ):
    # a: NumPy 1-D array containing the data to be smoothed
    # WSZ: smoothing window size needs, which must be odd number,
    # as in the original MATLAB implementation
    out0 = np.convolve(a,np.ones(WSZ,dtype=int),'valid')/WSZ    
    r = np.arange(1,WSZ-1,2)
    start = np.cumsum(a[:WSZ-1])[::2]/r
    stop = (np.cumsum(a[:-WSZ:-1])[::2]/r)[::-1]
    return np.concatenate((  start , out0, stop  ))


def bit_str2num(bits_str):
    num = 0
    for i in range(len(bits_str) - 1, -1, -1):
        bit_str = bits_str[i]
        multiplier = 0 if bit_str == '0' else 1
        num += multiplier * pow(2, len(bits_str) - 1 - i)
    return num 


def num2bin(num, bit_num): # return str
    current = "{0:b}".format(num)
    while len(current) < bit_num:
        current = '0' + current
    return current[-bit_num:]


def crc_cal(num, binary=True, bit_num=10):
    if type(num) == str:
        num = bit_str2num(num)
    byte_arr = bytearray(num.to_bytes(2, 'big'))
    crc = Crc4Itu.calc(byte_arr)
    if binary:
        return num2bin(crc, 4)
    else:
        return crc


def crc_validate(num, crc, binary=True, bit_num=10):
    if binary:
        num = bit_str2num(num)
        crc = bit_str2num(crc)
    hex_byte = bytes([crc])
    byte_arr = bytearray(num.to_bytes(2, 'big')) + hex_byte
    new_crc = Crc4Itu.calc(byte_arr)
    if new_crc == 0:
        return True
    return False
