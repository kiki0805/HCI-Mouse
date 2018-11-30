#ifndef DISPLAY_RENDERER_H_
#define DISPLAY_RENDERER_H_

#include <vector>
#include <map>

#include "shader.h"

namespace npnx {

class LayerObject;

class Renderer {
public:
  explicit Renderer(Shader *defaultShader);
  ~Renderer();
  
  int AddLayer(LayerObject * layer);
  void Initialize();
  
  void Draw(const int nbFrames);

private:
  //we can only add layers when the renderer is not initialized.
  bool mInitialized = false;
  std::map<float, LayerObject *> mLayers;

public:  
  std::vector<float> mVBOBuffer;
  std::vector<GLuint> mEBOBuffer;
  unsigned int mVAO, mVBO, mEBO;
  Shader *mDefaultShader;
};


}
#endif // !DISPLAY_REDERER_H_