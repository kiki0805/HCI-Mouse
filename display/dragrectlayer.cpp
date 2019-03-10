#include "dragrectlayer.h"
#include "renderer.h"

using namespace npnx;

DragRectLayer::DragRectLayer(float left, float bottom, float right, float top, float z_index, bool centrosymmetric):
  RectLayer(left, bottom, right, top, z_index),
  mLeft(left),
  mBottom(bottom),
  mRight(right),
  mTop(top),
  mCentrosymmetric(centrosymmetric)
{
}

int DragRectLayer::DrawGL(const int nbFrames) 
{
  NPNX_ASSERT(!mTexture.empty());

  glUniform1f(glGetUniformLocation(mParent->mDefaultShader->mShader, "xTrans"), mTransX+mATransX);
  glUniform1f(glGetUniformLocation(mParent->mDefaultShader->mShader, "yTrans"), mTransY+mATransY);

  if (mCentrosymmetric) {
    glUniform1i(glGetUniformLocation(mParent->mDefaultShader->mShader, "centrosymmetric"), 1);
  }
  glActiveTexture(GL_TEXTURE0);
  glBindTexture(GL_TEXTURE_2D, mTexture[textureNoCallback(nbFrames)]);
  glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, (void *)(mEBOOffset * sizeof(GLuint)));
  if (mCentrosymmetric) {
    glUniform1i(glGetUniformLocation(mParent->mDefaultShader->mShader, "centrosymmetric"), 0);
  }


  glUniform1f(glGetUniformLocation(mParent->mDefaultShader->mShader, "xTrans"), 0.0f);
  glUniform1f(glGetUniformLocation(mParent->mDefaultShader->mShader, "yTrans"), 0.0f);
  return 0;
}

bool DragRectLayer::isInside(double x, double y, const int nbFrames) {
  if (!visibleCallback(nbFrames)) return false;
  double dx = x - mTransX - mATransX;
  double dy = y - mTransY - mATransY;
  if (mCentrosymmetric) {
    dx = x + mTransX + mATransX;
    dy = y + mTransX + mATransY;
  }
  return dx >= mLeft && dx <=mRight && dy >= mBottom && dy <=mTop;
}

SplittedRectLayer::SplittedRectLayer(float left, float bottom, float right, float top, float z_index, float splitLength)
    : LayerObject(z_index)
{
  mVBOBuffer.assign({
    left - splitLength, bottom, 1.0f, 0.0f, 0.0f,
    - splitLength, bottom, 1.0f, 0.5f, 0.0f,
    - splitLength, top, 1.0f, 0.5f, 1.0f,
    left - splitLength, top, 1.0f, 0.0f, 1.0f,

    splitLength, bottom, 1.0f, 0.5f, 0.0f,
    right + splitLength, bottom, 1.0f, 1.0f, 0.0f,
    right + splitLength, top, 1.0f, 1.0f, 1.0f,
    splitLength, top, 1.0f, 0.5f, 1.0f
  });
  mEBOBuffer.assign({
    0,1,2,
    0,2,3,
    4,5,6,
    4,6,7
  });
  mTexture.clear();
}

int SplittedRectLayer::DrawGL(const int nbFrames)
{

  NPNX_ASSERT(!mTexture.empty());

  // Here we should do the following thing to return to default texture for GL_TEXTUREi for parent renderer.
  // But in our program we guarantte that GL_TEXTURE0 is set for every rect, so we need not to reset it.

  // int prevTextureBinding;
  // glGetIntegerv(GL_TEXTURE_BINDING_2D, &prevTextureBinding);
  // ...
  // glBindTexture(GL_TEXTURE_2D, prevTextureBinding);
  // TODO(after the thesis): found the texture type (i.e. GL_TEXTURE_3D) for current GL_TEXTUREi.
  
  glActiveTexture(GL_TEXTURE0);
  glBindTexture(GL_TEXTURE_2D, mTexture[textureNoCallback(nbFrames)]);
  glDrawElements(GL_TRIANGLES, 12, GL_UNSIGNED_INT, (void *)(mEBOOffset * sizeof(GLuint)));
  
  return 0;
}