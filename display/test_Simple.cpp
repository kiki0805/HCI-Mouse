#include "winusb/mousecore.h"
#include "common.h"

#include <string>
#include <cstdlib>
#include <chrono>
#include <atomic>
#include <iostream>

#include "winusb/mousecore.h"
#include "layerobject.h"
#include "shader.h"
#include "renderer.h"
#include "imageUtils.h"

using namespace npnx;

// const int num_position_texture = 248;
// const char position_texture_name_prefix[] = "freq_";
const char csv_name_prefix[] = "test_";
const int packetLengthInFrames = 62; //num_position_texture;
// const 
const int positionLimit = 100;

class Test_Simple {
public:
  int packetLimit = 100;
  int mode = 0;
  int num_position_texture = 248;
  //char position_texture_name_prefix[] = "freq1_";
  GLFWwindow * window;
  MouseCore * core;
  int nbFrames = 0;
  int beforeStripLengthInFrames = 0;//120;
  int afterStripLengthInFrames = 0;//120;
  int nextStopFrameNo = 0;
  int stopFrames = 0;
  int num_mouse = 0;

  int currentMousePositionId = -1;
  std::atomic<int>  currentPacketId = packetLimit;

  RectLayer *rect;

  std::atomic<bool> readMouseDataSwitch = false;
}; 

class Player_Simple {
public:

  //this is set by render thread and de-set by control transfer reader thread. 
  std::atomic<bool> writeFileSignal = false;
  std::thread *readerT;
};

Test_Simple test_;
Player_Simple player_[2];

struct CTData {
  int64_t timestamp;
  int packetId, RGBData, AveData;
};

int64_t getTime() {
  FILETIME systf;
  FILETIME loctf;
  GetSystemTimePreciseAsFileTime(&systf);
  FileTimeToLocalFileTime(&systf, &loctf);
  int64_t loctfi64 = (int64_t)loctf.dwHighDateTime * 4294967296LL + (int64_t)*(uint32_t *)&loctf.dwLowDateTime; 
  return loctfi64;
}

void mouseReportCallback(int idx, MouseReport report) {
  // printf("%d: %02hhx %02hhx %04hx %04hx %04hx\n", idx,
  //    report.flags, report.button, report.xTrans, report.yTrans, report.wheel);
}

void mouseReaderEntry(int mouseid, int positionID, int mode, bool EnableAveData = true) {
  std::vector<CTData> databuf;
  databuf.reserve(1000000);
  while (!player_[mouseid].writeFileSignal.load()) {
    uint8_t buf[4096];
    memset(buf, 0, sizeof(uint8_t) * 4096);
    int cnt = -1;
    cnt = test_.core->ControlTransfer(mouseid, 0x40, 0x01, 0x0000, 0x0D, buf, 1, 1000);
    LIBUSB_CHECK_RET(CT1, cnt);

    test_.core->ControlTransfer(mouseid, 0xC0, 0x01, 0x0000, 0x0D, buf, 1, 1000);
    LIBUSB_CHECK_RET(CT1, cnt);
    
    if (EnableAveData) {
      test_.core->ControlTransfer(mouseid, 0xC0, 0x01, 0x0000, 0x0B, buf + 1, 1, 1000);
      LIBUSB_CHECK_RET(CT1, cnt);
    }

    if (test_.readMouseDataSwitch.load()) {
      databuf.push_back({
        getTime(),
        test_.currentPacketId.load(),
        buf[0],
        buf[1]
      });
    }
  }
  
  std::string filename = csv_name_prefix;
  char* position_texture_name_prefix;
  if (mode == 1) position_texture_name_prefix = "freq1_";
  else if(mode == 2) position_texture_name_prefix = "freq2_";
  else if (mode == 3) position_texture_name_prefix = "freq_";
  else std::cout<<"WRONG TEST_.MODE"<<std::endl;
  filename += position_texture_name_prefix + std::to_string(getTime()) + "_" + std::to_string(mouseid) + ".csv";
  FILE *csv_file = fopen(filename.c_str(), "w");
  
  char fileLine[4096];
  sprintf(fileLine, "texture_name, mouse_id, position_id, packet_id, rgb_data, ave_data, timestamp\n");
  fwrite(fileLine, 1, strlen(fileLine), csv_file);

  for (auto it: databuf) {
    sprintf(fileLine, "%s, %d, %d, %d, %d, %d, %d.%07d\n", position_texture_name_prefix, mouseid, positionID, it.packetId, it.RGBData, it.AveData, it.timestamp / 10000000, it.timestamp % 10000000);
    fwrite(fileLine, 1, strlen(fileLine), csv_file);
  }

  fclose(csv_file);
  databuf.clear();
  player_[mouseid].writeFileSignal = false;
}

