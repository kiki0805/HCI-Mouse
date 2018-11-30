#ifndef DISPLAY_LAYEROBJECT_H_
#define DISPLAY_LAYEROBJECT_H_

#include "common.h"
#include <vector>
#include <functional>

namespace npnx {
using std::vector;

class Renderer;
class LayerObject {
public:
  explicit LayerObject(float z);
  virtual ~LayerObject();

  virtual int Initialize(const int VBOOffset, const int EBOOffset) = 0;
  virtual int Draw(const int nbFrames) = 0;

public: //avoid the tedious getter and setter functions. 
  vector<float> mVBOBuffer;
  vector<GLuint> mEBOBuffer;
  GLuint mVBOOffset, mEBOOffset;

  float z_index;
  Renderer *mParent;  
};

class RectLayer: public LayerObject{
public:
  RectLayer(float left, float bottom, float right, float top, float z_index);
  virtual ~RectLayer();

  virtual int Initialize(const int VBOOffset, const int EBOOffset);
  virtual int Draw(const int nbFrames);

public:
  std::function<bool(const int)> visibleCallback = [](int) { return true; };
  GLuint mTexture = 0;
};

} // namespace npnx

#endif // !DISPLAY_LAYEROBJECT_H_