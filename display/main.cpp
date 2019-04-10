#include "common.h"

#include <string>
#include <memory>
#include <cassert>
#include <time.h>       /* time */
#include <stdlib.h>
#include "layerobject.h"
#include "shader.h"
#include "renderer.h"

#include "imageUtils.h"
#include "IOUtils.h"
#define bit_len 248

int image_shift = 0;
void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
	if (action != GLFW_PRESS) return;
}

int main()
{

	std::string prefix = "fremw_";
	srand(time(NULL));
	NPNX_LOG(NPNX_DATA_PATH);
	glfwInit();
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
	glfwWindowHint(GLFW_AUTO_ICONIFY, GLFW_FALSE);

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
		// if (screen_x == 2560) {
		// 	holographic_screen = i;
		// }
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

	glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);
	glEnable(GL_BLEND);
	glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO);


	npnx::Shader defaultShader;
	defaultShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("movingFrag.glsl"));
	defaultShader.Use();
	glUniform1i(glGetUniformLocation(defaultShader.mShader, "texture0"), 0);
	glUniform1i(glGetUniformLocation(defaultShader.mShader, "nbFrame"), 0);
	glUniform1f(glGetUniformLocation(defaultShader.mShader, "xTrans"), 0.0f);
	glUniform1f(glGetUniformLocation(defaultShader.mShader, "yTrans"), 0.0f);

	npnx::Renderer renderer(&defaultShader, 0);
	npnx::RectLayer rect(-1.0f, -1.0f, 1.0f, 1.0f, 1.0);
	rect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("white.png")));
	renderer.AddLayer(&rect);

	renderer.Initialize();
	int nbFrames = 0;
	glfwSetKeyCallback(window, key_callback);
	int lastNbFrames = 0;
	double lastTime = glfwGetTime();
	double thisTime = glfwGetTime();
	while (!glfwWindowShouldClose(window)) {

		// glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
		// glClear(GL_COLOR_BUFFER_BIT);
		glUniform1i(glGetUniformLocation(defaultShader.mShader, "nbFrame"), nbFrames);
		renderer.Draw(nbFrames);
		nbFrames++;
		double thisTime = glfwGetTime();
    double deltaTime = thisTime - lastTime;
    if (deltaTime > 1.0)
    {
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
