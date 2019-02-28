// #include <glad/glad.h> 
//////////////////// WINDOWS
#include "pch.h"
#include <GL/glew.h>
#include <GL/wglew.h>
#define OS_STRING "Windows"

//////////////////UBUNTU
// #include <GL/glew.h>
// #include <GL/glxew.h>
// #define OS_STRING "Ubuntu"

//////////////////////////////

#include <GLFW/glfw3.h>

#include <stdio.h>
#include <assert.h>
#include "utils.h"
#include <iostream>
// g++ one_value.cpp -o one -Ibuild/include build/src/glad.c -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl

using namespace std;
float global_R;
float global_G;
float global_B;
float white;

int x;
int y;

GLfloat *pixels_map;
GLfloat *colors_map;


void change_output() {
	int color_count = 0;
	for (int i = 0; i < x; i++) {
		for (int j = 0; j < y; j++) {
			if (i % 4 >= 2) {
				*(colors_map + color_count) = global_R;
				*(colors_map + color_count + 1) = global_G;
				*(colors_map + color_count + 2) = global_B;
			}
			color_count += 3;
		}
	}
}


void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
	if (action == GLFW_PRESS) {
		switch (key) {
		case GLFW_KEY_Q: {
			global_R -= 0.1;
			global_R = max(0.0f, global_R);
			cout << "R " << global_R << endl;
			break;
		}
		case GLFW_KEY_W: {
			global_R += 0.1;
			global_R = min(1.0f, global_R);
			cout << "R " << global_R << endl;
			break;
		}
		case GLFW_KEY_A: {
			global_G -= 0.1;
			global_G = max(0.0f, global_G);
			cout << "G " << global_G << endl;
			break;
		}
		case GLFW_KEY_S: {
			global_G += 0.1;
			global_G = min(1.0f, global_G);
			cout << "G " << global_G << endl;
			break;
		}
		case GLFW_KEY_Z: {
			global_B -= 0.1;
			global_B = max(0.0f, global_B);
			cout << "B " << global_B << endl;
			break;
		}
		case GLFW_KEY_X: {
			global_B += 0.1;
			global_B = min(1.0f, global_B);
			cout << "B " << global_B << endl;
			break;
		}
		}
		change_output();
		cout << "RGB: " << global_R << " " << global_G << " " << global_B << endl;
	}
}



int main() {
	x = 500;
	y = 500;

	pixels_map = (GLfloat*)malloc(x * y * 2 * sizeof(GLfloat));
	colors_map = (GLfloat*)malloc(x * y * 3 * sizeof(GLfloat));
	white = 1.0f;
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
		if (screen_x == 1920 && screen_y == 1080) {
			holographic_screen = i;
		}
	}
	std::cout << holographic_screen << std::endl;

	GLFWwindow* window;
	if (OS_STRING == "Ubuntu")
		window = glfwCreateWindow(300, 300, "My Title", NULL, NULL);
	else
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
	glOrtho(0, 1920, 0, 1080, 0, 1); // essentially set coordinate system
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

	int pixel_count = 0;
	int color_count = 0;
	for (int i = 0; i < x; i++) {
		for (int j = 0; j < y; j++) {
			pixels_map[pixel_count] = i;
			pixels_map[pixel_count + 1] = j;
			pixel_count += 2;
			if (i % 6 < 3) {
				*(colors_map + color_count) = white;
				*(colors_map + color_count + 1) = white;
				*(colors_map + color_count + 2) = white;
			}
			else {
				*(colors_map + color_count) = global_R;
				*(colors_map + color_count + 1) = global_G;
				*(colors_map + color_count + 2) = global_B;
			}
			color_count += 3;
		}
	}
	int cnt = 0;
	global_R = 0.5f;
	global_G = 0.5f;
	global_B = 0.5f;
	glfwSetKeyCallback(window, key_callback);

	int pointNum = x * y;
	while (!glfwWindowShouldClose(window)) {
		//glClearColor(global_R, global_G, global_B, 1.0f);
		glClear(GL_COLOR_BUFFER_BIT);

		glEnableClientState(GL_VERTEX_ARRAY);
		glEnableClientState(GL_COLOR_ARRAY);

		glVertexPointer(2, GL_FLOAT, 0, pixels_map);
		glColorPointer(3, GL_FLOAT, 0, colors_map);
		glDrawArrays(GL_POINTS, 0, pointNum);

		glDisableClientState(GL_COLOR_ARRAY);
		glDisableClientState(GL_VERTEX_ARRAY);

		glfwSwapBuffers(window);
		glfwPollEvents();
	}

	// free_bit_arr((struct bit_ele*)::begin->first_bit);

	glfwTerminate();
	return 0;
}
