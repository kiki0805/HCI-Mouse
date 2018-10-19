# Trial

INTERPOLATION_DEBUG = True


GRAPHICS = True #False # True
TESTING_MODE = False #True
FORCED_EXIT = False

if TESTING_MODE:
    GRAPHICS = False

if not GRAPHICS:
    FORCED_EXIT = True

LOCATION_SLIDE_WINDOW_SIZE = 10
BITS_NUM = 10
FRAME_RATE = 20
MOUSE_FRAME_RATE = 2800 # 2400
PREAMBLE_STR = '10101010101010'
#PREAMBLE_STR = '11011'
PREAMBLE_LIST = list(PREAMBLE_STR) # used by np.array(preamble_list)
SIZE = (4, 4) # (256, 256)


# setting for decoder

TIMES_INTERPOLATE = 10 # 10 choice one from two
FRAMES_PER_SECOND_AFTER_INTERPOLATE = 8500 # choice one from two

POINTS_PER_FRAME = 30 # 30 # to combine
MEAN_WIDTH = 50 # 50
MIN_LEN_PER_BIT = 15 # 15
POINTS_TO_COMBINE = 40


# setting for encoder
ZOOM = 64 * 2

# Ultimate
#bits_num = 21
#frame_rate = 30
#preamble_str = '101101101001010'
#preamble_list = list(preamble_str) # used by np.array(preamble_list)
#screen_size = (1920, 1080)

