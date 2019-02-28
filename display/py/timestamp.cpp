#include <chrono>
#include <ratio>
#include <cstdio>

int main(){
  uint8_t buf[255];
  printf( "%lld ", std::chrono::high_resolution_clock::now().time_since_epoch().count());
  int64_t nowtime = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::high_resolution_clock::now().time_since_epoch()).count();
  *(int64_t *)(buf+1) = nowtime;
  printf("%lld\n", nowtime);
  for(int ind = 0; ind < 10; ind++) {
    printf("%02hhx ", buf[ind]);
  }
  printf("\n");
  return 0;
}