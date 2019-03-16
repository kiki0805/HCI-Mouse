#include "common.h"

#include <string>
#include <cstdlib>
#include <chrono>
#include <cstdio>

#include "layerobject.h"
#include "shader.h"
#include "renderer.h"
#include "imageUtils.h"
#include "dragrectlayer.h"
#include "multimouse.h"


using namespace npnx;

const int num_position_texture = 248;
int image_shift = 0;
const int feedbackLength = 120;

class Test_Whac {
public:
  GLFWwindow * window;
  int bgIndex = 0;
  int nbFrames = 0;
  int pieces_used = 0;
  bool running = false;
}; 
  

class Player_Whac {
public:
  bool showing = false;
  int nextBeginFrame = -1; 
  DragRectLayer *target;
};

Test_Whac test_;
Player_Whac player_[2];

auto truefunc = [] (int) -> bool {return true;};
auto falsefunc = [] (int) -> bool {return false;};

void mouse_button_callback(int hDevice, int button, int action, double screenX, double screenY) 
{
  if (!test_.running) {
    if (button == 0x01 && action == GLFW_PRESS)
    {
      for (int pid = 0; pid < multiMouseSystem.GetNumMouse(); pid ++) {
        int nbt = test_.nbFrames + (rand() % 240 + 120);
        player_[pid].nextBeginFrame = nbt;
        test_.running = true;
      }
    }
  }
}

void glfwmouse_button(GLFWwindow *window, int button, int action, int _) 
{
  if (action != GLFW_PRESS) return;
  double x, y;
  glfwGetCursorPos(test_.window, &x, &y); 
  mouse_button_callback(0, 1, GLFW_PRESS, (double)(x - WINDOW_WIDTH / 2) / (WINDOW_WIDTH / 2),
      - (double) (y - WINDOW_HEIGHT / 2) / (WINDOW_HEIGHT / 2));
}

void before_every_frame() 
{
  for (int pid = 0; pid < 2; pid++) {
    if (player_[pid].nextBeginFrame == test_.nbFrames) {
      player_[pid].showing = true;
      player_[pid].target->mTransX = ((double)rand() / RAND_MAX) * 0.5 + (pid == 0 ? -0.5 : 0);
      player_[pid].target->mTransY = ((double)rand() / RAND_MAX) * 1.6 - 0.8;
      player_[pid].target->textureNoCallback = [] (int nbFrames) {return 0;};
      player_[pid].target->visibleCallback = truefunc;
    }
    if (player_[pid].showing) {
      double x,y;
      for (int mid = 0; mid < multiMouseSystem.GetNumMouse(); mid++){
        multiMouseSystem.GetCursorPos(mid, &x, &y);
        if (player_[pid].target->isInside(x,y,test_.nbFrames)) {
          int fadeframe = test_.nbFrames + feedbackLength; 
          int nbt = fadeframe + (rand() % 240 + 120);
          
          player_[pid].target->visibleCallback = [fadeframe] (int nbFrames) {
            return nbFrames <= fadeframe;
          };
          player_[pid].target->textureNoCallback = [nbt] (int nbFrames) {return 1;};
          player_[pid].nextBeginFrame = nbt;
          player_[pid].showing = false;
          break;
        }
      }
    }
  }
}

void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods)
{
  if (action != GLFW_PRESS) return;
	switch (key) {
	case GLFW_KEY_W:
		test_.bgIndex ++;
    test_.bgIndex %= 3;
		break;
	default:
		break;
	}
}

int main() 
{
  srand(1); // this guarantee that the random target rectangle will be same every time we run.
  std::string frm;
  frm.reserve(2000000);
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
#if (defined __linux__)
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
  // adjustShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("newAdjFrag.glsl"));
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
  bg.textureNoCallback = [&](int _) {return test_.bgIndex; };
  renderer.AddLayer(&bg);

  RectLayer bgb(-(double)WINDOW_HEIGHT / WINDOW_WIDTH, -1.0f, (double)WINDOW_HEIGHT / WINDOW_WIDTH, 1.0f, -9.0f);
  bgb.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("goboard.jpg")));
  renderer.AddLayer(&bgb);

  GLuint sbTex = makeTextureFromImage(NPNX_FETCH_DATA("mole.png"));
  GLuint paTex = makeTextureFromImage(NPNX_FETCH_DATA("molehit.png"));

  const float targetVSize = 0.3f;
  const float targetHSize = targetVSize * WINDOW_HEIGHT / WINDOW_WIDTH;
  DragRectLayer piece1(-targetHSize / 2, -targetVSize / 2, targetHSize / 2, targetVSize / 2, 1.0f);
  piece1.mTexture.push_back(sbTex);
  piece1.mTexture.push_back(paTex);
  piece1.visibleCallback = falsefunc;
  renderer.AddLayer(&piece1);

  DragRectLayer piece2(-targetHSize / 2, -targetVSize / 2, targetHSize / 2, targetVSize / 2, 1.1f);
  piece2.mTexture.push_back(sbTex);
  piece2.mTexture.push_back(paTex);
  piece2.visibleCallback = falsefunc;
  renderer.AddLayer(&piece2);

  player_[0].target = &piece1;
  player_[1].target = &piece2;

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

  const float splitLength = 0.25f;
  SplittedRectLayer postRect(-9.0f / 16.0f, -1.0f, 9.0f / 16.0f, 1.0f, 999.9f, splitLength);
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
  #define M_PI 3.14159265359
  // multiMouseSystem.mouses[0]->SetMouseAngle(M_PI / 2.0);
  // multiMouseSystem.mouses[1]->SetMouseAngle(M_PI / 2.0 * 3.0);
  #undef M_PI
  multiMouseSystem.hciToScreenPosFunc = [=] (int p1, int p2, double *sx, double *sy){
    // (32,0)
    //  |
    // (0,0) -- (0,32)
    *sx = p2 * 32 + 420;
    *sy = WINDOW_HEIGHT - p1 * 32;
    if (*sx < WINDOW_WIDTH / 2) {
      *sx -= WINDOW_WIDTH / 2 * splitLength;
    } else {
      *sx += WINDOW_WIDTH / 2 * splitLength;
    }
  };

  test_.nbFrames = 0;
  int lastNbFrames = 0;
  double lastTime = glfwGetTime();
  double beginTime = lastTime;
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
      // glfwSetWindowTitle(window, std::to_string((test_.nbFrames - lastNbFrames) / deltaTime).c_str());
      double fr = (test_.nbFrames - lastNbFrames) / deltaTime;
      frm += std::to_string(fr) + "\n";
      lastNbFrames = test_.nbFrames;
      lastTime = thisTime;
    }
    if (thisTime - beginTime > 10) {
      glfwSetWindowShouldClose(window, true);
      break;
    }

    glfwSwapBuffers(window);
    glfwPollEvents();
    multiMouseSystem.PollMouseEvents();
  }

  FILE *frmf = fopen("framerate_wh.txt", "w");
  fwrite(frm.c_str(), frm.size(), 1, frmf);
  fclose(frmf);

  mouseRenderer.FreeLayers();
  postMouseRenderer.FreeLayers();
  return 0;

}