#ifndef DISPLAY_TRANSLAYER_H_
#define DISPLAY_TRANSLAYER_H_

#include "layerobject.h"

namespace npnx {

class DragRectLayer: public RectLayer {
public:
  DragRectLayer(float left, float bottom, float right, float top, float z_index, bool centrosymmetric = false);
  virtual ~DragRectLayer() = default;

  virtual int DrawGL(const int nbFrames) override;

  bool isInside(double x, double y, const int nbFrames);  
public:
  float mATransX = 0, mATransY = 0;
  float mTransX = 0, mTransY = 0;
  float mLeft, mBottom, mRight, mTop;
  bool mCentrosymmetric; 
};

class SplittedRectLayer: public LayerObject {
public:
  SplittedRectLayer(float left, float bottom, float right, float top, float z_index, float splitLength);
  virtual ~SplittedRectLayer() = default;

  virtual int DrawGL(const int nbFrames) override;

public:
  std::function<unsigned int(const int)> textureNoCallback = [] (const int) {return 0;};
  std::vector<GLuint> mTexture;
};

}

#endif

