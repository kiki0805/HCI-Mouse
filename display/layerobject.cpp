#include "layerobject.h"
#include "renderer.h"
#include "shader.h"

using namespace npnx;

LayerObject::LayerObject(float z):
mParent(NULL),
z_index(z)
{}

LayerObject::~LayerObject() {}

RectLayer::RectLayer(float left, float bottom, float right, float top, float z)
: LayerObject(z) 
{
  mVBOBuffer.assign({
    left, bottom, 1.0f, 0.0f, 0.0f,
    right, bottom, 1.0f, 1.0f, 0.0f,
    right, top, 1.0f, 1.0f, 1.0f,
    left, top, 1.0f, 0.0f, 1.0f
  });
  mEBOBuffer.assign({
    0,1,2,
    0,2,3
  });
}

RectLayer::~RectLayer() {}

int RectLayer::Initialize(const int VBOOffset, const int EBOOffset)
{
  for (auto it: mVBOBuffer) {
    mParent->mVBOBuffer.push_back(it);
  }
  for (auto it: mEBOBuffer) {
    mParent->mEBOBuffer.push_back(VBOOffset+it);
  }
  mVBOOffset = VBOOffset;
  mEBOOffset = EBOOffset;
  return 0;
}

int RectLayer::Draw(const int nbFrames)
{
  if (!visibleCallback(nbFrames)) return 0;
  glActiveTexture(GL_TEXTURE0);
  glBindTexture(GL_TEXTURE_2D, mTexture);
  glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, (void *)(mEBOOffset * sizeof(GLuint)));
  return 0;
}

