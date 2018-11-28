#include <GL/glew.h>

#ifdef _WIN32
#include <GL/wglew.h>
#endif

#ifdef __linux__
#include <GL/glxew.h>
#endif

#include <GLFW/glfw3.h>
#include <cassert>
#include <cstdlib> // for exit()
#include <iostream>
#include <fstream>
#include <string>

#define NPNX_ASSERT(A) do { \
  std::cerr << #A << (A) << std::endl; \
  if (!(A)) { \
    glfwTerminate(); \
    exit(-1); \
  } \
} while (false) 

int main() 
{
  glfwInit();
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
  glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
  
  GLFWwindow *window = glfwCreateWindow(800, 600, "hello", NULL, NULL);
  NPNX_ASSERT(window);
  glfwMakeContextCurrent(window);

  glewExperimental = GL_TRUE;
  GLenum err = glewInit();
  assert(!err);
  
  glViewport(0, 0, 800, 600);

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

  float vertices[] = {
    -0.9f, -0.9f, 0.0f,
    0.9f, -0.9f, 0.0f,
    0.9f, 0.9f, 0.0f,
    -0.9f, 0.9f, 0.0f
  };
  unsigned int indices[] = {
    0, 1, 2,
    0, 2, 3
  };


  unsigned int VAO;
  glGenVertexArrays(1, &VAO);
  std::cout.flush();
  unsigned int VBO;
  glGenBuffers(1, &VBO);  
  unsigned int EBO;
  glGenBuffers(1, &EBO);
  glBindVertexArray(VAO);
  glBindBuffer(GL_ARRAY_BUFFER, VBO);
  glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
  glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(indices), indices, GL_STATIC_DRAW);
  
  glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
  glEnableVertexAttribArray(0);

  std::cout.flush();
  const char *vertexShaderCode = "#version 330 core\n"
    "layout (location = 0) in vec3 aPos;\n"
    "void main()\n"
    "{\n"
    "   gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);\n"
    "}\0";
  const char *fragShaderCode = "#version 330 core\n"
    "out vec4 FragColor;\n"
    "void main()\n"
    "{\n"
    "   FragColor = vec4(1.0f, 0.5f, 0.2f, 1.0f);\n"
    "}\n\0";

  unsigned int vertexShader = glCreateShader(GL_VERTEX_SHADER);
  glShaderSource(vertexShader, 1, &vertexShaderCode, NULL);
  glCompileShader(vertexShader);
  int success;
  char log[512];
  glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
  if (!success) {
    glGetShaderInfoLog(vertexShader, 512, NULL, log);
  }

  unsigned int fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
  glShaderSource(fragmentShader, 1, &fragShaderCode, NULL);
  glCompileShader(fragmentShader);

  glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
  if (!success)
  {
    glGetShaderInfoLog(fragmentShader, 512, NULL, log);
    NPNX_ASSERT(log);
  }

  unsigned int shaderProgram;
  shaderProgram = glCreateProgram();
  glAttachShader(shaderProgram, vertexShader);
  glAttachShader(shaderProgram, fragmentShader);
  glLinkProgram(shaderProgram);
  glGetProgramiv(shaderProgram, GL_LINK_STATUS, &success);
  if (!success)
  {
    glGetProgramInfoLog(shaderProgram, 512, NULL, log);
    NPNX_ASSERT(log);
  }
  glDeleteShader(vertexShader);
  glDeleteShader(fragmentShader);


  int nbFrames = 0;
  double lastTime = glfwGetTime();
  while (!glfwWindowShouldClose(window)) {
    glfwSwapBuffers(window);
    glfwPollEvents();

    glClearColor(0.5f, 0.5f, 0.1f, 0.9f);
    glClear(GL_COLOR_BUFFER_BIT);

    nbFrames++;
    double thisTime = glfwGetTime();
    double deltaTime = thisTime - lastTime;
    if (deltaTime > 1.0) {
      glfwSetWindowTitle(window, std::to_string(nbFrames/deltaTime).c_str());
      nbFrames = 0;
      lastTime = thisTime;
    }

    glUseProgram(shaderProgram);
    glBindVertexArray(VAO);
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
    glBindVertexArray(0);

  }
  
  glfwTerminate();
  return 0;
}
