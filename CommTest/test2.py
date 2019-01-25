import win32pipe, win32file
import time

PIPE_NAME =r'\\.\pipe\test_pipe'

file_handle = win32file.CreateFile(PIPE_NAME,
                                   win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                   win32file.FILE_SHARE_WRITE, None,
                                   win32file.OPEN_EXISTING, 0, None)
try:
    for i in range(1, 11):
        msg = str(i)
        print('send msg:', msg)
        win32file.WriteFile(file_handle, msg.encode())
        time.sleep(1)
finally:
    try:
        win32file.CloseHandle(file_handle)
    except:
        pass