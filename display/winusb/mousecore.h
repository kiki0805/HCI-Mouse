#ifndef DISPLAY_WINUSB_MOUSECORE_H_
#define DISPLAY_WINUSB_MOUSECORE_H_

#include <stdint.h>
#include <functional>
#include <thread>

#include <libusb.h>
#include "libusb_utils.h"

struct MouseReport {
  uint8_t flags;
  uint8_t button;
  int16_t xTrans;
  int16_t yTrans;
  int16_t wheel;
};

//this callback must be thread safe.
typedef std::function<void(int, MouseReport)> MOUSEREPORTCALLBACKFUNC;

#define MOUSECORE_EXTRACT_BUFFER(buffer, size, offset, type) (((offset) + sizeof(type) <= (size)) ? *(type *)((uint8_t *)(buffer) + (offset)): (type) 0)

#define NUM_MOUSE_MAXIMUM 10

const uint16_t default_vid = 0x04D9;
const uint16_t default_pid = 0xA070;

//this is for mouse hid report
const int target_report_configuration = 0x01;
const int target_report_interface = 0x01;
const unsigned char target_report_endpoint = 0x82;

namespace npnx {
class MouseCore {
public:
  MouseCore();
  ~MouseCore();
  
  //return num_mouse
  int Init(uint16_t vid, uint16_t pid, MOUSEREPORTCALLBACKFUNC func);
  int ControlTransfer(int mouse_idx, uint8_t request_type, uint8_t bRequest, uint16_t wValue, uint16_t wIndex,
                      unsigned char *data, uint16_t wLength, unsigned int timeout);
  
private: 
  void poll(int idx);
  MouseReport & raw_to_mousereport(uint8_t *buffer, size_t size);

public:

private:
  libusb_device *devs[NUM_MOUSE_MAXIMUM];
  libusb_device_handle *devs_handle[NUM_MOUSE_MAXIMUM];
  MOUSEREPORTCALLBACKFUNC mouseReportCallbackFunc;
  int num_mouse = 0;
  int hid_report_size = 0;
  bool shouldStop = false;
  std::thread pollThread[NUM_MOUSE_MAXIMUM];

}; 
}

#endif // !DISPLAY_WINUSB_MOUSECORE_H_
