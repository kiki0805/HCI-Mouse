import sys
import time
import win32pipe
import win32file
from multiprocessing import Queue, Process
from comm_handler import *

def pipe_client_read(pipe_name, q):
    print("pipe client for reading")
    handle = win32file.CreateFile(pipe_name,
        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        0, None, win32file.OPEN_EXISTING, 0, None)

    try:
        while True:
            resp = win32file.ReadFile(handle, 1)
            q.put(resp)
    except:
        win32file.CloseHandle(handle)

def pipe_client_write(pipe_name, q, idx):
    print("pipe client for writing")
    handle = win32file.CreateFile(pipe_name,
        win32file.GENERIC_READ | win32file.GENERIC_WRITE,
        win32file.FILE_SHARE_WRITE, None,
        win32file.OPEN_EXISTING, 0, None)
    
    try:
        while True:
            packet = q.get()
            packet_tagged = tagging_index(packet, idx)
            win32file.WriteFile(handle, packet_tagged)
    except:
        win32file.CloseHandle(handle)


def angl_detect(in_queue, out_queue):
    import angle
    measurer = angle.AngleMeasurer()

    while True:
        pixel_val = in_queue.get()
        ret = measurer.update(pixel_val)
        if ret is not None:
            out_queue.put(data_packing('angle', ret))


def loc_recog(in_queue, out_queue):
    import location
    localizer = location.Localizer()

    while True:
        val = in_queue.get()
        ret = localizer.update(val)
        if ret is not None:
            out_queue.put(data_packing('location', ret))

if __name__ == '__main__':
    # hci.py idx inpipe outpipe
    assert len(sys.argv) == 4

    MOUSE_INDEX = sys.argv[1]
    INPIPE_NAME = sys.argv[2]
    OUTPIPE_NAME = sys.argv[3]
    print('Detected arguments:', end=' ')
    print(MOUSE_INDEX, INPIPE_NAME, OUTPIPE_NAME)
    
    read_queue = Queue()
    write_queue = Queue()
    angl_queue = Queue()
    loc_queue = Queue()

    # create four processes
    read_process = Process(target=pipe_client_read, args=(INPIPE_NAME, read_queue))
    write_process = Process(target=pipe_client_write, args=(OUTPIPE_NAME, write_queue, MOUSE_INDEX))
    angl_process = Process(target=angl_detect, args=(angl_queue, write_queue))
    loc_process = Process(target=loc_recog, args=(loc_queue, write_queue))

    while True:
        # if read_queue.empty():
        #     continue
        read_data = read_queue.get()
        func, decoded_data = data_resolve(read_data)
        if func == 'angl':
            angl_queue.put(decoded_data)
        elif func == 'loc':
            loc_queue.put(decoded_data)

    
