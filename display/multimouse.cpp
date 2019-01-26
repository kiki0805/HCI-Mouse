#include "multimouse.h"
#include "winusb/mousecore.h"
#include <cmath>

using namespace npnx;

MouseInstance::MouseInstance(MultiMouseSystem *parent, int hDevice):
  mParent(parent), 
  mDeviceHandle(hDevice)
{
  NPNX_ASSERT_LOG(parent, "MouseInstance no parent");

  mRotateMatrix[0][0] = cos(0);
  mRotateMatrix[0][1] = -sin(0);
  mRotateMatrix[1][0] = -mRotateMatrix[0][1];
  mRotateMatrix[1][1] = mRotateMatrix[0][0];
}

void MouseInstance::SetMouseState(double rotateInRad,double xCoord,double yCoord) {
  //set mouse coord to origin, and then set the origin in screencoord.
  std::lock_guard<std::recursive_mutex> lck(objectMutex);
  mMousePosX = 0;
  mMousePosY = 0;
  mRotateMatrix[0][0] = cos(rotateInRad);
  mRotateMatrix[0][1] = -sin(rotateInRad);
  mRotateMatrix[1][0] = -mRotateMatrix[0][1];
  mRotateMatrix[1][1] = mRotateMatrix[0][0];
  mOriginInScreenCoordX = xCoord;
  mOriginInScreenCoordY = yCoord;
}

void MouseInstance::HandleReport(const MouseReport & report) {
  std::lock_guard<std::recursive_mutex> lck(objectMutex);
  mMousePosX+=report.xTrans;
  mMousePosY+=report.yTrans;
  if (report.button != mHidLastButton){
    for (int i=0; i<7; i++) {
      if ((report.button & (1 << i)) ^ (mHidLastButton & (1 << i))) {
        double x,y;
        GetCursorPos(&x, &y);
        mParent->fifo.Push({mDeviceHandle, report.button, (report.button & (1 << i)) >> i, x, y});
      }
    }
    mHidLastButton = report.button;
  }
}

void MouseInstance::SetLastPush(uint8_t button, int action, double screenX, double screenY){
  // I think lastpush info is written and read only by main thread (set is from fifo.)
  // std::lock_guard<std::recursive_mutex> lck(objectMutex);
  if (action == GLFW_PRESS) {mPushedButton |= button;}
  else { mPushedButton &= (~button);}
  mLastPushPosInScreenX = screenX;
  mLastPushPosInScreenY = screenY;
}

void MouseInstance::GetLastPush(uint8_t *button, double *screenX, double *screenY){
  // std::lock_guard<std::recursive_mutex> lck(objectMutex);
  *button = mPushedButton;
  *screenX = mLastPushPosInScreenX;
  *screenY = mLastPushPosInScreenY;
}

void MouseInstance::GetCursorPos(double *x, double *y) {
  std::lock_guard<std::recursive_mutex> lck(objectMutex);
  *x = mMousePosX * mRotateMatrix[0][0] + mMousePosY * mRotateMatrix[0][1];
  *x *= mParent->mSensitivityX;
  *x += mOriginInScreenCoordX;
  *x = (*x - WINDOW_WIDTH / 2) / (WINDOW_WIDTH / 2);

  *y = mMousePosX * mRotateMatrix[1][0] + mMousePosY * mRotateMatrix[1][1];
  *y *= mParent->mSensitivityY;
  *y += mOriginInScreenCoordY;
  *y = - (*y - WINDOW_HEIGHT / 2) / (WINDOW_HEIGHT / 2);
}

MultiMouseSystem::MultiMouseSystem() {
  mouses.clear();
}

MultiMouseSystem::~MultiMouseSystem(){
  for (auto iter: mouses) {
    if (iter) {
      delete iter;
    }
  }
  mouses.clear();
}

void MultiMouseSystem::Init(MOUSEBUTTONCALLBACKFUNC func)
{
  NPNX_ASSERT(!mInitialized);
  mouseButtonCallback = func;
  num_mouse = core.Init(default_vid, default_vid, [&, this] (int idx, MouseReport report) -> void {this->reportCallback(idx, report);});
  mInitialized = true;
}

void MultiMouseSystem::GetCursorPos(int hDevice, double *x, double *y) {
  mouses[hDevice]->GetCursorPos(x,y);
}

void MultiMouseSystem::RegisterMouseRenderer(Renderer *renderer, std::function<bool(int)> defaultVisibleFunc){
  NPNX_ASSERT(!mRenderered);
  NPNX_ASSERT(mInitialized);
  mouseRenderer = renderer;
  originalMouseVisibleFunc = defaultVisibleFunc;
  mRenderered = true;

  for (int i = 0; i < num_mouse; i++) {
    checkNewMouse(i);
  }
  core.Start();
}

void MultiMouseSystem::checkNewMouse(int hDevice)
{
  mouses.push_back(new MouseInstance(this, hDevice));
  LayerObject *cursorLayer = mouseRenderer->mLayers[*(float *) &hDevice];
  cursorLayer->beforeDraw = [=](int nbFrames) {
    double x, y;
    this->GetCursorPos(hDevice, &x, &y);
    glUniform1f(glGetUniformLocation(cursorLayer->mParent->mDefaultShader->mShader, "xTrans"), x);
    glUniform1f(glGetUniformLocation(cursorLayer->mParent->mDefaultShader->mShader, "yTrans"), y);
    return 0;
  };
  cursorLayer->afterDraw = [=](int nbFrames) {
    glUniform1f(glGetUniformLocation(cursorLayer->mParent->mDefaultShader->mShader, "xTrans"), 0.0f);
    glUniform1f(glGetUniformLocation(cursorLayer->mParent->mDefaultShader->mShader, "yTrans"), 0.0f);
    return 0;
  };
  cursorLayer->visibleCallback = originalMouseVisibleFunc;
}

void MultiMouseSystem::PollMouseEvents() {
  MouseFifoReport report;
  while (fifo.Pop(&report)){
    mouseButtonCallback(report.hDevice, report.button, report.action, report.screenX, report.screenY);
  }
}

//this must be thread safe for diffrent mouse.
void MultiMouseSystem::reportCallback(int hDevice, MouseReport report){
  mouses[hDevice]->HandleReport(report);
}

namespace npnx {

MultiMouseSystem multiMouseSystem;

}