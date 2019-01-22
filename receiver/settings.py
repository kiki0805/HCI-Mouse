"""
Configuration
NOTE:
    Variables that may be changed often.
"""
duration = 3 # seconds
VIRTUAL_INPUT = True
GRAPHICS = True
REPORT = False #True
TEST_PRINTER = False #True

"""
Constants
NOTE:
    Variables that are constant generally. 
    Be careful to change them.
"""

# Dell MS111
idVendor = 0x046d 
idProduct = 0xc077
APPROXIMATE_FRAME_RATE = 1800 # Fake Number For Test

FRAME_RATE = 240
POINTS_AFTER_INTERPOLATION = 9600
POINTS_PER_SAMPLE = 10
MEAN_WIDTH = 50
CUT_INTERVAL = 0.1
INTERPOLATION_INTERVAL = 0.08


"""
Variables
NOTE:
    Variables caculated from the above data.
    DO NOT set them manually.
"""

POINTS_TO_COMBINE = int(POINTS_AFTER_INTERPOLATION / FRAME_RATE / POINTS_PER_SAMPLE)