void before_every_frame(){
  if (test_.nbFrames == test_.nextStopFrameNo) {
    
    test_.currentPacketId += 1;

    if (test_.currentPacketId.load() >= test_.packetLimit) {
      test_.readMouseDataSwitch = false;
      
      test_.currentPacketId = 0;


      //stop last thread.
      if (test_.currentMousePositionId != -1) {
        
        for(int i = 0; i < test_.num_mouse; i++) {
          player_[i].writeFileSignal = true;
        }

        for(int i = 0; i < test_.num_mouse; i++) {
          player_[i].readerT->join();
          delete player_[i].readerT;
          player_[i].readerT = NULL;
          NPNX_ASSERT(player_[i].writeFileSignal.load() == false);
        }       
      }

      test_.mode += 1;
      if (test_.mode > 3) {
        test_.currentMousePositionId += 1;
      }
      
      if (test_.currentMousePositionId >= positionLimit) {
        printf("finished!");
        glfwSetWindowShouldClose(test_.window, GLFW_TRUE);
        return;
      } else {
        // test_.packetLimit = test_.mode == 3 ? 400 : 100;
        if(test_.mode > 3){
          test_.mode = 1;
          
          printf("Change Position %d. input anything to continue:", test_.currentMousePositionId);
          char tempbuf[4096];
          scanf("%s", tempbuf); 
        }
        else{
          printf("Change Mode %d. \n", test_.mode);
        }
      }


      for (int i = 0; i < test_.num_mouse; i++) {
        player_[i].readerT = new std::thread(mouseReaderEntry, i, test_.currentMousePositionId, test_.mode, i == 0);
      }

      test_.readMouseDataSwitch = true;
    }
    
    int beginNo = test_.nbFrames + test_.beforeStripLengthInFrames;
    int endNo = beginNo + packetLengthInFrames;
    test_.nextStopFrameNo = endNo + test_.afterStripLengthInFrames;
    test_.rect->textureNoCallback = [=] (int nbFrames) -> unsigned int {
      if (test_.stopFrames != 0) {test_.stopFrames -= 1; return 0;}
      if (nbFrames >= beginNo && nbFrames < endNo) {
        // int shiftIndex = test_.currentPacketId / (packetLimit / 4);
          // return (nbFrames - beginNo) % packetLengthInFrames + shiftIndex * packetLengthInFrames + 248 * (test_.mode-1);
        if(test_.mode == 3) {
          // int lastShiftIndex = (test_.currentPacketId - 1) / (test_.packetLimit / 4);
          int shiftIndex = test_.currentPacketId % 4;
          // std::cout<<test_.currentPacketId<<" " <<shiftIndex<<std::endl;
          // if(shiftIndex - lastShiftIndex == 1) {test_.stopFrames = 239; return 0;}
          return (nbFrames - beginNo) % packetLengthInFrames + shiftIndex * packetLengthInFrames + 62 * (test_.mode-1);
        }
        else {
          return (nbFrames - beginNo) % packetLengthInFrames + 62 * (test_.mode-1);
        }
      }
      return 0;
    };

  }  
}

