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

// the NPNX_DATA_PATH is set by cmake scripts so that we don't need to care about
// where are the binary files in.
#ifndef NPNX_DATA_PATH
#define NPNX_DATA_PATH "./data"
#endif

// CAUTION : Use this will make the pointer invalid immediately after the caller end.
//  which means if the caller save this pointer for another use after the call, it will be a SEGFAULT.
#define NPNX_FETCH_DATA(A) ((std::string((NPNX_DATA_PATH)) + "/" + (A)).c_str())

#endif // !DISPLAY_COMMON_H_