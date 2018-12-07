#include "common.h"

#include <string>
#include <memory>
#include <cassert>

#include "layerobject.h"
#include "shader.h"
#include "renderer.h"
#include "imageUtils.h"

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
  

  npnx::Shader defaultShader;
  defaultShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("defaultFragment.glsl"));
  defaultShader.Use();
  glUniform1i(glGetUniformLocation(defaultShader.mShader, "texture0"), 0);

  npnx::Shader adjustShader;
  adjustShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("adjustFragment.glsl"));
  adjustShader.Use();
  glUniform1i(glGetUniformLocation(adjustShader.mShader, "texture0"), 0);
  glUniform1i(glGetUniformLocation(adjustShader.mShader, "rawScreen"), 1);
  glUniform1i(glGetUniformLocation(adjustShader.mShader, "letThrough"), 0);

  unsigned int fbo0, fboColorTex0;
  generateFBO(fbo0, fboColorTex0); 

  npnx::Renderer renderer(&defaultShader, fbo0);
  npnx::Renderer postRenderer(&adjustShader, 0);
  postRenderer.mDefaultTexture.assign({0, fboColorTex0});

  // --------------- Add your layer here--------------//  
  npnx::RectLayer baseRect(-1.0f, -1.0f, 1.0f, 1.0f, -1.0f);
  baseRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("test.png")));
  renderer.AddLayer(&baseRect);

  npnx::RectLayer upperRect(-0.5f, -0.1f, -0.2f, 0.8f, 0.0f);
  std::unique_ptr<unsigned char> anotherBuffer(new unsigned char[600 * 600 * 3]);
  generateRandomArray(anotherBuffer.get(), 600 * 600 * 3, 0, 255);
  upperRect.mTexture.push_back(makeTexture(anotherBuffer.get(), 600, 600, 3));
  upperRect.visibleCallback = [] (int nbFrames) {
    return (nbFrames & 255) < 128;
  };
  renderer.AddLayer(&upperRect);

  npnx::RectLayer postBaseRect(-1.0f, -1.0f, 1.0f, 1.0f, -999.0f);
  postBaseRect.beforeDraw = [&] (const int nbFrames) {
    glUniform1i(glGetUniformLocation(postBaseRect.mParent->mDefaultShader->mShader, "letThrough"), 1);
    return 0;
  };
  postBaseRect.afterDraw = [&] (const int nbFrames) {
    glUniform1i(glGetUniformLocation(postBaseRect.mParent->mDefaultShader->mShader, "letThrough"), 0);
    return 0;
  };
  postBaseRect.mTexture.push_back(0);
  postRenderer.AddLayer(&postBaseRect);

  npnx::RectLayer postRect(-0.6f, -0.1f, -0.3f, 0.433f, 999.9f);
  postRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("hitcircle.png")));
  postRect.visibleCallback = [](int nbFrames) {
    return (nbFrames & 3) < 2;
  };
  postRenderer.AddLayer(&postRect);

// ------------------------------------------------//
  renderer.Initialize();
  postRenderer.Initialize();

  int nbFrames = 0;
  int lastNbFrames = 0;
  double lastTime = glfwGetTime();
  while (!glfwWindowShouldClose(window)) {

    // if (renderer.Updated(nbFrames) || postRenderer.Updated(nbFrames)) {
    renderer.Draw(nbFrames);
    postRenderer.Draw(nbFrames);
    // }

    nbFrames++;
    double thisTime = glfwGetTime();
    double deltaTime = thisTime - lastTime;
    if (deltaTime > 1.0) {
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
