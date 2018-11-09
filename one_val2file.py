from setting import *
from utils import *

val = int(input("Fixed value: "))
raw_data = num2bin(val, BITS_NUM)

data = raw_data
if fiveBsixB:
    from fiveBsixB_coding import *
    print('Using 10B/12B...')
    data = PREAMBLE_STR + CODING_DIC[raw_data]
elif CRC4:
    print('Using CRC4...')
    data = raw_data + crc_cal(raw_data)

print('Raw data(' +  str(len(raw_data)) + '): ' + raw_data)
print('Decoded data(' +  str(len(data)) + '): ' + data)
with open(SHARE_PATH, 'w') as f:
    f.write(data)
    f.write('\n')

with open('openGL/share_data', 'w') as f:
    f.write(data)
    f.write('\n')
print('Finish writing ' + SHARE_PATH)

