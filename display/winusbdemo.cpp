#include "common.h"

#include <string>
#include <memory>
#include <cassert>
#include <ctime>
// do not include <windows.h>, glfw3native.h included for us and do some workaround work.

#include "layerobject.h"
#include "shader.h"
#include "renderer.h"
#include "imageUtils.h"
#include "dragrectlayer.h"
#include "multimouse.h"

using namespace npnx;
int image_shift = 0;
const int num_position_texture = 248;
enum class MouseButtonState {
  LEFT_PUSHED, RIGHT_PUSHED, RELEASED
};

enum class SceneState {
  ADJUSTING, GAMING
};

class DragDemo {
public:
  GLFWwindow *windowPtr;

  MouseButtonState buttonState = MouseButtonState::RELEASED;
  double lastPushX, lastPushY;
  double cursorOriginX = 0, cursorOriginY = 0, cursorSensitivityX = 1.0, cursorSensitivityY = 1.0;
  float rulerRatio = 0.3f;

  SceneState sceneState = SceneState::GAMING;
  DragRectLayer *focusLayer = NULL;
  LayerObject *postLayer = NULL;

  Renderer *renderer = NULL;
  int nbFrames;

} dragDemo;

void npnxGetCursorPos(GLFWwindow *window, double *x, double *y) {
  double xx, yy;
  glfwGetCursorPos(window, &xx, &yy);
  *x = (xx - dragDemo.cursorOriginX) * dragDemo.cursorSensitivityX / (WINDOW_WIDTH / 2);
  *y = -(yy - dragDemo.cursorOriginY) * dragDemo.cursorSensitivityY / (WINDOW_HEIGHT / 2);
}

void mouse_button_callback(int hDevice, int button, int action, double screenX, double screenY)
{
  if (dragDemo.sceneState == SceneState::ADJUSTING) {
    double x, y;
    glfwGetCursorPos(dragDemo.windowPtr, &x, &y);
    if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_PRESS) {
      dragDemo.cursorOriginX = x;
      dragDemo.cursorOriginY = y;
      dragDemo.buttonState = MouseButtonState::LEFT_PUSHED;
    }
    else if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_RELEASE) {
      dragDemo.cursorSensitivityX = WINDOW_WIDTH * dragDemo.rulerRatio / (x - dragDemo.cursorOriginX);
      dragDemo.cursorSensitivityY = WINDOW_HEIGHT * dragDemo.rulerRatio / (y - dragDemo.cursorOriginY);
      NPNX_LOG(dragDemo.cursorSensitivityX);
      NPNX_LOG(dragDemo.cursorSensitivityY);
      dragDemo.cursorOriginX = x;
      dragDemo.cursorOriginY = y;
      dragDemo.buttonState = MouseButtonState::RELEASED;
      dragDemo.sceneState = SceneState::GAMING;
    }
  }
  else {
    double x, y;
    npnxGetCursorPos(dragDemo.windowPtr, &x, &y);
    if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_PRESS) {
      dragDemo.focusLayer = NULL;
      std::map<float, LayerObject *> & dragVec = dragDemo.renderer->mLayers;
      for (auto it = dragVec.rbegin(); it != dragVec.rend(); ++it) {
        if (it->second->visibleCallback(dragDemo.nbFrames)) {
          DragRectLayer *temp = dynamic_cast<DragRectLayer *>(it->second);
          if (temp) {
            if (temp->isInside(x, y, dragDemo.nbFrames)) {
              dragDemo.lastPushX = x;
              dragDemo.lastPushY = y;
              dragDemo.focusLayer = temp;
              break;
            }
          }
        }
      }
      dragDemo.buttonState = MouseButtonState::LEFT_PUSHED;
    }
    else if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_RELEASE) {
      if (dragDemo.focusLayer) {
        dragDemo.focusLayer->mATransX += dragDemo.focusLayer->mTransX;
        dragDemo.focusLayer->mATransY += dragDemo.focusLayer->mTransY;
        dragDemo.focusLayer->mTransX = 0;
        dragDemo.focusLayer->mTransY = 0;
        dragDemo.focusLayer = NULL;
      }
      dragDemo.buttonState = MouseButtonState::RELEASED;
    }
  }
}

void mouse_pos_callback(GLFWwindow *window, double x, double y)
{

}

void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods)
{
  //if (dragDemo.buttonState != MouseButtonState::RELEASED){
  //  return;
  //}

  // if (key == GLFW_KEY_A)
  // {
  //   if (action == GLFW_RELEASE && dragDemo.sceneState == SceneState::GAMING)
  //   {
  //     dragDemo.sceneState = SceneState::ADJUSTING;
  //   }
  //   return;
  // }

  // if (key == GLFW_KEY_S)
  // {
    /*if (action == GLFW_PRESS)
    {
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_NORMAL);
    glfwSetCursorPos(window, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2);
    }
    if (action == GLFW_RELEASE)
    {
    glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    glfwGetCursorPos(window, &dragDemo.cursorOriginX, &dragDemo.cursorOriginY);
    }*/

  if (action != GLFW_PRESS) return;
  switch (key) {
  case GLFW_KEY_W:
    image_shift += 62;
    image_shift %= 248;
    std::cout << image_shift << std::endl;
    break;
  case GLFW_KEY_S:
    image_shift += 62;
    image_shift %= 248;
    std::cout << image_shift << std::endl;
    break;
  default:
    break;
  }
  //   return;
  // }

  static int demomod = 0;
  if (action == GLFW_RELEASE)
  {
    switch (demomod)
    {
    case 0:
      dragDemo.postLayer->visibleCallback = [](int nbFrames) {
        return true;
      };
      break;
    case 1:
      dragDemo.postLayer->visibleCallback = [](int nbFrames) {
        return false;
      };
      break;
    case 2:
      dragDemo.postLayer->visibleCallback = [](int nbFrames) {
        return (nbFrames & 3) < 2;
      };
      break;
    }
    demomod++;
    demomod %= 3;
  }
}

