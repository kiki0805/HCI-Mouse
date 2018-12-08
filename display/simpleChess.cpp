#include "common.h"
#include "simpleChess.h"

#include "imageUtils.h"
#include <cstdlib>

using namespace npnx;

SimpleChess::SimpleChess()
{}

SimpleChess::~SimpleChess()
{
  for (auto it: shaders) {
    delete it;
  }
  for (auto it: renderers) {
    delete it;
  }
  for (auto it: layers) {
    delete it;
  }
}

void SimpleChess::Init()
{
  glEnable(GL_BLEND);
  glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO);

  Shader *defaultShader = new Shader;
  defaultShader->LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("defaultFragment.glsl"));
  defaultShader->Use();
  glUniform1i(glGetUniformLocation(defaultShader->mShader, "texture0"), 0);
  shaders.push_back(defaultShader);

  Shader *adjustShader = new Shader;
  adjustShader->LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("adjustFragment1.glsl"));
  adjustShader->Use();
  glUniform1i(glGetUniformLocation(adjustShader->mShader, "texture0"), 0);
  glUniform1i(glGetUniformLocation(adjustShader->mShader, "rawScreen"), 1);
  glUniform1i(glGetUniformLocation(adjustShader->mShader, "letThrough"), 0);
  shaders.push_back(adjustShader);

  unsigned int fbo0, fboColorTex0;
  generateFBO(fbo0, fboColorTex0);

  Renderer *renderer = new Renderer(defaultShader, fbo0);
  Renderer *postRenderer = new Renderer(adjustShader, 0);
  postRenderer->mDefaultTexture.assign({0, fboColorTex0});
  renderers.push_back(renderer);
  renderers.push_back(postRenderer);

  
  RectLayer *bg = new RectLayer(-1.0f, -1.0f, 1.0f, 1.0f, -999.0f);
  bg->mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("test.png")));
  renderer->AddLayer(bg);
  layers.push_back(bg);
  
  const float boardup = 0.9f;
  RectLayer *board = new RectLayer(-boardup * WINDOW_HEIGHT / WINDOW_WIDTH,
                                   -boardup,
                                   boardup * WINDOW_HEIGHT / WINDOW_WIDTH,
                                   boardup, 
                                   -99.0f);
  board->mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("board.png")));
  renderer->AddLayer(board);
  layers.push_back(board);

  blackCoinTex = makeTextureFromImage(NPNX_FETCH_DATA("red.png"));
  whiteCoinTex = makeTextureFromImage(NPNX_FETCH_DATA("green.png"));

  RectLayer *promptCoin = new RectLayer(-0.80f, 0.74f - coinHeight, -0.8f + coinWidth, 0.74f, -10.0f);
  promptCoin->mTexture.push_back(blackCoinTex);
  promptCoin->mTexture.push_back(whiteCoinTex);
  promptCoin->visibleCallback = [=](int nbFrames) {
    return this->inProgress == true;
  };
  promptCoin->textureNoCallback = [=](int nbFrames) {
    return this->nextColor - 1;
  };  
  renderer->AddLayer(promptCoin);
  layers.push_back(promptCoin);

  chessAnchor[0][0][0] = -0.42f;
  chessAnchor[0][0][1] = 0.74f;
  for(int i=0; i<3; i++) {
    for(int j=0; j<3; j++){
      if (i!=0 || j!=0) {
        chessAnchor[i][j][0] = chessAnchor[0][0][0] + j * widthSep;
        chessAnchor[i][j][1] = chessAnchor[0][0][1] - i * heightSep;
      }
      RectLayer* thisCoin = new RectLayer(
          chessAnchor[i][j][0],
          chessAnchor[i][j][1] - coinHeight, 
          chessAnchor[i][j][0] + coinWidth,
          chessAnchor[i][j][1],
          i * 0.3f + j * 0.01f // we use map so every layer should not have the same z-index.
          ); // the anchor is top left, while the rect receive bottom left coord.
      thisCoin->visibleCallback = [=] (int nbFrames) {
        if (this->chess[i][j] == 0) return false;
        if (this->inProgress == false && this->chess[i][j] > 2) {
          double tt = glfwGetTime();
          return (tt - (int) tt) > 0.5;
        }
        return true;
      };
      thisCoin->mTexture.push_back(blackCoinTex);
      thisCoin->mTexture.push_back(whiteCoinTex);
      thisCoin->textureNoCallback = [=] (int nbFrames) {
        return (this->chess[i][j] & 1) ? 0:1;
      };
      renderer->AddLayer(thisCoin);
      layers.push_back(thisCoin);
    }
  }

  RectLayer *postBaseRect = new RectLayer(-1.0f, -1.0f, 1.0f, 1.0f, -999.0f);
  postBaseRect->beforeDraw = [=](const int nbFrames) {
    glUniform1i(glGetUniformLocation(postBaseRect->mParent->mDefaultShader->mShader, "letThrough"), 1);
    return 0;
  };
  postBaseRect->afterDraw = [=](const int nbFrames) {
    glUniform1i(glGetUniformLocation(postBaseRect->mParent->mDefaultShader->mShader, "letThrough"), 0);
    return 0;
  };
  postBaseRect->mTexture.push_back(0);
  postRenderer->AddLayer(postBaseRect);
  layers.push_back(postBaseRect);

  RectLayer *postRect = new RectLayer(-0.9f, -0.9f, 0.1f, 0.8f, 999.9f);
  postRect->mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("hitcircle.png")));
  postRect->visibleCallback = [] (int) {return false;};
  postRenderer->AddLayer(postRect);
  layers.push_back(postRect);
  postLayer = postRect; //hack here.

  renderer->Initialize();
  postRenderer->Initialize();
}

