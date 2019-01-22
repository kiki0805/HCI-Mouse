#ifndef DISPLAY_TRANSLAYER_H_
#define DISPLAY_TRANSLAYER_H_

#include "layerobject.h"

namespace npnx {

class DragRectLayer: public RectLayer {
public:
  DragRectLayer(float left, float bottom, float right, float top, float z_index);
  virtual ~DragRectLayer() = default;

  virtual int DrawGL(const int nbFrames) override;

  bool isInside(double x, double y, const int nbFrames);  
public:
  float mATransX = 0, mATransY = 0;
  float mTransX = 0, mTransY = 0;
  float mLeft, mBottom, mRight, mTop;
};

}

#endif

