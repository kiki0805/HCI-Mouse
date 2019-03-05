#include "curvelayer.h"
#include "renderer.h"
#include <vector>
#include <functional>
#include <cmath>

using namespace npnx;

CurveLayer::CurveLayer(std::vector<float> & controlPoints, float lineWidth, float z) :
  LayerObject(z)
{
  NPNX_ASSERT(controlPoints.size() % 6 == 0 && controlPoints.size() > 6);
  mControlPoints = controlPoints;
  mLineWidth = lineWidth;
  mLinePoints.clear();
}

CurveLayer::~CurveLayer() {}

int CurveLayer::Initialize(const int VBOOffset, const int EBOOffset) {
  int pointer = 0;
  
  while (pointer < mControlPoints.size() - 6) {
    double dis = distance(mControlPoints[pointer], mControlPoints[pointer + 1], mControlPoints[pointer + 6], mControlPoints[pointer + 7]);
    int tLimit = (int)(dis * 50);
    std::vector<float> tempVector = {
        mControlPoints[pointer],
        mControlPoints[pointer + 1],
        mControlPoints[pointer + 4],
        mControlPoints[pointer + 5],
        mControlPoints[pointer + 8],
        mControlPoints[pointer + 9],
        mControlPoints[pointer + 6],
        mControlPoints[pointer + 7]
    };
    for (int t = 0; t < tLimit; t++) {
      double x,y,nx,ny;
      bSplineSolver(tempVector, (double)t/tLimit, &x, &y, &nx, &ny);
      mLinePoints.push_back(x);
      mLinePoints.push_back(y);
      mLinePoints.push_back(nx);
      mLinePoints.push_back(ny);
    }
    pointer+=6;
  }

  for(int i = 0; i < mLinePoints.size(); i+=4) {
    float x,y,nx,ny;
    x = mLinePoints[i];
    y = mLinePoints[i+1];
    nx = mLinePoints[i+2];
    ny = mLinePoints[i+3];
    
    nx = nx * WINDOW_WIDTH / WINDOW_HEIGHT;
    double dd = distance(0.0, 0.0, nx, ny);
    nx /= dd;
    ny /= dd;
    
    float upx, upy, downx, downy;
    upx = mLineWidth / WINDOW_WIDTH * -ny;
    upy = mLineWidth / WINDOW_WIDTH * nx;
    downx = -upx;
    downy = -upy;

    upx = upx * WINDOW_HEIGHT / WINDOW_WIDTH;
    downx = downx * WINDOW_HEIGHT / WINDOW_WIDTH;

    upx += x;
    upy += y;
    downx +=x;
    downy +=y; 

	float kk = (float)i / mLinePoints.size();

    std::vector<float> tempVec;
    tempVec.assign({
      downx, downy, 1.0f, kk, 0.0f,
      upx, upy, 1.0f, kk, 1.0f
    });

    for (auto i: tempVec) {
      mParent->mVBOBuffer.push_back(i);
    }
    mNbVertex += 2;
  }
 
  for (int i = 0; i < mNbVertex; i+=1) {
	  mParent->mEBOBuffer.push_back(VBOOffset + i);
  }
  
  mVBOOffset = VBOOffset;
  mEBOOffset = EBOOffset;
  return 0;
}

int CurveLayer::DrawGL(const int nbFrames) {
  NPNX_ASSERT(mTexture!= 0);
  glActiveTexture(GL_TEXTURE0);
  glBindTexture(GL_TEXTURE_2D, mTexture);
  glDrawElements(GL_TRIANGLE_STRIP, mNbVertex, GL_UNSIGNED_INT, (void *)(mEBOOffset * sizeof(GLuint)));
  return 0;
}

void CurveLayer::bSplineSolver(const vector<float> & controlPoints, const double t, 
                    double *x, double *y, double *nx, double *ny)
{
#define NPNX_BEZIERTRIPLEFUNC(t, offset) \
  ((1-(t)) * (1-(t)) * (1-(t)) * controlPoints[(offset) + 0] \
  + 3 * (1-(t)) * (1-(t)) * (t) * controlPoints[(offset) + 2] \
  + 3 * (1-(t)) * (t) * (t) * controlPoints[(offset) + 4] \
  + (t) * (t) * (t) * controlPoints[(offset) + 6])

#define NPNX_BEZIERDOUBLEFUNC(t, offset) \
  ((1-(t)) * (1-(t)) * controlPoints[(offset) + 0] \
  + 2 * (1-(t)) * (t) * controlPoints[(offset) + 2] \
  + (t) * (t) * controlPoints[(offset) + 4])

// *x = NPNX_BEZIERTRIPLEFUNC(t, 0);
// *y = NPNX_BEZIERTRIPLEFUNC(t, 1);

  double x0, y0, x1, y1;
  x0 = NPNX_BEZIERDOUBLEFUNC(t, 0);
  x1 = NPNX_BEZIERDOUBLEFUNC(t, 2);
  y0 = NPNX_BEZIERDOUBLEFUNC(t, 1);
  y1 = NPNX_BEZIERDOUBLEFUNC(t, 3);

  *nx = x1 - x0;
  *ny = y1 - y0;

  *x = (1 - t) * x0 + t * x1;
  *y = (1 - t) * y0 + t * y1;

#undef NPNX_BEZIERDOUBLEFUNC
#undef NPNX_BEZIERTRIPLEFUNC
}