#ifndef DISPLAY_MULTIMOUSE_H_
#define DISPLAY_MULTIMOUSE_H_

#include "common.h"
#include "layerobject.h"
#include "renderer.h"

#include <functional>
#include <map>

namespace npnx {

class MultiMouseSystem;

class MouseInstance {
public:
  MouseInstance(MultiMouseSystem *parent, HANDLE hDevice);
  ~MouseInstance() = default;

  // this is for HCI message.
  // the rotate angle is right to top in radian.
  //              |     /
  //              | a /
  //              |--/
  //              |/
  // ----------------------------
  //              |
  //              |
  //              |
  //              |
  //
  void SetMouseState(double rotate, double xCoord, double yCoord); 
  
  void GetCursorPos(double *x, double *y);

public:
  MultiMouseSystem *mParent = NULL;
  HANDLE mDeviceHandle = 0;
  
  RectLayer *cursorLayer;
  
  int mMousePosX = 0, mMousePosY = 0; // the mouse space coordinate

  //we want to know last press position on screen.                                    
  double mLastPushMouseInScreenX = 0.0, mLastPushMousePosInScreenY = 0.0; 
  //left push and right push is exclusive. when push got after another push, release first and then push.
  bool mLeftPushed = false, mRightPushed = false;
  
  //this is for transform from mouse input to screen
  //every time we get a rotate angle, we calc the matrix.
  double mRotateMatrix[2][2]; 
  double mOriginInScreenCoordX = WINDOW_WIDTH / 2, mOriginInScreenCoordY = WINDOW_HEIGHT / 2;

};

class MultiMouseSystem {
public:
  MultiMouseSystem();
  ~MultiMouseSystem();

  void Init(GLFWwindow *window); //register raw input for mouse equipments;
  void CheckNewMouse(HANDLE hDevice);  

  //renderer should have cNumLimit Rectlayers. 
  void RegisterMouseRenderer(Renderer* renderer, std::function<bool(int)> defaultVisibleFunc);

  void GetCursorPos(HANDLE hDevice, double *x, double *y);

public:
  static const size_t cNumLimit = 10;
  std::map<HANDLE, MouseInstance *> mouses;
  inline size_t GetNumMouse() { return mouses.size(); }
  double mSensitivityX = 1.0, mSensitivityY = 1.0;
  
private:
  Renderer *mouseRenderer;
  std::function<bool(int)> originalMouseVisibleFunc;

  bool mInitialized = false;
  bool mRenderered = false;
};

extern MultiMouseSystem multiMouseSystem;

} // namespace npnx
#endif // !DISPLAY_MULTIMOUSE_H_