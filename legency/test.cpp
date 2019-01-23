#include <iostream>
#include <ctime>
using namespace std;
int main() {
    time_t now = time(0);
    int a = 0;
    for(int i = 0; i < 90000; i++) {
        a++;
    }
    cout << time(0) - now <<endl;
    return 0;
}