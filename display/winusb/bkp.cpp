#include "mousecore.h"
#include <windows.h> //for sleep
#include <iostream>
#include <time.h>
#include <ctime>

using namespace npnx;
using namespace std;
MouseCore mouseCore;

void mouseReportCallback(int idx, MouseReport report) {
  //printf("%d: %02hhx %02hhx %04hx %04hx %04hx\n", idx,
  //    report.flags, report.button, report.xTrans, report.yTrans, report.wheel);
}

int main() {
  int count = mouseCore.Init(default_vid, default_pid, mouseReportCallback);
  Sleep(1000);
  unsigned char buf[1];
  HANDLE hPipe;
  DWORD dwWritten;


  hPipe = CreateFile(TEXT("\\\\.\\pipe\\test_pipe"),
	  GENERIC_READ | GENERIC_WRITE,
	  0,
	  NULL,
	  OPEN_EXISTING,
	  0,
	  NULL);
  
  // for(int i=0; i<count; i++) {
  //   // int cnt = mouseCore.ControlTransfer(i, 0x81, 0x06, 0x2200, 0x00, buf, 1024, 1000);
  //   int cnt = mouseCore.ControlTransfer(i, 0xC0, 0x01, 0x0000, 0x0D, buf, 1024, 1000);
  //   LIBUSB_CHECK_RET_BUFFER(main_control_tranfer, cnt, buf);
  //   Sleep(1);
  // }

  int cnt;
  // cnt = mouseCore.ControlTransfer(0, 0x40, 0x01, 0x0000, 0x010D, buf, 1, 1000);
  clock_t begin = clock();

  if (hPipe == INVALID_HANDLE_VALUE)
  {
	  printf("Create Pipe Error(%d)\n", GetLastError());
  }
  while((clock() - begin) / (float)CLOCKS_PER_SEC < 5) {
	  // for (int i = 0; i < 19 * 19; i++) {
		//   cnt = mouseCore.ControlTransfer(0, 0xC0, 0x01, 0x0000, 0x0D, buf, 1, 1000);
    //   WriteFile(hPipe, buf, 1, &dwWritten, NULL);
    //   Sleep(1.5);
	  // }

    cnt = mouseCore.ControlTransfer(0, 0x40, 0x01, 0x0000, 0x010D, buf, 1, 1000);
    cnt = mouseCore.ControlTransfer(0, 0xC0, 0x01, 0x0000, 0x0D, buf, 1, 1000);
    WriteFile(hPipe, buf, 1, &dwWritten, NULL);
  }
  CloseHandle(hPipe);
  return 0;
}