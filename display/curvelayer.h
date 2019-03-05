#ifndef DISPLAY_CURVELAYER_H_
#define DISPLAY_CURVELAYER_H_

#include "common.h"
#include "layerobject.h"
#include <vector>
#include <cmath>


namespace npnx {
using std::vector;

class CurveLayer : public LayerObject {
public:
  CurveLayer(vector<float> & controlPoints, float lineWidth, float z);
  virtual ~CurveLayer();
  
  virtual int Initialize(const int VBOOffset, const int EBOOffset);
  
  virtual int DrawGL(const int nbFrames);

private:
  void bSplineSolver(const vector<float> & controlPoints, const double t, double *x, double *y, double *nx, double *ny);
  inline double distance(const double x0, const double y0, const double x1, const double y1)
  {
    return std::sqrt((x1-x0)*(x1-x0)+(y1-y0)*(y1-y0)); 
  }

private:
  int mNbVertex = 0;

public:
  // mControlPoints : x0, y0, lh0x, lh0y, rh0x, rh0y,  x1, y1, lh1x, lh1y, rh1x, rh1y ...
  vector<float> mControlPoints;
  vector<float> mLinePoints;
  float mLineWidth;
  GLuint mTexture  = 0;
};
}







#endif // !DISPLAY_CURVELAYER_H_