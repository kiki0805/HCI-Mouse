// #include <glad/glad.h> 
//////////////////// WINDOWS
#define OS_STRING "Windows"
#define _USE_MATH_DEFINES
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
#define bit_len 62
// g++ one_value.cpp -o one -Ibuild/include build/src/glad.c -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl

using namespace std;


int main() {
	int init_ret = glfwInit();
	assert(init_ret == 1);

	int monitorCount;
	GLFWmonitor** pMonitor = glfwGetMonitors(&monitorCount);

	int holographic_screen = -1;
	for (int i = 0; i < monitorCount; i++) {
		int screen_x, screen_y;
		const GLFWvidmode * mode = glfwGetVideoMode(pMonitor[i]);
		screen_x = mode->width;
		screen_y = mode->height;
		std::cout << "Screen size is X = " << screen_x << ", Y = " << screen_y << std::endl;
		//if (screen_x == 1366 && screen_y == 768) {
		if (screen_x == 1920 && screen_y == 1080) {
			holographic_screen = i;
		}
	}
	std::cout << holographic_screen << std::endl;

	GLFWwindow* window;
	if (OS_STRING == "Ubuntu")
		window = glfwCreateWindow(300, 300, "My Title", NULL, NULL);
	else
		//window = glfwCreateWindow(1366,768, "Holographic projection", pMonitor[holographic_screen], NULL);

		window = glfwCreateWindow(1920, 1080, "Holographic projection", pMonitor[holographic_screen], NULL);
	if (!window) {
		printf("Window or OpenGL context creation failed\n");
	}
	glfwMakeContextCurrent(window);
	if (OS_STRING == "Ubuntu")
		glViewport(0, 0, 300, 300);
	// glViewport(0, 0, 1366, 768);
	else
		glViewport(0, 0, 1920, 1080);
	//glViewport(0, 0, 1366, 768);

// if (!gladLoadGLLoader((GLADloadproc) glfwGetProcAddress)) {
//     std::cout << "Failed to initialize OpenGL context" << std::endl;
//     return -1;
// }

	GLenum err = glewInit();
	assert(GLEW_OK == err);
	fprintf(stdout, "Status: Using GLEW %s\n", glewGetString(GLEW_VERSION));

#ifdef __linux__ 
	if (glxewIsSupported("GLX_MESA_swap_control")) {
		printf("OK, we can use GLX_MESA_swap_control\n");
	}
	else {
		printf("[WARNING] GLX_MESA_swap_control is NOT supported.\n");
	}
	glXSwapIntervalMESA(1);
	printf("Swap interval: %d\n", glXGetSwapIntervalMESA());

	// if (glxewIsSupported("GLX_SGI_swap_control")) {
	//     printf("OK, we can use GLX_SGI_swap_control\n");
	// } else {
	//     printf("[WARNING] GLX_SGI_swap_control is NOT supported.\n");
	// }
	// glXSwapIntervalSGI(1);
#elif _WIN32
	if (wglewIsSupported("WGL_EXT_swap_control")) {
		printf("OK, we can use WGL_EXT_swap_control\n");
	}
	else {
		printf("[WARNING] WGL_EXT_swap_control is NOT supported.\n");
	}
	wglSwapIntervalEXT(1);
#else

#endif
	double count = 0.0f;
	double color;
	double freqs[] = { 40.0f, 240.0f };
	int i = 0;
	double freq = freqs[0];
	int index = 0;
	double colors[] = { 64.0f, 128.0f, 192.0f };
	float baseColor = 32.0f;
	float tmpColor;
	bool f = true;
	int nbFrames = 0;
	float diff = 20.0f;
	int c = 0;
	while (!glfwWindowShouldClose(window)) {

		if (nbFrames % 2 == 0) {
			tmpColor = baseColor - diff;
			glClearColor(tmpColor / 255.0f, tmpColor / 255.0f, tmpColor / 255.0f, 1.0f);
		}
		else if (nbFrames % 2 == 1) {
			tmpColor = baseColor + diff;
			glClearColor(tmpColor / 255.0f, tmpColor / 255.0f, tmpColor / 255.0f, 1.0f);
		}
		if (nbFrames % (2 * 240) == 0 && nbFrames != 0) {
			baseColor += 8.0f;
            if(baseColor > 192.0f) break;
		}
		nbFrames++;
		//color = (cos(2.0*M_PI*freq*((double)count / 240.0)) + 1.0) / 2.0 * 0.3 + 0.35;
		//cout << (cos(2.0*M_PI*freq*((double)count / 240.0)) + 1.0) / 2.0 * 0.3 + 0.35<< endl;
		glClear(GL_COLOR_BUFFER_BIT);

		glfwSwapBuffers(window);
		glfwPollEvents();
	}

	// free_bit_arr((struct bit_ele*)::begin->first_bit);

	glfwTerminate();
	return 0;
}
