
#include "videolayer.h"
#include "imageUtils.h"
#include <string>

using namespace npnx;

FakeVideoLayer::FakeVideoLayer(const std::string & fileheader, const std::string & filetailer, int num, int ffps, float z_index):RectLayer(-1.0, -1.0, 1.0, 1.0, z_index),
header(fileheader),
tail(filetailer),
numImage(num),
fps(ffps)
{
    memorypool = new uint8_t[memorysize];
    memoryusage = 0;
	lastframeTime = std::chrono::high_resolution_clock::now();
}


FakeVideoLayer::~FakeVideoLayer()
{
  if (memorypool) delete [] memorypool;
}

int FakeVideoLayer::Initialize(const int VBOOffset, const int EBOOffset)
{
  memoryheadInd = 0;
  memoryTailInd = 0;
  memoryusage = 0;
  currentImageNum = 0;
  int suc = 0;
  while (memoryTailInd<numImage && suc>=0) {
    suc = readImageFlipped(generateFilename(memoryTailInd).c_str(), memorypool+memoryusage, memorysize-memoryusage, texWidth, texHeight, texChannel);
    if (suc>=0) {
      memoryusage+=suc;
      memoryTailInd++;
    } else {
      NPNX_ASSERT(memoryTailInd!=memoryheadInd);
    }
  }

  glGenTextures(1, &mTexture);
  glActiveTexture(GL_TEXTURE0);
  glBindTexture(GL_TEXTURE_2D, mTexture);
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, texWidth, texHeight, 0, GL_BGR, GL_UNSIGNED_BYTE, memorypool);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);

  defaultInitialize(VBOOffset, EBOOffset);
}
int FakeVideoLayer::DrawGL(const int nbFrames)
{

    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, mTexture);

    auto nowtp = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> frametime((double)1/fps);
    
    if (nowtp-lastframeTime>frametime){
      currentImageNum++;
      currentImageNum%=numImage;
      while (!(currentImageNum>=memoryheadInd && currentImageNum<memoryTailInd)) {

        memoryheadInd = currentImageNum;
        memoryTailInd = currentImageNum;

        memoryusage = 0;
        int suc = 0;
        while (memoryTailInd<numImage && suc>=0) {
          suc = readImageFlipped(generateFilename(memoryTailInd).c_str(), memorypool+memoryusage, memorysize-memoryusage, texWidth, texHeight, texChannel);
          if (suc>=0) {
              memoryusage+=suc;
              memoryTailInd++;
          } else {
            NPNX_ASSERT(memoryTailInd!=memoryheadInd);
          }
        }
      }

	  uint8_t *newp = memorypool + (currentImageNum - memoryheadInd) * texHeight * texWidth * texChannel;
	  glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, texWidth, texHeight, GL_BGR, GL_UNSIGNED_BYTE, newp);
      lastframeTime = nowtp;
    } 
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, (void *)(mEBOOffset * sizeof(GLuint)));
}

std::string FakeVideoLayer::generateFilename(int num){
  return header+std::to_string(num)+tail;
}