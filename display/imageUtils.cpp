#include "imageUtils.h"

#include "common.h"
#include <memory>
#include <string>

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

unsigned int makeTexture(unsigned char *buffer, int width, int height, int channel)
{
  //only for BGR or BGRA image with 8bit fixed point depth.
  //if you have another format, write another function by copying most of this one.
  unsigned int texture;
  glGenTextures(1, &texture);
  glBindTexture(GL_TEXTURE_2D, texture);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
  switch (channel)
  {
  case 3:
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_BGR, GL_UNSIGNED_BYTE, buffer);
    break;
  case 4:
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_UNSIGNED_BYTE, buffer);
    break;
  default:
    NPNX_ASSERT(channel != 3 && channel != 4);
    break;
  }
  glGenerateMipmap(GL_TEXTURE_2D);
  return texture;
}

unsigned int makeTextureFromImage(const char * imagepath){
  cv::Mat img;
  img = cv::imread(imagepath, cv::IMREAD_UNCHANGED);
  NPNX_LOG(imagepath);
  NPNX_LOG(img.rows);
  NPNX_LOG(img.cols);
  NPNX_LOG(img.channels());
  NPNX_ASSERT(img.isContinuous());
  NPNX_ASSERT(img.elemSize1() == 1);
  NPNX_LOG(img.rows * img.cols * img.channels());
  //unique_ptr only used for simple buffers, do not use it or shared ptr to generate class object, because my ability limitation.
  //  ——npnx
  return makeTexture(img.data, img.cols, img.rows, img.channels());
}