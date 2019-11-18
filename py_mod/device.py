import usb.core
import time
import math
import numpy as np
import usb.util

'''
# Used to sample the pixel register synchronously

mouse = Mouse() # to indicate parameters when in need
while True:
    print(mouse.sample())
'''
class Mouse:
    def __init__(self, idVendor=0x046d, idProduct=0xc077, pixel_register=0x0D):
        self.device = usb.core.find(idVendor=idVendor, idProduct=idProduct)

        if self.device.is_kernel_driver_active(0):
            self.device.detach_kernel_driver(0)

        self.device.set_configuration()
        self.register = pixel_register
    
    def write_register(self):
        self.device.ctrl_transfer(
            bmRequestType = 0x40, #Write
            bRequest = 0x01,
            wValue = 0x0000,
            wIndex = self.register, #PIX_GRAB register value
            data_or_wLength = None
        )
    
    def read_register(self):
        response = self.device.ctrl_transfer(bmRequestType = 0xC0, #Read
            bRequest = 0x01,
            wValue = 0x0000,
            wIndex = self.register, #PIX_GRAB register value
            data_or_wLength = 1
        )
        return response
    
    def sample(self):
        self.write_register()
        point = self.read_register()
        return time.time(), point
