#ifndef DISPLAY_VIDEOLAYER_H_
#define DISPLAY_VIDEOLAYER_H_

#include "common.h"
#include "layerobject.h"
#include <chrono>

// #include <libavcodec/avcodec.h>
// #include <libavformat/avformat.h>
// #include <libavutil/pixdesc.h>
// #include <libavutil/hwcontext.h>
// #include <libavutil/opt.h>
// #include <libavutil/avassert.h>
// #include <libavutil/imgutils.h>


namespace npnx {
// //dead.
// class VideoLayer: public RectLayer {
// public:

//   //initffmpeg should only run once for the process.
//   VideoLayer(const char * filename, bool initffmpeg = false);
//   virtual ~VideoLayer();

//   virtual int Initialize(const int VBOOffset, const int EBOOffset);
//   virtual int DrawGL(const int nbFrames) override;

// private:
//   std::string filename;
//   File * fileHandle;
//   AVFormatContext *input_ctx = NULL;
//   int video_stream;
//   AVStream *video = NULL;
//   AVCodecContext *decoder_ctx = NULL;
//   AVCodec *decoder = NULL;
//   AVPacket packet;
//   enum AVHWDeviceType type;
// }

  class FakeVideoLayer:public RectLayer {
  public:
    //the filename is fileheader%dfiletailer.
    FakeVideoLayer(const std::string & fileheader, const std::string & filetailer, int num, int ffps, float z_index);
    virtual ~FakeVideoLayer();

    virtual int Initialize(const int VBOOffset, const int EBOOffset) override;
    virtual int DrawGL(const int nbFrames) override;

  private:
    std::string generateFilename(int num);

    uint8_t *memorypool = NULL;
    size_t memoryusage, memoryheadInd=0, memoryTailInd=0;
    size_t memorysize = 4000000000LL;
    GLuint mTexture; 
    int fps;
    int currentImageNum;
    std::chrono::high_resolution_clock::time_point lastframeTime;
    std::string header,tail;
    int numImage, texWidth, texHeight, texChannel;
  };
}

#endif // !DISPLAY_VIDEOLAYER_H_ 