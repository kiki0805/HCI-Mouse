#include "common.h"

#include <string>
#include <cstdlib>
#include <chrono>

#include "layerobject.h"
#include "shader.h"
#include "renderer.h"
#include "imageUtils.h"
#include "dragrectlayer.h"
#include "multimouse.h"

using namespace npnx;

const int num_position_texture = 248;
int image_shift = 0;

class Test_HCIPointer {
public:
  GLFWwindow * window;
  int testCount = 0;
  DragRectLayer * targetRect;
  bool showing = false;
  int nextBeginDrawNbFrame = -1;
  int nbFrames = 0;
  int bgIndex = 0;
  std::chrono::high_resolution_clock::time_point lastShowingTime;
}; 

Test_HCIPointer test_;

void mouse_button_callback(int hDevice, int button, int action, double screenX, double screenY) 
{
  if (hDevice != 0) return;
  if (button == 0x01 && action == GLFW_PRESS) {
    if (test_.showing == false && test_.nextBeginDrawNbFrame < test_.nbFrames ) {
      test_.nextBeginDrawNbFrame = ((double)rand() / RAND_MAX) * 240 + test_.nbFrames;
      test_.targetRect->mTransX = ((double)rand() / RAND_MAX) * 0.7 - 0.35;
      test_.targetRect->mTransY = ((double)rand() / RAND_MAX) * 1.1 - 0.1; NPNX_LOG(test_.targetRect->mTransX);
      NPNX_LOG(test_.targetRect->mTransY);
    }
  } 
}

void glfwmouse_button(GLFWwindow *window, int button, int action, int _) 
{
  double x, y;
  glfwGetCursorPos(test_.window, &x, &y);
  x = (x - WINDOW_WIDTH / 2) / (WINDOW_WIDTH / 2);
  y = -(y - WINDOW_HEIGHT / 2) / (WINDOW_HEIGHT / 2);
  mouse_button_callback(0, 1, action, x, y);
}


void save_respondtime_to_file(double respondTimer)
{
  freopen("respondtime.txt","a",stdout);
  printf("%.4lf\n",respondTimer);
  freopen("CON","a",stdout);
  return ;
}


void before_every_frame() 
{
  double x,y;
  multiMouseSystem.GetCursorPos(0, &x, &y);
  if (test_.showing == true && test_.targetRect->isInside(x, y, test_.nbFrames)) {
    double respondTimer = (double) std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now() - test_.lastShowingTime).count();
    respondTimer /= 1e6;
    // NPNX_LOG(respondTimer);
    save_respondtime_to_file(respondTimer);
    test_.testCount ++;
    NPNX_LOG(test_.testCount);
    NPNX_LOG(test_.bgIndex);
    test_.showing = false;
    test_.targetRect->visibleCallback = [] (int) {return false;};
    test_.nextBeginDrawNbFrame = ((double)rand() / RAND_MAX) * 240 + test_.nbFrames;
    test_.targetRect->mTransX = ((double)rand() / RAND_MAX) * 0.7 - 0.35;
    test_.targetRect->mTransY = ((double)rand() / RAND_MAX) * 1.1 - 0.1;
    NPNX_LOG(test_.targetRect->mTransX);
    NPNX_LOG(test_.targetRect->mTransY);
  }
  if (test_.nbFrames == test_.nextBeginDrawNbFrame) {
    test_.targetRect->visibleCallback = [] (int) {return true;};
    test_.showing = true;
    test_.lastShowingTime = std::chrono::high_resolution_clock::now();
  }
}

