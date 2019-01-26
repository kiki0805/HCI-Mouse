#ifndef DISPLAY_MOUSEFIFO_H_
#define DISPLAY_MOUSEFIFO_H_

#include <deque>
#include <mutex>
#include "winusb/mousecore.h"

namespace npnx {

struct MouseFifoReport {
  int hDevice, button, action;
  double screenX, screenY;
};

class MouseFifo {
public:
  MouseFifo() = default;
  ~MouseFifo() = default;

  inline void Push(const MouseFifoReport & report) {
    std::lock_guard<std::mutex> lck(objectMutex);
    data.push_back(report);
  } 

  inline bool Pop(MouseFifoReport *report) {
    std::lock_guard<std::mutex> lck(objectMutex);
    if (data.empty()) return false;
    *report = data.front();
    data.pop_front();
    return true;
  }

private:
  std::mutex objectMutex;
  std::deque<MouseFifoReport> data;
};

}

#endif // !DISPLAY_MOUSEFIFO_H_