void SimpleChess::Draw(const int nbFrames)
{

  renderers[0]->Draw(nbFrames);
  renderers[1]->Draw(nbFrames);
}


void SimpleChess::CheckEnd()
{
  int lines[8][3] = {
    0,1,2,
    3,4,5,
    6,7,8,
    0,3,6,
    1,4,7,
    2,5,8,
    0,4,8,
    2,4,6
  };

  int *chessArray = &chess[0][0];
  bool finished = true;
  bool found = false;
  for(int i = 0; i < 8; i++) {
    if (chessArray[lines[i][0]] == 0) {
      finished = false;
      continue;
    } else {
      int nowSide = chessArray[lines[i][0]];
      for (int j = 1; j < 3; j++) {
        if (chessArray[lines[i][j]] == 0) {finished = false;}
        
        if (nowSide != chessArray[lines[i][j]])
          {
            nowSide = -1;
            break;
        }
      }
      if (nowSide != -1) {
        inProgress = false;
        found = true;
        for(int j=0; j<3; j++) {
          chessArray[lines[i][j]] += 2; 
        }
        break;
      } 
    }
  }

  if (finished && !found) {
    inProgress = false;
    for(int i = 0; i < 9; i++) {
      chessArray[i] +=2;
    }
  }
}


void npnx::mouse_button_callback(GLFWwindow *window, int button, int action, int mods)
{
  double x,y;
  glfwGetCursorPos(window, &x, &y);
  if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_RELEASE) { 
    NPNX_LOG(x);
    NPNX_LOG(y);
  } else {
    return;
  }
  if (simpleChess.inProgress == false)
  {
    simpleChess.inProgress = true;
    memset(&simpleChess.chess[0][0], 0, 9 * sizeof(int));
    simpleChess.nextColor = 1;
    return;
  }
  x = x / (WINDOW_WIDTH / 2) - 1;
  y = WINDOW_HEIGHT - y;
  y = y / (WINDOW_HEIGHT / 2) - 1;
  NPNX_LOG(x);
  NPNX_LOG(y);

  int xidx = (int) ((x - simpleChess.chessAnchor[0][0][0]) / simpleChess.widthSep);
  int yidx = (int) (- (y - simpleChess.chessAnchor[0][0][1]) / simpleChess.heightSep);
  NPNX_LOG(xidx);
  NPNX_LOG(yidx);
  if (xidx >=0 && yidx >=0 && xidx <=2 && yidx <=2 && simpleChess.chess[yidx][xidx] == 0) {
    simpleChess.chess[yidx][xidx] = simpleChess.nextColor;
    simpleChess.nextColor = (simpleChess.nextColor == 1) ? 2 : 1; 
    simpleChess.CheckEnd();
  }
}