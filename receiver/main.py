import collections
import random
import settings
import time
from multiprocessing import Process, Queue
from test_utils import TestPrinter

test_printer = TestPrinter(settings.TEST_PRINTER)


def figure_handler(data):
    import figure_utils
    # Register Line and Corresponding Data
    manager = figure_utils.GraphicsManager()
    manager.register('uniform_data', settings.POINTS_PER_SAMPLE * 10) # 10 samples
    manager.register('mean', settings.POINTS_PER_SAMPLE * 10)
    manager.register('binary_data', settings.POINTS_PER_SAMPLE * 10)
    manager.register('samples', 10, scatter=True)

    start = time.time()
    current = time.time()
    while current - start < settings.duration + 10:
        # Get New Data Point
        uniform_point = data['uniform_data'].get()
        mean_point = data['mean'].get()
        binary_point = data['binary_data'].get()
        sample = data['samples'].get()
        
        # current = point[0] # (timestamp, value)
        current = time.time()

        # Update Data and Corresponding Line
        manager.update('uniform_data', uniform_point)
        manager.update('mean', mean_point)
        manager.update('binary_data', binary_point)
        manager.update('samples', sample)


def report_handler():
    while True:
        time.sleep(1)


def dsp_handler(raw_queue, data):
    import DSP_utils
    # Register Data
    manager = DSP_utils.DataManager()
    manager.register_data('raw_data', settings.CUT_INTERVAL * settings.POINTS_AFTER_INTERPOLATION * 2)
    manager.register_data('uniform_data', settings.POINTS_PER_SAMPLE + settings.MEAN_WIDTH)
    manager.register_data('mean', settings.POINTS_PER_SAMPLE)
    manager.register_data('binary_data', settings.POINTS_PER_SAMPLE) # One Bit

    start = time.time()
    current = time.time()
    while current - start < settings.duration + 3:
        response, timestamp = raw_queue.get()
        current = timestamp

        # Fix Raw Value
        val_fixed = DSP_utils.fix_raw_value(response)
        if not val_fixed:
            continue
        
        # Interpolation

        # Averaging

        # Update Threshold

        # Binarization

        # Sampling

        # Update Graphics Data
        if settings.GRAPHICS:
            pass


if __name__ == '__main__':
    # Shared Data & Processes Initialization
    raw_queue = Queue() # Main to DSP Process (dsp_handler)
    data = {} # Graphics & Report Data

    # DSP Process to Graphics Process (figure_handler)
    data['uniform_data'] = Queue() # Data after interpolation and averaging
    data['mean'] = Queue() # Threshold for binarization
    data['binary_data'] = Queue() # Data after binarization
    data['samples'] = Queue()
    
    if settings.GRAPHICS:
        figure_p = Process(target=figure_handler, args=(data, ))
        figure_p.start()
    if settings.REPORT:
        report_p = Process(target=report_handler)
        report_p.start()
    dsp_p = Process(target=dsp_handler, args=(raw_queue, data))
    dsp_p.start()

    # Device Initialization
    if not settings.VIRTUAL_INPUT:
        import usb.core
        import usb.util
        device = usb.core.find(idVendor=settings.idVendor, idProduct=settings.idProduct)
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
        device.set_configuration()
    else:
        # For Virtual Input
        from test_utils import read_virtual_mouse

    # USB Reading Loop
    from device_utils import reset_device, read_device
    start = time.time()
    count = 0
    while time.time() - start < settings.duration:
        if settings.VIRTUAL_INPUT:
            # Virtual Input
            response = read_virtual_mouse(settings.APPROXIMATE_FRAME_RATE)
        else:
            reset_device(device)
            response = read_device(device)
        raw_queue.put((response, time.time()))
        count += 1
    print('Frame rate: ' + str(count / (time.time() - start)))

    # Kill/Wait Processes
    time.sleep(2)
    dsp_p.terminate()
    if settings.REPORT:
        report_p.terminate()
    if settings.GRAPHICS:
        figure_p.join()

