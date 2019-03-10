#include <Windows.h>
#include <cstdint>
#include <cstdio>
#include <string>
#include <iostream>

std::string fileOutput = "";

void printTime() {
  SYSTEMTIME loct;
  FILETIME systf;
  FILETIME loctf;
  GetSystemTimePreciseAsFileTime(&systf);
  FileTimeToLocalFileTime(&systf, &loctf);
  FileTimeToSystemTime(&loctf, &loct);
  int64_t loctfi64 = (int64_t)loctf.dwHighDateTime * 4294967296LL + (int64_t)*(uint32_t *)&loctf.dwLowDateTime; 
  int microseconds = loctfi64 % 10000000;
  char newTime[1024];
  sprintf(newTime, "%d:%d:%d.%d\n", loct.wHour, loct.wMinute, loct.wSecond, microseconds);
  fileOutput += newTime;
}

int main(){
  fileOutput.reserve(2000000);
  for (int i = 0; i<1000; i++) {
    printTime();
    printTime();
    printTime();
  }
  std::cout<< fileOutput;

  return 0;
}