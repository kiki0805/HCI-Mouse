#include "common.h"

#include <cassert>
#include <cstdlib> // for exit()
#include <iostream>
#include <fstream>
#include <string>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

#include "shader.h"

int main() 
{
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
  
  glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);

#ifdef NPNX_V_SYNC
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

#ifdef  _WIN32
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

  float vertices[] = {
    -0.9f, -0.9f, 0.0f, 0.0f, 0.0f,
    0.9f, -0.9f, 0.0f, 1.0f, 0.0f,
    0.9f, 0.9f, 0.0f, 1.0f, 1.0f,
    -0.9f, 0.9f, 0.0f, 0.0f, 1.0f
  };
  unsigned int indices[] = {
    0, 1, 2,
    0, 2, 3
  };


  unsigned int VAO;
  glGenVertexArrays(1, &VAO);
  unsigned int VBO;
  glGenBuffers(1, &VBO);  
  unsigned int EBO;
  glGenBuffers(1, &EBO);
  glBindVertexArray(VAO);
  glBindBuffer(GL_ARRAY_BUFFER, VBO);
  glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
  glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(indices), indices, GL_STATIC_DRAW);
  
  glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void *)0);
  glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void *) (3*sizeof(float)));
  glEnableVertexAttribArray(0);
  glEnableVertexAttribArray(1);

  cv::Mat img;
  img = cv::imread("../../data/test.png");
  NPNX_LOG(img.rows);
  NPNX_LOG(img.cols);
  NPNX_LOG(img.channels());
  NPNX_LOG(img.elemSize());
  NPNX_LOG(img.isContinuous());
  NPNX_LOG(img.size);
  NPNX_LOG(img.rows * img.cols * img.channels() * img.elemSize1());
  unsigned char *picBuffer = new unsigned char[img.rows * img.cols * img.channels() * img.elemSize1()];
  memcpy(picBuffer, img.data, img.rows * img.cols * img.channels() * img.elemSize1());

  npnx::Shader defaultShader;
  defaultShader.LoadShader("../../data/defaultVertex.glsl", "../../data/defaultFragment.glsl");
  
  unsigned int texture;
  glGenTextures(1, &texture);
  glBindTexture(GL_TEXTURE_2D, texture);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.cols, img.rows, 0, GL_BGR, GL_UNSIGNED_BYTE, picBuffer);
  glGenerateMipmap(GL_TEXTURE_2D);
  delete[] picBuffer;

  defaultShader.Use();
  glUniform1i(glGetUniformLocation(defaultShader.mShader, "texture1"), 0);

  int nbFrames = 0;
  int lastNbFrames = 0;
  double lastTime = glfwGetTime();
  while (!glfwWindowShouldClose(window)) {

    glClearColor(0.5f, 0.5f, 0.1f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);

    nbFrames++;
    double thisTime = glfwGetTime();
    double deltaTime = thisTime - lastTime;
    if (deltaTime > 1.0) {
      glfwSetWindowTitle(window, std::to_string((nbFrames - lastNbFrames)/deltaTime).c_str());
      lastNbFrames = nbFrames;
      lastTime = thisTime;
    }

    defaultShader.Use();
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, texture);
    glBindVertexArray(VAO);
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);

    glfwSwapBuffers(window);
    glfwPollEvents();
  }

  glfwTerminate();
  return 0;
}
