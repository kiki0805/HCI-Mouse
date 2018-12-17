from setting import *
from utils import *

def hle(size):
    assert math.log(size[0], 2) % 1 == 0
    assert math.log(size[1], 2) % 1 == 0

    width_divided = size[0]
    height_divided = size[1]

    imgs_arr = np.zeros((BITS_NUM, size[0], size[1]), dtype=np.int16)
    [im_id, row, col] = imgs_arr.shape

    turn = True
    for n in range(im_id):
        # if n < len(PREAMBLE_STR):
        #     imgs_arr[n, :, :] = PREAMBLE_STR[n] == '0'
        #     continue
        mod = width_divided / 2 if turn else height_divided / 2
        if turn:
            width_divided /= 2
        else:
            height_divided /= 2

        if turn:
            for j in range(col):
                imgs_arr[n, :, j] = '0' if math.floor(j / mod) % 2 == 0 else '1'
        else:
            for i in range(row):
                imgs_arr[n, i, :] = '0' if math.floor(i / mod) % 2 == 0 else '1'
                
        turn = not turn
    return imgs_arr


# per x, y, per bit
# without preamble
def hle_raw(size):
    imgs_arr = np.zeros((size[0], size[1], BITS_NUM), dtype=np.int16)
    raw_imgs_arr = hle(size)
    for i in range(size[0]):
        for j in range(size[1]):
            imgs_arr[i,j,:] = raw_imgs_arr[:,i,j]
    return imgs_arr
            

# with preamble
# per x,y, per bit
def fiveBsixB_encode(size):
    from fiveBsixB_coding import CODING_DIC
    assert BITS_NUM == 10
    raw_arr = hle_raw(size)
    imgs_arr = np.zeros((size[0], size[1], len(PREAMBLE_STR) + 12), dtype=np.int16)
    for i in range(size[0]):
        for j in range(size[1]):
            temp_list = raw_arr[i,j,:].tolist()
            temp_list = [str(i) for i in temp_list]
            encoded_str = CODING_DIC[''.join(temp_list)]
            encoded_list = PREAMBLE_STR + encoded_str
            imgs_arr[i,j] = list(encoded_list)
    return imgs_arr

def write_nparray(arr):
    f = open(SHARE_PATH_LOCATION, 'w')
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            str_list = [str(i) for i in arr[i][j]]
            f.write(''.join(str_list))
            f.write('\n')
    f.close()
    f = open('openGL/share_data_location', 'w')
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            str_list = [str(i) for i in arr[i][j]]
            f.write(''.join(str_list))
            f.write('\n')
    f.close()


if fiveBsixB:
    raw_data = fiveBsixB_encode(SIZE)
    print('Using 10B/12B...')
    write_nparray(raw_data)
    print('Location data of block (x, y) are stored in:')
    print('\tline x * SIZE + y ( from 0 ).')
    print('Line n ( from 0 ) stores location data of:')
    print('\tblock (floor(n / SIZE), n - SIZE * floor(n / SIZE)).')
    print('Finish writing ' + SHARE_PATH_LOCATION + ' and openGL/share_data_location')
else:
    print('Not supported yet...')
    # data = raw_data + crc_cal(raw_data)

