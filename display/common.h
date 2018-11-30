#ifndef DISPLAY_COMMON_H_
#define DISPLAY_COMMON_H_

#include <GL/glew.h>

#ifdef _WIN32
#include <GL/wglew.h>
#endif

#ifdef __linux__
#include <GL/glxew.h>
#endif

#include <GLFW/glfw3.h>
#include <iostream>
#include <cstdlib>

#define NPNX_ASSERT(A)                   \
  do                                     \
  {                                      \
    if (!(A))                            \
    {                                    \
      std::cerr << #A << " failed!" << std::endl; \
      glfwTerminate();                   \
      exit(-1);                          \
    }                                    \
  } while (false)

#define NPNX_ASSERT_LOG(A,B) \
  do                              \
  {                               \
    if (!(A))                     \
    {                             \
      std::cerr << #A << std::endl; \
      std::cerr << (B) << std::endl; \
      glfwTerminate();            \
      exit(-1);                   \
    }                             \
  } while (false)

#define NPNX_LOG(A) do { \
  std::cout << #A << " " << (A) << std::endl; \
  std::cout.flush(); \
} while (false)

#define WINDOW_WIDTH 1920
#define WINDOW_HEIGHT 1080


#endif // !DISPLAY_COMMON_H_