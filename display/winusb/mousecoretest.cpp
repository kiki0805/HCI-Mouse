#include "mousecore.h"
#include <windows.h> //for sleep
#include <iostream>
#include <string>

using namespace npnx;
using namespace std;
MouseCore mouseCore;

string fileOutput = "";

void printTime(int id) {
  SYSTEMTIME loct;
  FILETIME systf;
  FILETIME loctf;
  GetSystemTimePreciseAsFileTime(&systf);
  FileTimeToLocalFileTime(&systf, &loctf);
  FileTimeToSystemTime(&loctf, &loct);
  int64_t loctfi64 = (int64_t)loctf.dwHighDateTime * 4294967296LL + (int64_t)*(uint32_t *)&loctf.dwLowDateTime; 
  int microseconds = loctfi64 % 10000000;
  char newTime[1024];
  sprintf(newTime, "%d %d:%d:%d.%07d\n", id, loct.wHour, loct.wMinute, loct.wSecond, microseconds);
  fileOutput += newTime;
}

void mouseReportCallback(int idx, MouseReport report) {
  //printf("%d: %02hhx %02hhx %04hx %04hx %04hx\n", idx,
  //    report.flags, report.button, report.xTrans, report.yTrans, report.wheel);
}

int main() {
  fileOutput.reserve(2000000);
  int count = mouseCore.Init(default_vid, default_pid, mouseReportCallback);
  // mouseCore.Start();

  Sleep(1000);
  unsigned char bufs[1024];
  unsigned char buf[1];
  HANDLE hPipe;
  DWORD dwWritten;
  for (int i = 0; i < 1000; i++) {
    printTime(1);
    int cnt = mouseCore.ControlTransfer(0, 0xC0, 0x01, 0x0000, 0x0D, buf, 1, 1000);
    printTime(2);
  }
  std::cout << fileOutput << std::endl;
  return 0;
}