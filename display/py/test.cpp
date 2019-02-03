#define UNICODE

#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <time.h>

int main(int argc, char *argv[]) {
  for(int i=0; i<argc; i++){
    printf("%s\n", argv[i]);
  }
  if (argc < 4) return 0;
  WCHAR inPipeName[4096], outPipeName[4096];
  mbstowcs(inPipeName, argv[2], 4095);
  mbstowcs(outPipeName, argv[3], 4095);
  HANDLE hInpipe = CreateFile(inPipeName, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);
  HANDLE hOutpipe = CreateFile(outPipeName, GENERIC_READ | GENERIC_WRITE, 0, NULL, OPEN_EXISTING, 0, NULL);
  if (hOutpipe == INVALID_HANDLE_VALUE){
    printf("%d\n", GetLastError());
    return 0;
  }
  int count = 0;
  clock_t tt = clock();
  while (true) {
    count ++ ;
    unsigned char buf[4096];
    DWORD length;
    if (!ReadFile(hInpipe, buf, 4096, &length, NULL)){
      return 0;
    }
    if (count % 1000 != 0) {
      // for (int i=0; i<length;  i++) {
      //   printf("%02hhX ", buf[i]);
      // }
      // if (length != 0 )printf("\n");
    }
    if (clock() - tt > 3 * CLOCKS_PER_SEC) {
      // unsigned char buf[] = {0, 2, 0, 0, 0, 0}; //do not forget little-endian
      // unsigned char buf[] = {0, 1, 90, 0, 255, 1}; 
      unsigned char buf[] = {0, 0, 255, 1, 255, 1}; 
      DWORD length;
      if (!WriteFile(hOutpipe, buf, 6, &length, NULL)) {
        return 0;
      }
      tt = clock();
    }
  }
  return 0;
}
