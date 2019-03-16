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
#include "curvelayer.h"
#include "curvedata.h"

using namespace npnx;

const int num_position_texture = 248;
int image_shift = 0;

class Test_Slider {
public:
  ~Test_Slider();
  GLFWwindow * window;
  DragRectLayer * targetRect;
  int bgIndex = 0;
  int testCount = 0;
  int testCount2 = 0;
  bool running = false;
  int nbFrames = 0;
  FILE * mousePathFile;
  std::vector<CurveLayer *> curves;
  std::vector<DragRectLayer *> sourceCircles;
  std::vector<DragRectLayer *> targetCircles;
}; 
  

Test_Slider::~Test_Slider(){
  for (auto it: curves) {
    delete it;
  }
  for (auto it: sourceCircles) {
    delete it;
  }
  for (auto it: targetCircles) {
    delete it;
  }
  curves.clear();
  sourceCircles.clear();
  targetCircles.clear();
}

class Player_Slider {
public:
  int curveIdx = 0;
  int nextDrawFrame = -1;
  bool drawing = false;
  std::chrono::high_resolution_clock::time_point displayTime;
};

Test_Slider test_;
Player_Slider player_[2];

auto truefunc = [] (int) -> bool {return true;};
auto falsefunc = [] (int) -> bool {return false;};

void curveFadeout(int curveid, int playerid, int fade_in_frames = 120) {
  int layerid = curveid * 2 + playerid;
  test_.curves[layerid]->visibleCallback = falsefunc;
  test_.sourceCircles[layerid] -> visibleCallback = falsefunc;
  int shouldFadeAt = test_.nbFrames + fade_in_frames;
  test_.targetCircles[layerid] -> visibleCallback = [&, shouldFadeAt](int nbFrames){return nbFrames < shouldFadeAt;};
  test_.targetCircles[layerid] -> textureNoCallback = [](int) {return 1;};
}

void curveFadein(int curveid, int playerid, int delay_in_frames) {
  int layerid = curveid * 2 + playerid;
  int shouldVisibleAt = test_.nbFrames + delay_in_frames;
  auto delayvisiblefunc = [&, shouldVisibleAt] (int nbFrames) {return nbFrames > shouldVisibleAt;};
  test_.curves[layerid] ->visibleCallback = delayvisiblefunc;
  test_.sourceCircles[layerid] -> visibleCallback = delayvisiblefunc;
  test_.targetCircles[layerid] -> textureNoCallback = [](int) {return 0;};
  test_.targetCircles[layerid] -> visibleCallback = delayvisiblefunc;
}

