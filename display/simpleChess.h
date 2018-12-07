#ifndef DISPLAY_SIMPLECHESS_H
#define DISPLAY_SIMPLECHESS_H

#include "common.h"
#include "layerobject.h"
#include "renderer.h"
#include "shader.h"

#include <vector>

namespace npnx {

class SimpleChess{
public:
  SimpleChess();
  ~SimpleChess();

  void Init();
  void Draw(const int nbFrames);
  void CheckEnd();

public:
  bool inProgress = true;
  int nextColor = 1;
  int chess[3][3] = {0};
  float chessAnchor[3][3][2];
  float heightSep = 0.57f;
  float widthSep = 0.33f;
  float coinHeight = 0.33f;
  float coinWidth = 0.185f;
  LayerObject *postLayer = NULL;

private: 
  std::vector<LayerObject *> layers;
  std::vector<Renderer *> renderers;
  std::vector<Shader *> shaders;
  unsigned int blackCoinTex = 0, whiteCoinTex = 0;
};

extern SimpleChess simpleChess;

void __cdecl mouse_button_callback(GLFWwindow *window, int button, int action, int mods);
}

#endif // !DISPLAY_SIMPLECHESS_H