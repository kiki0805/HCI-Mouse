#include "common.h"

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>
#include <string>

#include "layerobject.h"
#include "shader.h"
#include "renderer.h"


// I want to set the NPNX_DATA_PATH by cmake scripts so that we don't need to care about 
// where are the binary files in.
#ifndef NPNX_DATA_PATH
#define NPNX_DATA_PATH "./data"
#endif

unsigned int makeTexture(unsigned char *buffer, int width, int height) 
{
  //only for BGR 3 channel image with 8bit fixed point depth.
  //if you have another format, write another function by copying most of this one.
  unsigned int texture;
  glGenTextures(1, &texture);
  glBindTexture(GL_TEXTURE_2D, texture);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_BGR, GL_UNSIGNED_BYTE, buffer);
  glGenerateMipmap(GL_TEXTURE_2D); 
  return texture;
}

int main() 
{
  NPNX_LOG(NPNX_DATA_PATH);
  glfwInit();
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
  glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

  GLFWwindow *window = glfwCreateWindow(WINDOW_WIDTH, WINDOW_HEIGHT, "hello", NULL, NULL);
  NPNX_ASSERT(window);
  glfwMakeContextCurrent(window);

  glewExperimental = GL_TRUE;
  GLenum err = glewInit();
  assert(!err);

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

  cv::Mat img;
  img = cv::imread((std::string(NPNX_DATA_PATH)+"/test.png").c_str());
  NPNX_LOG(img.rows);
  NPNX_LOG(img.cols);
  NPNX_LOG(img.channels());
  NPNX_LOG(img.isContinuous());
  NPNX_LOG(img.rows * img.cols * img.channels() * img.elemSize1());
  unsigned char *picBuffer = new unsigned char[img.rows * img.cols * img.channels() * img.elemSize1()];
  memcpy(picBuffer, img.data, img.rows * img.cols * img.channels() * img.elemSize1());

  npnx::Shader defaultShader;
  defaultShader.LoadShader((std::string(NPNX_DATA_PATH)+"/defaultVertex.glsl").c_str(), 
    (std::string(NPNX_DATA_PATH)+"/defaultFragment.glsl").c_str());
  defaultShader.Use();
  glUniform1i(glGetUniformLocation(defaultShader.mShader, "texture1"), 0);

  npnx::Renderer renderer(&defaultShader);

// --------------- Add your layer here--------------//  
  npnx::RectLayer baseRect(-1.0f, -1.0f, 1.0f, 1.0f, -1.0f);
  baseRect.mTexture = makeTexture(picBuffer, img.cols, img.rows);
  renderer.AddLayer(&baseRect);

//randomly generate a picBuffer
unsigned char *anotherBuffer = new unsigned char[600 * 600 * 3];
for (int i=0; i<600 * 600 * 3; i++) {
  anotherBuffer[i] = rand() & 255;
}

  npnx::RectLayer upperRect(-0.5f, -0.1f, 0.3f, 0.4f, 0.0f);
  upperRect.mTexture = makeTexture(anotherBuffer, 600, 600);
  upperRect.visibleCallback = [] (int nbFrames) {
    return (nbFrames & 3) < 2;
  };
  renderer.AddLayer(&upperRect);

// ------------------------------------------------//
  delete [] picBuffer;
  renderer.Initialize();

  int nbFrames = 0;
  int lastNbFrames = 0;
  double lastTime = glfwGetTime();
  while (!glfwWindowShouldClose(window))
  {

    glClearColor(0.5f, 0.5f, 0.1f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);

    nbFrames++;
    double thisTime = glfwGetTime();
    double deltaTime = thisTime - lastTime;
    if (deltaTime > 1.0)
    {
      glfwSetWindowTitle(window, std::to_string((nbFrames - lastNbFrames) / deltaTime).c_str());
      lastNbFrames = nbFrames;
      lastTime = thisTime;
    }

    renderer.Draw(nbFrames);

    glfwSwapBuffers(window);
    glfwPollEvents();
  }

  glfwTerminate();
  return 0;
}