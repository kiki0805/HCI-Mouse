#ifndef DISPLAY_SIMPLECHESS_H
#define DISPLAY_SIMPLECHESS_H

#include "common.h"
#include "layerobject.h"
#include "renderer.h"
#include "shader.h"

#include <vector>

namespace npnx {

enum class CursorAdjustState
{
  INACTIVATED, READY, PUSHED
};

class SimpleChess{
public:
  SimpleChess();
  ~SimpleChess();

  void Init();
  void Draw(const int nbFrames);
  void CheckEnd();

public:
  GLFWwindow *windowPtr;
  bool inProgress = true;
  int nextColor = 1;
  int chess[19][19] = {0};
  float chessAnchor[19][19][2];
  float heightSep = 0.053f / WINDOW_HEIGHT * WINDOW_WIDTH;
  float widthSep = 0.053f;
  float coinHeight = 0.053f / WINDOW_HEIGHT * WINDOW_WIDTH;
  float coinWidth = 0.053f;
  float rulerRatio = 0.3f;
  LayerObject *postLayer = NULL;

  CursorAdjustState cursorState = CursorAdjustState::INACTIVATED;
  double cursorOriginX = 0, cursorOriginY = 0, cursorSensitivityX = 1.0, cursorSensitivityY = 1.0;

private: 
  std::vector<LayerObject *> layers;
  std::vector<Renderer *> renderers;
  std::vector<Shader *> shaders;
  unsigned int blackCoinTex = 0, whiteCoinTex = 0;
};

extern SimpleChess simpleChess;

void mouse_button_callback(GLFWwindow *window, int button, int action, int mods);
void mouse_pos_callback(GLFWwindow *window, double x, double y);
void key_callback(GLFWwindow *window, int key, int scancode, int action, int mods);

}

#endif // !DISPLAY_SIMPLECHESS_H