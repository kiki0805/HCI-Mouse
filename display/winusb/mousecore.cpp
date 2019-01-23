#include "mousecore.h"

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <libusb.h>
#include "libusb_utils.h"

using namespace npnx;

MouseCore::MouseCore() {
  memset(devs, 0x00, NUM_MOUSE_MAXIMUM * sizeof(libusb_device *));
  memset(devs_handle, 0x00, NUM_MOUSE_MAXIMUM * sizeof(libusb_device_handle *));
  mouseReportCallbackFunc = NULL;
}

MouseCore::~MouseCore() {
  shouldStop = true;
  //here join all the thread.
  for (int i=0; i< NUM_MOUSE_MAXIMUM; i++) {
    if (devs_handle[i] != NULL) {
      libusb_release_interface(devs_handle[i], target_report_interface);
      libusb_close(devs_handle[i]);
      devs_handle[i] = NULL;
    }
  }
}

//return num_mouse
int MouseCore::Init(uint16_t vid, uint16_t pid, MOUSEREPORTCALLBACKFUNC func) {
  mouseReportCallbackFunc = func;

  libusb_device **dev_list;
  int cnt;
  int ret; // return value;
  unsigned char buf[4096]; //WinUSB only support up to 4kb buffer. Larger is useless.

  LIBUSB_ASSERTCALL(libusb_init(NULL));
  
  cnt = (int) libusb_get_device_list(NULL, &dev_list);
  LIBUSB_CHECK_RET(libusb_get_device_list, cnt);

  for (int i = 0; i < cnt; i++) {
    print_device(dev_list[i], 0);
    libusb_device_descriptor desc;
    LIBUSB_ASSERTCALL(libusb_get_device_descriptor(dev_list[i], &desc));
    if (desc.idVendor == vid, desc.idProduct == pid) {
      printf("found target\n");
      devs[num_mouse++] = dev_list[i];
      LIBUSB_ASSERTCALL(libusb_open(devs[num_mouse - 1], &devs_handle[num_mouse - 1]));
      if (num_mouse > NUM_MOUSE_MAXIMUM) break;
    }
  } 
  
  libusb_free_device_list(dev_list, 1);

  for (int i = 0; i < num_mouse; i++) {
    printf("device %d: \n", i);

    cnt = libusb_get_descriptor(devs_handle[i], LIBUSB_DT_DEVICE, 0, buf, 4096);
    LIBUSB_CHECK_RET_BUFFER(mousecore_device_descriptor, cnt, buf);

    cnt = libusb_get_descriptor(devs_handle[i], LIBUSB_DT_CONFIG, 0, buf, 4096);
    LIBUSB_CHECK_RET_BUFFER(mousecore_config_descriptor, cnt, buf);
    
    cnt = libusb_control_transfer(devs_handle[i], 0x81, 0x06, 0x2100, 0, buf, 1024, 1000);
    LIBUSB_CHECK_RET_BUFFER(mousecore_hid_descriptor, cnt, buf);

    cnt = libusb_control_transfer(devs_handle[i], 0x81, 0x06, 0x2200, 0, buf, 1024, 1000);
    LIBUSB_CHECK_RET_BUFFER(mousecore_hid_report_descriptor, cnt, buf);
    hid_report_size = get_hid_record_size(buf, cnt, HID_REPORT_TYPE_INPUT);

    printf("\n");

    LIBUSB_ASSERTCALL(libusb_set_configuration(devs_handle[i], target_report_configuration));
    LIBUSB_ASSERTCALL(libusb_claim_interface(devs_handle[i], target_report_interface));
    
    pollThread[i] = std::thread([&, this] (int idx) {poll(idx);}, i);
  }
  
  return num_mouse;
}

int MouseCore::ControlTransfer(int mouse_idx, uint8_t request_type, uint8_t bRequest, uint16_t wValue, uint16_t wIndex,
                    unsigned char *data, uint16_t wLength, unsigned int timeout) {
  return libusb_control_transfer(devs_handle[mouse_idx], request_type, bRequest, wValue, wIndex, data, wLength > 4096 ? 4096: wLength, timeout);
}


void MouseCore::poll(int idx) {
  while (!shouldStop) {
    int ret, cnt;
    unsigned char buf[1024];
    ret = libusb_interrupt_transfer(devs_handle[idx], target_report_endpoint, buf, hid_report_size, &cnt, 1);
    if (ret == LIBUSB_ERROR_TIMEOUT) continue;
    if (ret < 0) {
      printf("%d device polling failed: %s", idx, libusb_error_name(ret));
      exit(ret);
    } else if (cnt > 0) {
      mouseReportCallbackFunc(idx, raw_to_mousereport(buf, cnt));
    }
  }
}

MouseReport MouseCore::raw_to_mousereport(uint8_t *buffer, size_t size) {
  MouseReport result;
  memset(&result, 0, sizeof(MouseReport));
  result.flags = MOUSECORE_EXTRACT_BUFFER(buffer, size, 0, uint8_t);
  result.button = MOUSECORE_EXTRACT_BUFFER(buffer, size, 1, uint8_t);
  result.xTrans = MOUSECORE_EXTRACT_BUFFER(buffer, size, 2, int16_t);
  result.yTrans = MOUSECORE_EXTRACT_BUFFER(buffer, size, 4, int16_t);
  result.wheel = MOUSECORE_EXTRACT_BUFFER(buffer, size, 6, int16_t);
  return result;
}
