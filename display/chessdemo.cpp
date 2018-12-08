#include "common.h"

#include <string>
#include <memory>
#include <cassert>

#include "layerobject.h"
#include "shader.h"
#include "renderer.h"
#include "imageUtils.h"
#include "simpleChess.h"

namespace npnx {
  SimpleChess simpleChess;
}

void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods);

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
  // glEnable(GL_BLEND);
  // glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO);

  npnx::simpleChess.Init();
  glfwSetMouseButtonCallback(window, npnx::mouse_button_callback);
  glfwSetKeyCallback(window, key_callback);

  int nbFrames = 0;
  int lastNbFrames = 0;
  double lastTime = glfwGetTime();
  while (!glfwWindowShouldClose(window))
  {

    npnx::simpleChess.Draw(nbFrames);

    nbFrames++;
    double thisTime = glfwGetTime();
    double deltaTime = thisTime - lastTime;
    if (deltaTime > 1.0)
    {
      glfwSetWindowTitle(window, std::to_string((nbFrames - lastNbFrames) / deltaTime).c_str());
      lastNbFrames = nbFrames;
      lastTime = thisTime;
    }

    glfwSwapBuffers(window);
    glfwPollEvents();
  }

  glfwTerminate();
  return 0;
}

void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods)
{
  static int demomod = 0;
  if (action == GLFW_RELEASE) {
    switch (demomod) {
      case 0:npnx::simpleChess.postLayer->visibleCallback = [](int nbFrames) {
          return true;
        };
        break;
      case 1:npnx::simpleChess.postLayer->visibleCallback = [](int nbFrames) {
          return false;
        }; 
        break;
      case 2:npnx::simpleChess.postLayer->visibleCallback = [](int nbFrames) {
          return (nbFrames & 3) < 2;
        };
        break;
    }
    demomod++;
    demomod%=3;
  }
}