int main()
{
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
  glEnable(GL_BLEND);
  glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO);

  dragDemo.windowPtr = window;
  multiMouseSystem.Init(mouse_button_callback);

  // glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_NORMAL);
  // glfwSetCursorPos(window, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2);
  // glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
  // glfwGetCursorPos(window, &dragDemo.cursorOriginX, &dragDemo.cursorOriginY);

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
  dragDemo.renderer = &renderer;

  // RectLayer bg(-1.0f, -1.0f, 1.0f, 1.0f, -999.0f);
  // bg.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("test.png")));
  // renderer.AddLayer(&bg);

  RectLayer bgb(-(double)WINDOW_HEIGHT / WINDOW_WIDTH, -1.0f, (double)WINDOW_HEIGHT / WINDOW_WIDTH, 1.0f, -9.0f);
  bgb.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("goboard.jpg")));
  renderer.AddLayer(&bgb);


  srand(time(NULL));
  float ll, bb, rect_size;

  // A is index, should be literally integer.
#define NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(A,B) \
  ll = ((double)rand()/RAND_MAX - 0.5) * 1.8 - 0.1; \
  bb = ((double)rand()/RAND_MAX - 0.5) * 1.8 - 0.1; \
  rect_size = ((double)rand()/RAND_MAX) * 0.2 + 0.1; \
  DragRectLayer ob ## A(ll,bb,ll+rect_size, bb+rect_size*WINDOW_WIDTH/WINDOW_HEIGHT, -1.0 + 0.001 * (A)); \
  ob ## A.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA(B))); \
  renderer.AddLayer(&ob ## A);

  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(0, "blackcoin.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(1, "board.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(2, "green.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(3, "red.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(4, "whitecoin.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(5, "blackcoin.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(6, "board.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(7, "green.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(8, "red.png")
  // NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER(9, "whitecoin.png")

//should only be used here, because no do-while scope here.
#undef NPNX_DRAGDEMO_ALLOC_RANDOM_LAYER


  const float rulerRatio = dragDemo.rulerRatio;
  RectLayer ruler(-rulerRatio, -rulerRatio, rulerRatio, rulerRatio, 999.0f);
  ruler.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("ruler.png")));
  ruler.visibleCallback = [&](int nbFrames) { return dragDemo.sceneState == SceneState::ADJUSTING; };
  renderer.AddLayer(&ruler);

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
  dragDemo.postLayer = &postRect;

  renderer.Initialize();
  postRenderer.Initialize();

  glfwSetKeyCallback(window, key_callback);

  multiMouseSystem.RegisterPoseMouseRenderer(&postMouseRenderer);
  multiMouseSystem.RegisterMouseRenderer(&mouseRenderer, [&](int) { return dragDemo.sceneState == SceneState::GAMING; });

  dragDemo.nbFrames = 0;
  int lastNbFrames = 0;
  double lastTime = glfwGetTime();
  while (!glfwWindowShouldClose(window))
  {
    if (dragDemo.sceneState == SceneState::GAMING && dragDemo.buttonState == MouseButtonState::LEFT_PUSHED) {
      if (dragDemo.focusLayer) {
        DragRectLayer *dragged = dragDemo.focusLayer;
        NPNX_ASSERT(dragged);
        double x, y;
        npnxGetCursorPos(window, &x, &y);
        dragged->mTransX = x - dragDemo.lastPushX;
        dragged->mTransY = y - dragDemo.lastPushY;
      }
    }
    renderer.Draw(dragDemo.nbFrames);
    mouseRenderer.Draw(dragDemo.nbFrames);
    postRenderer.Draw(dragDemo.nbFrames);
    postMouseRenderer.Draw(dragDemo.nbFrames);
    dragDemo.nbFrames++;
    double thisTime = glfwGetTime();
    double deltaTime = thisTime - lastTime;
    if (deltaTime > 1.0)
    {
      glfwSetWindowTitle(window, std::to_string((dragDemo.nbFrames - lastNbFrames) / deltaTime).c_str());
      lastNbFrames = dragDemo.nbFrames;
      lastTime = thisTime;
    }

    glfwSwapBuffers(window);
    glfwPollEvents();
    multiMouseSystem.PollMouseEvents();
  }
  mouseRenderer.FreeLayers();
  postMouseRenderer.FreeLayers();

  glfwTerminate();
  return 0;
}
