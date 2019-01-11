from SlideWindow import *
import matplotlib.pyplot as plt

# line1 = plt.scatter([], [], marker='o', color='red') # plot the data and specify the 2d line
line1, = plt.plot([], [], 'r')
line2, = plt.plot([], [], 'b', label='inter')
line3, = plt.plot([], [], 'g', label='mean')
line4, = plt.plot([], [], 'y', label='repaired')
line5 = plt.scatter([], [], marker='x', color='black')
line6, = plt.plot([], [], 'm')


raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, line1, int(MOUSE_FRAME_RATE * 0.1))  # maintain raw frames within around 2 seconds
# raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, None, int(MOUSE_FRAME_RATE / 2))  # maintain raw frames within around 2 seconds
# frames_m = SlideArray(np.array([[]]), int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line2, \
#         int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 16)) # maintain frames within 2 seconds after interpolation
# y_mean = SlideArray(np.array([[]]), int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line3, \
#         int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE /16)) # maintain frames within 2 seconds after interpolation
# one_bit = SlideArray(np.array([[]]), math.ceil(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / FRAME_RATE) * 2, line4, \
#         math.floor(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / FRAME_RATE)) # maintain frames within 2 seconds after interpolation
# sample_arr = SlideArray(np.array([[]]), int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line5, \
#         int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 16), scatter_mode=True) # maintain frames within 2 seconds after interpolation

# binary_arr = SlideArray(np.array([[]]), math.ceil(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE * 2), line1, \
        # int(FRAMES_PER_SECOND_AFTER_INTERPOLATE / POINTS_TO_COMBINE / 16)) # maintain frames within 2 seconds after interpolation

if MANCHESTER_MODE:
    bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM * 2 + len(PREAMBLE_STR)) * 2) # maintain frames within 2 seconds after interpolation
elif fiveBsixB:
    bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM + 2 + len(PREAMBLE_STR)) * 2)
elif CRC4:
    bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM + 4) * 2)
elif DESIGNED_CODE:
    bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM * 3 + len(PREAMBLE_LIST)))
else:
    bit_arr = BitSlideArray(np.array([[]]), (BITS_NUM + len(PREAMBLE_STR)) * 2) # maintain frames within 2 seconds after interpolation
