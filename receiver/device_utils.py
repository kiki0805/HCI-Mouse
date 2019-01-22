def reset_device(device):
    device.ctrl_transfer(bmRequestType = 0x40, #Write
                        bRequest = 0x01,
                        wValue = 0x0000,
                        wIndex = 0x0D, #PIX_GRAB register value
                        data_or_wLength = None
                        )

def read_device(device):
    return device.ctrl_transfer(bmRequestType = 0xC0, #Read
                        bRequest = 0x01,
                        wValue = 0x0000,
                        wIndex = 0x0D, #PIX_GRAB register value
                        data_or_wLength = 1
                        )