void mouse_button_callback(int hDevice, int button, int action, double screenX, double screenY) 
{
  // if (hDevice != 0) return;
  if (button == 0x00000001 && action == GLFW_PRESS) {
    if (test_.running == false) {
      for (int pid = 0; pid < 2; pid++) {
        int ndf = (int)((double)rand() / RAND_MAX * 240 + 120);
        player_[pid].nextDrawFrame = test_.nbFrames + ndf;
        curveFadein(player_[pid].curveIdx, pid, ndf);
      }
      test_.running = true;
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

void save_respondtime_to_file(int pid, double respondTimer)
{
  freopen("slider_hci_mutl_.txt","a",stdout);
  printf("%d %.4lf\n",pid, respondTimer);
  freopen("CON","a",stdout);
  return ;
}


void before_every_frame() 
{
  for (int pid = 0; pid < 2; pid++) {
    if (test_.nbFrames == player_[pid].nextDrawFrame) {
      player_[pid].displayTime = std::chrono::high_resolution_clock::now();
      player_[pid].drawing = true;
    }

    if (!player_[pid].drawing) continue;
    double x,y;
    if (multiMouseSystem.GetNumMouse() == 0) {
      glfwGetCursorPos(test_.window, &x, &y);
      x = (double)(x - WINDOW_WIDTH / 2) / (WINDOW_WIDTH / 2);
      y = - (double) (y - WINDOW_HEIGHT / 2) / (WINDOW_HEIGHT / 2);
      if (test_.targetCircles[player_[pid].curveIdx * 2 + pid] -> isInside(x, y, test_.nbFrames)) {
        double respondTimer = (double) std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now() - player_[pid].displayTime).count();
        respondTimer /= 1e6;
        printf("pid:%d respondTime:%lf\n", 
          pid,
          respondTimer
        );
        save_respondtime_to_file(pid, respondTimer);
        // test_.testCount ++;
        // if (test_.testCount % 10 == 0) {
        //   std::cout<<"change background" << std::endl;
        //   test_.bgIndex ++;
        //   test_.bgIndex %= 3;
        // }
        curveFadeout(player_[pid].curveIdx, pid, 120);
        player_[pid].curveIdx += 1;
        player_[pid].curveIdx %= MAX_PREDEFINED_CURVES;
        int ndf = (int)((double)rand() / RAND_MAX * 240 + 120);
        player_[pid].nextDrawFrame = test_.nbFrames + ndf;
        curveFadein(player_[pid].curveIdx, pid, ndf);
        player_[pid].drawing = false;
      }
    } else {
      for (int mouseid = 0; mouseid < multiMouseSystem.GetNumMouse(); mouseid++) {
        multiMouseSystem.GetCursorPos(mouseid, &x, &y);
        if (test_.targetCircles[player_[pid].curveIdx * 2 + pid] -> isInside(x, y, test_.nbFrames)) {
          double respondTimer = (double) std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now() - player_[pid].displayTime).count();
          respondTimer /= 1e6;
          printf("pid:%d respondTime:%lf\n", 
            pid,
            respondTimer
          );
          save_respondtime_to_file(pid, respondTimer);
          // test_.testCount2 ++;
          // if (test_.testCount2 % 10 == 0) {
          //   std::cout<<"change background" << std::endl;
          //   test_.bgIndex ++;
          //   test_.bgIndex %= 3;
          // }
          curveFadeout(player_[pid].curveIdx, pid, 120);
          player_[pid].curveIdx += 1;
          player_[pid].curveIdx %= MAX_PREDEFINED_CURVES;
          int ndf = (int)((double)rand() / RAND_MAX * 240 + 120);
          player_[pid].nextDrawFrame = test_.nbFrames + ndf;
          curveFadein(player_[pid].curveIdx, pid, ndf);
          player_[pid].drawing = false;
          break; // if one mouse is hitting the object, do not test for the other mouses.
        }
      }
    }
  }
}

void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods)
{
  // std::cout<<"change background"<<std::endl;
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
  test_.mousePathFile = fopen(NPNX_FETCH_DATA("mouse_path.dat"), "w");
  std::string frm;
  frm.reserve(2000000);
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
  // adjustShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("newAdjFrag.glsl"));
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
  bg.textureNoCallback = [&](int _) {return test_.bgIndex; };
  renderer.AddLayer(&bg);

  // RectLayer bgb(-(double)WINDOW_HEIGHT / WINDOW_WIDTH, -1.0f, (double)WINDOW_HEIGHT / WINDOW_WIDTH, 1.0f, -9.0f);
  // bgb.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("goboard.jpg")));
  // renderer.AddLayer(&bgb);

  std::vector<CurveLayer *> & curves = test_.curves;
  std::vector<DragRectLayer *> & sourceCircles = test_.sourceCircles;
  std::vector<DragRectLayer *> & targetCircles = test_.targetCircles;

  GLuint curveEndTex = makeTextureFromImage(NPNX_FETCH_DATA("sliderb.png"));
  GLuint curveBeginTex = makeTextureFromImage(NPNX_FETCH_DATA("sliderb1.png"));
  GLuint curveBodyTex = makeTextureFromImage(NPNX_FETCH_DATA("bar.png"));
  GLuint curvePassedTex = makeTextureFromImage(NPNX_FETCH_DATA("passed.png"));

  for (int i = 0; i < MAX_PREDEFINED_CURVES; i++) {
    for (int j = 0; j < 2; j++) {
      CurveLayer * curve = new CurveLayer(predefinedCurves[i], 150.0f, 50.0f+0.1f * (i * 2 + j) , j == 0);
      curve->mTexture = curveBodyTex;
      curve->visibleCallback = falsefunc;
      renderer.AddLayer(curve);
      curves.push_back(curve);
    
      const float targetVSize = 0.2f;
      const float targetHSize = targetVSize * WINDOW_HEIGHT / WINDOW_WIDTH;
      DragRectLayer* sourceRect = new DragRectLayer(-targetHSize / 2, -targetVSize / 2, targetHSize / 2, targetVSize / 2, 100.0f+0.1f * (i * 2 + j) , j == 0);
      sourceRect->mTexture.push_back(curveBeginTex);
      sourceRect->mATransX = predefinedCurves[i][0];
      sourceRect->mATransY = predefinedCurves[i][1];
      sourceRect->visibleCallback = falsefunc;
      renderer.AddLayer(sourceRect);
      sourceCircles.push_back(sourceRect);

      DragRectLayer* targetRect = new DragRectLayer(-targetHSize / 2, -targetVSize / 2, targetHSize / 2, targetVSize / 2, 200.0f+0.1f * (i * 2 + j), j == 0);
      targetRect->mTexture.push_back(curveEndTex);
      targetRect->mTexture.push_back(curvePassedTex);
      int s = predefinedCurves[i].size();
      targetRect->mATransX = predefinedCurves[i][s - 6];
      targetRect->mATransY = predefinedCurves[i][s - 5];
      targetRect->textureNoCallback = [] (int) {return 0;};
      targetRect->visibleCallback = falsefunc;
      renderer.AddLayer(targetRect);
      targetCircles.push_back(targetRect);
    }
  }
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
  multiMouseSystem.mEnableAngle = true;
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
    glUniform1i(glGetUniformLocation(adjustShader.mShader, "nbFrames"), test_.nbFrames);

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
    if (thisTime - beginTime > 110) {
      glfwSetWindowShouldClose(window, true);
      break;
    }

    glfwSwapBuffers(window);
    glfwPollEvents();
    multiMouseSystem.PollMouseEvents();
  }
  mouseRenderer.FreeLayers();
  postMouseRenderer.FreeLayers();

  FILE *frmf = fopen("framerate_sl.txt", "w");
  fwrite(frm.c_str(), frm.size(), 1, frmf);
  fclose(frmf);

  fclose(test_.mousePathFile);
  return 0;

}