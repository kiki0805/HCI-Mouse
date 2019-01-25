#include "multimouse.h"
#include <cmath>

using namespace npnx;

MouseInstance::MouseInstance(MultiMouseSystem *parent, HANDLE hDevice):
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
  std::lock_guard<std::mutex> lck(objectMutex);
  mMousePosX = 0;
  mMousePosY = 0;
  mRotateMatrix[0][0] = cos(rotateInRad);
  mRotateMatrix[0][1] = -sin(rotateInRad);
  mRotateMatrix[1][0] = -mRotateMatrix[0][1];
  mRotateMatrix[1][1] = mRotateMatrix[0][0];
  mOriginInScreenCoordX = xCoord;
  mOriginInScreenCoordY = yCoord;
}

void MouseInstance::MovingFromReport(int x, int y) {
  std::lock_guard<std::mutex> lck(objectMutex);
  mMousePosX+=x;
  mMousePosY+=y;
}

void MouseInstance::GetCursorPos(double *x, double *y) {
  std::lock_guard<std::mutex> lck(objectMutex);
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
    if (iter.second) {
      delete iter.second;
    }
  }
  mouses.clear();
}

void MultiMouseSystem::Init(GLFWwindow *window){
  RAWINPUTDEVICE Rid[1];

  Rid[0].usUsagePage = 0x01;
  Rid[0].usUsage = 0x02;
  Rid[0].dwFlags = RIDEV_NOLEGACY; // adds HID mouse and also ignores legacy mouse messages
  Rid[0].hwndTarget = glfwGetWin32Window(window);

  if (RegisterRawInputDevices(Rid, 1, sizeof(Rid[0])) == FALSE)
  {
    //registration failed. Call GetLastError for the cause of the error
    NPNX_ASSERT(false && "registerRawInput");
  }

  UINT numHIDDevices = 0;

  UINT getRawInputDeviceListNumResult = GetRawInputDeviceList(NULL, &numHIDDevices, sizeof(RAWINPUTDEVICELIST));
  NPNX_ASSERT_LOG(getRawInputDeviceListNumResult != -1, GetLastError());

  NPNX_LOG(numHIDDevices);
  PRAWINPUTDEVICELIST hidDeviceList = new RAWINPUTDEVICELIST[numHIDDevices];

  UINT getRawInputDeviceListResult = GetRawInputDeviceList(hidDeviceList, &numHIDDevices, sizeof(RAWINPUTDEVICELIST));
  NPNX_ASSERT_LOG(getRawInputDeviceListResult != -1, GetLastError());

  for (int i = 0; i < numHIDDevices; i++)
  {
    if (true)//(hidDeviceList[i].dwType == RIM_TYPEMOUSE)
    {
      if(hidDeviceList[i].dwType == RIM_TYPEMOUSE) printf("mouse\n");
      UINT cbSize = 0;
      UINT getRawInputDeviceInfoNumResult = GetRawInputDeviceInfoW(hidDeviceList[i].hDevice, RIDI_DEVICENAME, NULL, &cbSize);
      NPNX_ASSERT_LOG(getRawInputDeviceInfoNumResult != -1, GetLastError());
      WCHAR *tempbuffer = (WCHAR *)calloc(1, sizeof(WCHAR) * cbSize);
      UINT getRawInputDeviceInfoResult = GetRawInputDeviceInfoW(hidDeviceList[i].hDevice, RIDI_DEVICENAME, tempbuffer, &cbSize);
      NPNX_ASSERT_LOG(getRawInputDeviceInfoResult != -1, GetLastError());
      printf("%ls\r\n", tempbuffer);
      free(tempbuffer);
    }
  }

  mInitialized = true;
}

void MultiMouseSystem::GetCursorPos(HANDLE hDevice, double *x, double *y) {
  mouses[hDevice]->GetCursorPos(x,y);
}

void MultiMouseSystem::RegisterMouseRenderer(Renderer *renderer, std::function<bool(int)> defaultVisibleFunc){
  mouseRenderer = renderer;
  originalMouseVisibleFunc = defaultVisibleFunc;
  mRenderered = true;
}

void MultiMouseSystem::CheckNewMouse(HANDLE hDevice)
{
  NPNX_ASSERT(mInitialized && mRenderered);
  if (mouses.find(hDevice) == mouses.end()) {
    if (GetNumMouse() == cNumLimit) return;
    mouses[hDevice] = new MouseInstance(this, hDevice);
    int layerIndex = GetNumMouse() - 1;
    LayerObject *cursorLayer = mouseRenderer->mLayers[*(float *) &layerIndex];
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
}

namespace npnx {

MultiMouseSystem multiMouseSystem;

}