
def get_mouse_data():
    import win32file
    import win32pipe

    PIPE_NAME = r'\\.\pipe\test_pipe'
    PIPE_BUFFER_SIZE = 1


    while True:
        named_pipe = win32pipe.CreateNamedPipe(PIPE_NAME,
                                                win32pipe.PIPE_ACCESS_DUPLEX,
                                                win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT | win32pipe.PIPE_READMODE_MESSAGE,
                                                win32pipe.PIPE_UNLIMITED_INSTANCES,
                                                PIPE_BUFFER_SIZE,
                                                PIPE_BUFFER_SIZE, 500, None)

        while True:
            try:
                win32pipe.ConnectNamedPipe(named_pipe, None)
                data = win32file.ReadFile(named_pipe, PIPE_BUFFER_SIZE, None)

                # if data is None or len(data) < 2:
                #     continue

                print ('receive msg:', int.from_bytes(data[1], 'big'))
            except BaseException as e:
                print ("exception:", e)
                break
        win32pipe.DisconnectNamedPipe(named_pipe)
