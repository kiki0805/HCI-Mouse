#include "dragrectlayer.h"
#include "renderer.h"

using namespace npnx;

DragRectLayer::DragRectLayer(float left, float bottom, float right, float top, float z_index):
  RectLayer(left, bottom, right, top, z_index),
  mLeft(left),
  mBottom(bottom),
  mRight(right),
  mTop(top)
{
}

int DragRectLayer::DrawGL(const int nbFrames) 
{
  NPNX_ASSERT(!mTexture.empty());

  glUniform1f(glGetUniformLocation(mParent->mDefaultShader->mShader, "xTrans"), mTransX+mATransX);
  glUniform1f(glGetUniformLocation(mParent->mDefaultShader->mShader, "yTrans"), mTransY+mATransY);

  glActiveTexture(GL_TEXTURE0);
  glBindTexture(GL_TEXTURE_2D, mTexture[textureNoCallback(nbFrames)]);
  glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, (void *)(mEBOOffset * sizeof(GLuint)));

  glUniform1f(glGetUniformLocation(mParent->mDefaultShader->mShader, "xTrans"), 0.0f);
  glUniform1f(glGetUniformLocation(mParent->mDefaultShader->mShader, "yTrans"), 0.0f);
  return 0;
}

bool DragRectLayer::isInside(double x, double y, const int nbFrames) {
  double dx = x - mTransX - mATransX;
  double dy = y - mTransY - mATransY;
  return dx >= mLeft && dx <=mRight && dy >= mBottom && dy <=mTop;
}