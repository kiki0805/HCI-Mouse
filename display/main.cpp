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
bool post1 = true;
bool post2 = false;
void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
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
	case GLFW_KEY_C:
		post1 = !post1;
		post2 = !post2;
		std::cout << post1 << " " << post2 << std::endl;
		break;
	default:
		break;
	}
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


	npnx::Shader defaultShader;
	defaultShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("defaultFragment.glsl"));
	defaultShader.Use();
	glUniform1i(glGetUniformLocation(defaultShader.mShader, "texture0"), 0);

	npnx::Shader adjustShader;
	adjustShader.LoadShader(NPNX_FETCH_DATA("defaultVertex.glsl"), NPNX_FETCH_DATA("adjustFragment.glsl"));
	adjustShader.Use();
	glUniform1i(glGetUniformLocation(adjustShader.mShader, "texture0"), 0);
	glUniform1i(glGetUniformLocation(adjustShader.mShader, "rawScreen"), 1);
	glUniform1i(glGetUniformLocation(adjustShader.mShader, "letThrough"), 0);
	glUniform1i(glGetUniformLocation(adjustShader.mShader, "val"), 0);

	unsigned int fbo0, fboColorTex0;
	generateFBO(fbo0, fboColorTex0);

	npnx::Renderer renderer(&defaultShader, fbo0);
	npnx::Renderer postRenderer(&adjustShader, 0);
	postRenderer.mDefaultTexture.assign({ 0, fboColorTex0 });

	// --------------- Add your layer here--------------//  
	npnx::RectLayer baseRect(-1.0f, -1.0f, 1.0f, 1.0f, -1.0f);
	baseRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("grey_1920_1080.png")));
	//baseRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("test.png")));
	renderer.AddLayer(&baseRect);

	npnx::RectLayer upperRect(-0.5f, -0.1f, -0.2f, 0.8f, 0.0f);
	std::unique_ptr<unsigned char> anotherBuffer(new unsigned char[600 * 600 * 3]);
	generateRandomArray(anotherBuffer.get(), 600 * 600 * 3, 0, 255);
	upperRect.mTexture.push_back(makeTexture(anotherBuffer.get(), 600, 600, 3));
	upperRect.visibleCallback = [](int nbFrames) {
		return (nbFrames & 255) < 128;
	};
	//renderer.AddLayer(&upperRect);

	npnx::RectLayer postBaseRect(-1.0f, -1.0f, 1.0f, 1.0f, -999.0f);
	postBaseRect.beforeDraw = [&](const int nbFrames) {
		glUniform1i(glGetUniformLocation(postBaseRect.mParent->mDefaultShader->mShader, "letThrough"), 1);
		return 0;
	};
	postBaseRect.afterDraw = [&](const int nbFrames) {
		glUniform1i(glGetUniformLocation(postBaseRect.mParent->mDefaultShader->mShader, "letThrough"), 0);
		return 0;
	};
	postBaseRect.mTexture.push_back(0);
	postRenderer.AddLayer(&postBaseRect);

	npnx::RectLayer postRect(-0.5625f, -1.0f, 0.5625f, 1.0f, 9999.9f);
	//unsigned int circleTex = makeTextureFromImage(NPNX_FETCH_DATA("space2_test_1.png"));
	//unsigned int whiteTex = makeTextureFromImage(NPNX_FETCH_DATA("space2_test_2.png"));
	for (int i = 0; i < bit_len; i++) {
		std::string img_name = prefix + std::to_string(i) + ".png";
		unsigned int bit = makeTextureFromImage(NPNX_FETCH_DATA(img_name));
		postRect.mTexture.push_back(bit);
	}
	postRect.visibleCallback = [](int nbFrames) {
		return post1;
	};
	postRect.textureNoCallback = [](int nbFrames) {
		return nbFrames % 62 + image_shift;
	};

	npnx::RectLayer leftRect(-1.0f, -1.0f, 0.0f, 1.0f, 100.0f);
	leftRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("left0.png")));
	leftRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("left1.png")));
	leftRect.visibleCallback = [](int nbFrames) {
		return true;
	};
	leftRect.textureNoCallback = [](int nbFrames) {
		return nbFrames % bit_len;
	};

	npnx::RectLayer rightRect(0.0f, -1.0f, 1.0f, 1.0f, 200.0f);
	rightRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("right0.png")));
	rightRect.mTexture.push_back(makeTextureFromImage(NPNX_FETCH_DATA("right1.png")));
	rightRect.visibleCallback = [](int nbFrames) {
		return true;
	};
	rightRect.textureNoCallback = [](int nbFrames) {
		return nbFrames % bit_len;
	};

	postRenderer.AddLayer(&postRect);
	//postRenderer.AddLayer(&rightRect);
	//postRenderer.AddLayer(&leftRect);
	// ------------------------------------------------//
	renderer.Initialize();
	postRenderer.Initialize();

	int nbFrames = 0;
	glfwSetKeyCallback(window, key_callback);
	int lastNbFrames = 0;
	double lastTime = glfwGetTime();
	double thisTime = glfwGetTime();
	while (!glfwWindowShouldClose(window)) {

		// if (renderer.Updated(nbFrames) || postRenderer.Updated(nbFrames)) {
		renderer.Draw(nbFrames);
		postRenderer.Draw(nbFrames);
		// }

		nbFrames++;

		glfwSwapBuffers(window);
		glfwPollEvents();
	}

	glfwTerminate();
	return 0;
}
