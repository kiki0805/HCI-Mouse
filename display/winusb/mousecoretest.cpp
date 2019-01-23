#include "mousecore.h"
#include <windows.h> //for sleep

using namespace npnx;
MouseCore mouseCore;

void mouseReportCallback(int idx, MouseReport report) {
  printf("%d: %02hhx %02hhx %04hx %04hx %04hx\n", idx,
      report.flags, report.button, report.xTrans, report.yTrans, report.wheel);
}

int main() {
  mouseCore.Init(default_vid, default_pid, mouseReportCallback);
  Sleep(1000);
  unsigned char buf[4096];
  
  for(int i=0; i<10; i++) {
    int cnt = mouseCore.ControlTransfer(0, 0x81, 0x06, 0x2200, 0, buf, 1024, 1000);
    LIBUSB_CHECK_RET_BUFFER(main_control_tranfer, cnt, buf);
    Sleep(1);
  }

  Sleep(3000);
  return 0;
}