int main() 
{
  srand(1); // this guarantee that the random target rectangle will be same every time we run.
  NPNX_LOG(NPNX_DATA_PATH);
  glfwInit();
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
  glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
  glfwWindowHint(GLFW_AUTO_ICONIFY, GLFW_FALSE);

  int monitorCount;
  GLFWmonitor** pMonitor = glfwGetMonitors(&monitorCount);

  int holographic_screen = -1;
  for (int i = 0; i < monitorCount; i++) {
    int screen_x, screen_y;
    const GLFWvidmode * mode = glfwGetVideoMode(pMonitor[i]);
    screen_x = mode->width;
    screen_y = mode->height;
    std::cout << "Screen size is X = " << screen_x << ", Y = " << screen_y << std::endl;
    if (screen_x == WINDOW_WIDTH && screen_y == WINDOW_HEIGHT) {
      holographic_screen = i;
    }
  }
  NPNX_LOG(holographic_screen);

  GLFWwindow* window;
#if (defined __linux__ || defined NPNX_BENCHMARK)
  window = glfwCreateWindow(WINDOW_WIDTH, WINDOW_HEIGHT, "My Title", NULL, NULL);

#else
  if (holographic_screen == -1)
    window = glfwCreateWindow(WINDOW_WIDTH, WINDOW_HEIGHT, "My Title", NULL, NULL);
  else
    window = glfwCreateWindow(WINDOW_WIDTH, WINDOW_HEIGHT, "Holographic projection", pMonitor[holographic_screen], NULL);
#endif  

  NPNX_ASSERT(window);
  glfwMakeContextCurrent(window);

  test_.window = window;

  glewExperimental = GL_TRUE;
  GLenum err = glewInit();
  NPNX_ASSERT(!err);

#ifndef NPNX_BENCHMARK
#ifdef __linux__
  if (glxewIsSupported("GLX_MESA_swap_control"))
  {
    printf("OK, we can use GLX_MESA_swap_control\n");
  }
  else
  {
    printf("[WARNING] GLX_MESA_swap_control is NOT supported.\n");
  }
  glXSwapIntervalMESA(1);
  printf("Swap interval: %d\n", glXGetSwapIntervalMESA());
#endif

#ifdef _WIN32
  if (wglewIsSupported("WGL_EXT_swap_control"))
  {
    printf("OK, we can use WGL_EXT_swap_control\n");
  }
  else
  {
    printf("[WARNING] WGL_EXT_swap_control is NOT supported.\n");
  }
  wglSwapIntervalEXT(1);
#endif
#endif

  glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);
  glEnable(GL_BLEND);
  glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO);

  Shader defaultShader;
  defaultShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("defaultFragment.glsl"));
  defaultShader.Use();
  glUniform1i(glGetUniformLocation(defaultShader.mShader, "texture0"), 0);
  glUniform1f(glGetUniformLocation(defaultShader.mShader, "xTrans"), 0.0f);
  glUniform1f(glGetUniformLocation(defaultShader.mShader, "yTrans"), 0.0f);

  Renderer renderer(&defaultShader, 0);

  RectLayer postRect(-9.0f / 16.0f, -1.0f, 9.0f / 16.0f, 1.0f, 999.9f);
  
  std::string position_texture_name_prefix;
  int num_position_texture;
  int mode = 0;
  while(mode < 3) {
    mode ++;
    if (mode == 1) {
      position_texture_name_prefix = "freq1_";
      num_position_texture = 62;
    }
    else if(mode == 2) {
      position_texture_name_prefix = "freq2_";
      num_position_texture = 62;
    }
    else if (mode == 3) {
      position_texture_name_prefix = "freq_";
      num_position_texture = 248;
    }
    for (int i = 0; i < num_position_texture; i++) {
      std::string pos_texture_path = position_texture_name_prefix;
      pos_texture_path += std::to_string(i);
      pos_texture_path += ".png";
      postRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA(pos_texture_path)));
    }
  }
  postRect.visibleCallback = [](int) {return true; };
  postRect.textureNoCallback = [=](int nbFrames) {return 0; };
  test_.rect = &postRect;
  renderer.AddLayer(&postRect);
  
  renderer.Initialize();

  MouseCore core;
  test_.core = &core;
  test_.num_mouse = core.Init(default_vid, default_pid, mouseReportCallback);

  test_.nbFrames = 0;
  int lastNbFrames = 0;
  double lastTime = glfwGetTime();
  while (!glfwWindowShouldClose(window))
  {
    before_every_frame();

    renderer.Draw(test_.nbFrames);
    test_.nbFrames++;
    double thisTime = glfwGetTime();
    double deltaTime = thisTime - lastTime;
    if (deltaTime > 1.0)
    {
      glfwSetWindowTitle(window, std::to_string((test_.nbFrames - lastNbFrames) / deltaTime).c_str());
      lastNbFrames = test_.nbFrames;
      lastTime = thisTime;
    }

    glfwSwapBuffers(window);
    glfwPollEvents();    
  }
  glfwTerminate();

  return 0;
}