#ifndef DISPLAY_WINUSB_MOUSECORE_H_
#define DISPLAY_WINUSB_MOUSECORE_H_


#ifndef USE_MOUSECORE_NATIVE
#include <libusb.h>
#include "libusb_utils.h"
  #ifdef MOUSECORE_NATIVE_ASYNC
    #error "cannot use native_async without native enabled."
  #endif

#else
#include "../common.h"
#include "usb_utils.h"
#include <windows.h>
#include <SetupAPI.h>
#endif

#include <stdint.h>
#include <functional>
#include <thread>
#include <vector>

struct MouseReport {
  uint8_t flags;
  uint8_t button;
  int16_t xTrans;
  int16_t yTrans;
  int16_t wheel;
};

//this callback must be thread safe.
typedef std::function<void(int, MouseReport)> MOUSEREPORTCALLBACKFUNC;

#define MOUSECORE_EXTRACT_BUFFER(buffer, size, offset, type) \
  (((offset) + sizeof(type) <= (size)) ? *(type *)((uint8_t *)(buffer) + (offset)): (type) 0)

#define NUM_MOUSE_MAXIMUM 10

// const uint16_t default_vid = 0x046D;
// const uint16_t default_pid = 0xC077;

// const uint16_t default_vid = 0x046D;
// const uint16_t default_pid = 0xC019;

const uint16_t default_vid = 0x046D;
const uint16_t default_pid = 0xC05B;

//this is for mouse hid report
const int target_report_configuration = 0x01;
const int target_report_interface = 0x00;
const unsigned char target_report_endpoint = 0x81;

namespace npnx {
class MouseCore {
public:
  MouseCore();
  ~MouseCore();
  
  //return num_mouse
  int Init(uint16_t vid, uint16_t pid, MOUSEREPORTCALLBACKFUNC func);
  int ControlTransfer(int mouse_idx, uint8_t request_type, uint8_t bRequest, uint16_t wValue, uint16_t wIndex,
                      unsigned char *data, uint16_t wLength, unsigned int timeout);
  
  //start polling for all mouses.
  void Start();

private: 
  void poll(int idx);
  MouseReport raw_to_mousereport(uint8_t *buffer, size_t size);

private:

#ifndef USE_MOUSECORE_NATIVE
  libusb_device *devs[NUM_MOUSE_MAXIMUM];
  libusb_device_handle *devs_handle[NUM_MOUSE_MAXIMUM];
#else
  std::vector<PSP_DEVICE_INTERFACE_DETAIL_DATA> pInterface_details;
  std::vector<HANDLE> h_files, h_winusbs, h_hidinterfaces;
  inline WCHAR* GetDevicePath(int hDevice) {
    return &(pInterface_details[hDevice]->DevicePath[0]);
  }
#endif

  MOUSEREPORTCALLBACKFUNC mouseReportCallbackFunc;
  int num_mouse = 0;
  int hid_report_size = 0;

  bool shouldStop = false;
  std::thread pollThread[NUM_MOUSE_MAXIMUM];

}; 
}

#endif // !DISPLAY_WINUSB_MOUSECORE_H_
