# Trial

LOOP = False# True
DETAILS = True #False
INTERPOLATION_DEBUG = True
MANCHESTER_MODE = False #False #True
CRC4 = False
fiveBsixB = True
GRAPHICS = False # True
TESTING_MODE = True
FORCED_EXIT = False

if TESTING_MODE:
    GRAPHICS = False
    DETAILS = True

if not GRAPHICS:
    FORCED_EXIT = True

LOCATION_SLIDE_WINDOW_SIZE = 10
BITS_NUM = 10
FRAME_RATE = 60
MOUSE_FRAME_RATE = 2800 # 2400

if MANCHESTER_MODE:
    PREAMBLE_STR = '10001' # '10101010101010' # '000'
elif CRC4:
    PREAMBLE_STR = ''
elif fiveBsixB:
    PREAMBLE_STR = '100001' # ver.1
else:
    PREAMBLE_STR = '10101010101010' #'10001' # '10101010101010' # '000'

#PREAMBLE_STR = '11011'
PREAMBLE_LIST = list(PREAMBLE_STR) # used by np.array(preamble_list)
SIZE = (32, 32) # (256, 256)
CRC_LEN = 4


# setting for decoder

TIMES_INTERPOLATE = 10 # 10 choice one from two
FRAMES_PER_SECOND_AFTER_INTERPOLATE = 8500 # choice one from two

#POINTS_PER_FRAME = 30 # 30 # to combine
MEAN_WIDTH = 50 # 50
#MIN_LEN_PER_BIT = 15 # 15

if FRAME_RATE == 60:
    POINTS_TO_COMBINE = 14 # 40 for 20hz , 14 for 60hz -> maintain 10 points for one bit
else:
    POINTS_TO_COMBINE = 40


# setting for encoder
ZOOM = 16