void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods)
{
  if (action != GLFW_PRESS) return;
	switch (key) {
	case GLFW_KEY_W:
		test_.bgIndex ++;
    test_.bgIndex %= 3;
    test_.testCount = 0;
		break;
	default:
		break;
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

  multiMouseSystem.Init(mouse_button_callback, true);
  glfwSetKeyCallback(window, key_callback);
  glfwSetMouseButtonCallback(window, glfwmouse_button);

  Shader defaultShader;
  defaultShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("defaultFragment.glsl"));
  defaultShader.Use();
  glUniform1i(glGetUniformLocation(defaultShader.mShader, "texture0"), 0);
  glUniform1f(glGetUniformLocation(defaultShader.mShader, "xTrans"), 0.0f);
  glUniform1f(glGetUniformLocation(defaultShader.mShader, "yTrans"), 0.0f);

  Shader adjustShader;
  adjustShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("adjustFragment.glsl"));
  adjustShader.Use();
  glUniform1i(glGetUniformLocation(adjustShader.mShader, "texture0"), 0);
  glUniform1f(glGetUniformLocation(adjustShader.mShader, "xTrans"), 0.0f);
  glUniform1f(glGetUniformLocation(adjustShader.mShader, "yTrans"), 0.0f);
  glUniform1i(glGetUniformLocation(adjustShader.mShader, "centrosymmetric"), 0);
  glUniform1i(glGetUniformLocation(adjustShader.mShader, "rawScreen"), 1);
  glUniform1i(glGetUniformLocation(adjustShader.mShader, "letThrough"), 0);

  unsigned int fbo0, fboColorTex0;
  generateFBO(fbo0, fboColorTex0);

  Renderer renderer(&defaultShader, fbo0);
  Renderer mouseRenderer(&defaultShader, fbo0);
  Renderer postRenderer(&adjustShader, 0);
  Renderer postMouseRenderer(&defaultShader, 0);

  postRenderer.mDefaultTexture.assign({ 0, fboColorTex0 });

  RectLayer bg(-1.0f, -1.0f, 1.0f, 1.0f, -999.0f);
  bg.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("win.jpg")));
  bg.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("lion.png")));
  bg.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("grey_1920_1080.png")));
  bg.textureNoCallback = [=](int bgIndex) {return bgIndex; };
  renderer.AddLayer(&bg);

  // RectLayer bgb(-(double)WINDOW_HEIGHT / WINDOW_WIDTH, -1.0f, (double)WINDOW_HEIGHT / WINDOW_WIDTH, 1.0f, -9.0f);
  // bgb.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("goboard.jpg")));
  // renderer.AddLayer(&bgb);

  const float targetVSize = 0.3f;
  const float targetHSize = targetVSize * WINDOW_HEIGHT / WINDOW_WIDTH;
  DragRectLayer targetRect(-targetHSize / 2, -targetVSize / 2, targetHSize / 2, targetVSize / 2, 100.0f);
  targetRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("sliderb.png")));
  targetRect.visibleCallback = [] (int) {return false;};
  renderer.AddLayer(&targetRect);
  test_.targetRect = &targetRect;
  
  GLuint mouseTex = makeTextureFromImage(NPNX_FETCH_DATA("cursor.png"));
  GLuint mouseWhiteBlockTex = makeTextureFromImage(NPNX_FETCH_DATA("whiteblock.png"));
  GLuint mouseRedBlockTex = makeTextureFromImage(NPNX_FETCH_DATA("redblock.png"));
  for (int i = 0; i < multiMouseSystem.cNumLimit; i++) {
    const float cursorSize = 0.1f;
    RectLayer *cursorLayer = new RectLayer(0.0f, -cursorSize, cursorSize * WINDOW_HEIGHT / WINDOW_WIDTH, 0.0f, *(float *)&i);
    cursorLayer->mTexture.push_back(mouseTex);
    cursorLayer->visibleCallback = [](int) {return false; };
    mouseRenderer.AddLayer(cursorLayer);

    const float blockVSize = 0.15f;
    const float blockHSize = blockVSize * WINDOW_HEIGHT / WINDOW_WIDTH;
    RectLayer *postColor = new RectLayer(-blockHSize / 2, -blockVSize / 2, blockHSize / 2, blockVSize / 2, *(float *)&i);
    postColor->mTexture.push_back(mouseRedBlockTex);
    postColor->mTexture.push_back(mouseWhiteBlockTex);
    postColor->visibleCallback = [](int) {return false; };
    postMouseRenderer.AddLayer(postColor);
  }

  mouseRenderer.Initialize();
  postMouseRenderer.Initialize();


  RectLayer postBaseRect(-1.0, -1.0, 1.0, 1.0, -999.9);
  postBaseRect.mTexture.push_back(0);
  postBaseRect.beforeDraw = [&](const int nbFrames) {
    glUniform1i(glGetUniformLocation(postRenderer.mDefaultShader->mShader, "letThrough"), 1);
    return 0;
  };
  postBaseRect.afterDraw = [&](const int nbFrames) {
    glUniform1i(glGetUniformLocation(postRenderer.mDefaultShader->mShader, "letThrough"), 0);
    return 0;
  };
  postRenderer.AddLayer(&postBaseRect);

  RectLayer postRect(-9.0f / 16.0f, -1.0f, 9.0f / 16.0f, 1.0f, 999.9f);
  for (int i = 0; i < num_position_texture; i++) {
    std::string pos_texture_path = "fremw2_";
    pos_texture_path += std::to_string(i);
    pos_texture_path += ".png";
    postRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA(pos_texture_path)));
  }
  postRect.visibleCallback = [](int) {return true; };
  postRect.textureNoCallback = [=](int nbFrames) {return nbFrames % 62 + image_shift; };
  postRenderer.AddLayer(&postRect);
  
  renderer.Initialize();
  postRenderer.Initialize();

  multiMouseSystem.RegisterPoseMouseRenderer(&postMouseRenderer);
  multiMouseSystem.RegisterMouseRenderer(&mouseRenderer, [&](int) { return true; });
  multiMouseSystem.mEnableAngle = false;

  test_.nbFrames = 0;
  int lastNbFrames = 0;
  double lastTime = glfwGetTime();
  while (!glfwWindowShouldClose(window))
  {
    before_every_frame();

    renderer.Draw(test_.nbFrames);
    mouseRenderer.Draw(test_.nbFrames);
    postRenderer.Draw(test_.nbFrames);
    postMouseRenderer.Draw(test_.nbFrames);
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
    multiMouseSystem.PollMouseEvents();
  }
  mouseRenderer.FreeLayers();
  postMouseRenderer.FreeLayers();

}