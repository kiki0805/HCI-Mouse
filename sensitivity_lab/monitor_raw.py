pct = input('pct: ')
snr = '-'#input('SNR: ')
base_color = input('base color: ')
FILE_NAME = '_'.join(['data233', 'fdiff', pct, snr, base_color])
import os
count = 0
while os.path.exists(FILE_NAME + str(count) + '.csv'):
    count += 1
FILE_NAME = FILE_NAME + str(count) + '.csv'

print('FILE NAME:', FILE_NAME)
# FILE_NAME = None

import usb.core
import re
import sys
import threading
from multiprocessing import Process, Queue
import time
import math
import numpy as np
import usb.util
from setting import *
from utils import *

if not FILE_NAME:
    
    dur = input('Duration: ')
    update_time = input('update time: _s ')
    update_time = -1 if update_time == '' else int(update_time)

    dur = 10 if dur == '' else int(dur)
else:
    dur = 999
    update_time = -1
idVendor = 0x046d
idProduct = 0xc077 # dell
# idProduct = 0xc019 # logitech without tag
# idProduct = 0xc05b # logitech with tag

device = usb.core.find(idVendor=idVendor, idProduct=idProduct)

if idProduct == 0xc077:
    # register = 0x0D # 0x0B
    register = 0x0B # average
else:
    register = 0x0B
if device.is_kernel_driver_active(0):
    device.detach_kernel_driver(0)

device.set_configuration()

def init():
    device.ctrl_transfer(bmRequestType = 0x40, #Write
                                         bRequest = 0x01,
                                         wValue = 0x0000,
                                        #  wIndex = 0x0D, #PIX_GRAB register value
                                         wIndex = register, #PIX_GRAB register value
                                         data_or_wLength = None
                                         )

start = time.time()

def update():
    global q, update_time
    if FILE_NAME:
        f = open(FILE_NAME, 'w')
    time1 = None
    print('started')
    while True:

        response, timestamp = q.get()
        if not time1:
            time1 = timestamp
        if not response:
            return

        val = int.from_bytes(response, 'big')
        val_fixed = val
        if register == 0x0D:
            if val_fixed < 128:
            # print('+ 128')
                val_fixed += 128
        # if val_fixed > 240:
        #    # print('delete')
        if FILE_NAME:
            f.write(str(val_fixed) + ','  + str(timestamp) + '\n')
            continue


q = Queue()
p = Process(target=update) # for display
p.start()


start = time.time()
global_count = 0
flag = 0
while time.time() - start < dur:
    t1 = time.time()
    response = device.ctrl_transfer(bmRequestType = 0xC0, #Read
                     bRequest = 0x01,
                     wValue = 0x0000,
                    #  wIndex = 0x0D, #PIX_GRAB register value
                     wIndex = register, #PIX_GRAB register value
                     data_or_wLength = 1
                     )
    # response2 = device.ctrl_transfer(bmRequestType = 0xC0, #Read
    #                  bRequest = 0x01,
    #                  wValue = 0x0000,
    #                 #  wIndex = 0x0D, #PIX_GRAB register value
    #                  wIndex = 0x09, #PIX_GRAB register value
    #                  data_or_wLength = 1
    #                  )
    if register == 0x0D:
        init()
    q.put((response, time.time()))
    # print(time.time() - t1)
    global_count += 1

print('Frame rate: ' + str(global_count / (time.time() - start)))
p.terminate()
# sys.exit()
