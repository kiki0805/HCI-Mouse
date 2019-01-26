import re
import sys
from interpolate_f import interpolate_f
import threading
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
import time
import math
import numpy as np
from setting import *
from utils import *



class SlideArray:
    def __init__(self, window, size, line, draw_interval, ele_type='coordiante', location_mod=False, sample_line=None, scatter_mode=False):
        self.scatter_mode = scatter_mode
        self.sample_line = sample_line
        self.window = window
        self.draw_interval = draw_interval
        self.line = line
        self.size = size
        self.last_detected = -1
        self.location_mod = location_mod
        self.init_timestamp = None
        self.window_of_last_one = None
        self.window_of_last_zero = None

    def push(self, chunk_or_ele): # chunk for coordinate, ele for binary bits
        assert chunk_or_ele.size <= self.size * 2
        if self.window.size + chunk_or_ele.size > self.size * 2:
            self.window = self.window[int((chunk_or_ele.size + self.window.size) - self.size * 2):]
        if self.window.size == 0:
            self.window = chunk_or_ele
        else:
            self.window = np.concatenate((self.window, chunk_or_ele))

    def is_full(self):
        if self.window.size > self.size * 2:
            print('outflow')
        return self.window.size == self.size * 2

    def update_line_data(self):
        if self.line is None:
            return
        if self.window.size == 0:
            return

        x, y = divide_coordinate(self.window)
        if x.size < self.draw_interval:
            if self.scatter_mode:
                self.line.set_offsets(self.window)
                return
            self.line.set_xdata(x)
            self.line.set_ydata(y)
        else:
            if self.scatter_mode:
                self.line.set_offsets(self.window[-self.draw_interval:,:])
                return
            self.line.set_xdata(x[-self.draw_interval:])
            self.line.set_ydata(y[-self.draw_interval:])

def update(q):
    plt.ion()
    line1 = None
    # line1, = plt.plot([], [], 'r', label='original') 
    ax = plt.gca() # get most of the figure elements 
    update_time = -1
    raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, line1, int(MOUSE_FRAME_RATE * 0.05))
    # raw_frames_m = SlideArray(np.array([[]]), MOUSE_FRAME_RATE * 2, line1, MOUSE_FRAME_RATE)
    time1 = None
    while True:

        response, timestamp = q.get()
        if not time1:
            time1 = timestamp
        if not response:
            return

        val = int.from_bytes(response, 'big')
        val_fixed = val
        if val_fixed < 128:
           # print('+ 128')
           val_fixed += 128
        # if val_fixed > 240:
        #    # print('delete')
        #    continue
        # print(val_fixed)
        raw_frames_m.push(np.array([[timestamp, val_fixed], ]))
        if raw_frames_m.line and timestamp - time1 > update_time:
            raw_frames_m.update_line_data()
            ax.relim() # renew the data limits
            ax.autoscale_view(True, True, True) # rescale plot view
            plt.draw() # plot new figure
            if update_time != -1:
                time1 = timestamp
                plt.pause(update_time)
            else:
                plt.pause(1e-6)

import win32file
import win32pipe
if __name__ == '__main__':
    q = Queue()

    start = time.time()
    p = Process(target=update,args=(q,)) # for display
    p.start()


    # start = time.time()
    global_count = 0
    PIPE_NAME = r'\\.\pipe\test_pipe'
    PIPE_BUFFER_SIZE = 1
    named_pipe = win32pipe.CreateNamedPipe(PIPE_NAME,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT | win32pipe.PIPE_READMODE_MESSAGE,
                    win32pipe.PIPE_UNLIMITED_INSTANCES,
                    PIPE_BUFFER_SIZE,
                    PIPE_BUFFER_SIZE, 500, None)
    while True:

        try:
            t1 = time.time()
            win32pipe.ConnectNamedPipe(named_pipe, None)
            data = win32file.ReadFile(named_pipe, PIPE_BUFFER_SIZE, None)
            if start is None:
                start = time.time()
            # if data is None or len(data) < 2:
            #     continue

            # print ('receive msg:', int.from_bytes(data[1], 'big'))
            q.put((data[1], time.time()))
            print(time.time()-t1)
        except BaseException as e:
            print ("exception:", e)
            break

        global_count += 1

    win32pipe.DisconnectNamedPipe(named_pipe)
    print('Frame rate: ' + str(global_count / (time.time() - start)))
    # p.terminate()
    sys.exit()
