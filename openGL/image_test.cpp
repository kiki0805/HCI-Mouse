// #include <glad/glad.h>
#include "pch.h"
#include <GL/glew.h>
// #include <GL/glxew.h>
#include <GL/wglew.h>
#include <GLFW/glfw3.h>
#include "image_process.h"

#include <stdio.h>
#include <assert.h>
#include "utils.h"
#include <iostream>
#include <algorithm>

#define BIT_NUM 2
using namespace std;

// g++ image_test.cpp -o test -Ibuild/include build/src/glad.c -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl `pkg-config --cflags --libs opencv`

void assign_value(GLfloat** colors_map, int*** pixel_arr, int n, int color_index, int i, int j) {
	colors_map[n][color_index] = (float)pixel_arr[i][j][2] / 255.0;
	colors_map[n][color_index + 1] = (float)pixel_arr[i][j][1] / 255.0;
	colors_map[n][color_index + 2] = (float)pixel_arr[i][j][0] / 255.0;
}


int main(void)
{
	Image4Render img_data = Image4Render(1920,1080);
	char n[] = "new_im";
	img_data.read_from_file(n);

	// Image4Render img_data1 = Image4Render(1080, 1080);
	// char n1[] = "im";
	// img_data1.read_from_file(n1);

	Image4Render img_data2 = Image4Render(1920, 1080);
	char n2[] = "new_im2";
	img_data2.read_from_file(n2);


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
		window = glfwCreateWindow(1920, 1080, "Holographic projection", pMonitor[holographic_screen], NULL);
	if (!window) {
		printf("Window or OpenGL context creation failed\n");
	}
	glfwMakeContextCurrent(window);
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

	GLfloat **pixels_map = (GLfloat**)malloc(BIT_NUM * img_data.width * img_data.height * 2 * sizeof(GLfloat*));
	GLfloat **colors_map = (GLfloat**)malloc(BIT_NUM * img_data.width * img_data.height * 3 * sizeof(GLfloat*));
	for (int i = 0; i < BIT_NUM; i++) {
		pixels_map[i] = (GLfloat*)malloc(2 * img_data.width * img_data.height * sizeof(GLfloat));
		colors_map[i] = (GLfloat*)malloc(img_data.width * img_data.height * 3 * sizeof(GLfloat));
	}

	int bit_index = 0;
	printf("Load location data into memory...\n");
	int pixel_index = 0;
	int color_index = 0;
	for (int n = 0; n < BIT_NUM; n++) {
		for (int i = 0; i < img_data.width; i++) {
			for (int j = 0; j < img_data.height; j++) {
				// pixels_map[n][pixel_index] = i;
				// pixels_map[n][pixel_index + 1] = j;
				pixels_map[n][pixel_index] = j;
				pixels_map[n][pixel_index + 1] = img_data.height - i;


				if(n == 0) {
					/*colors_map[n][color_index] = 0;
					colors_map[n][color_index + 1] = 0;
					colors_map[n][color_index + 2] = 0;*/
				    assign_value(colors_map, img_data.pixel_arr, n, color_index, i, j);
				}
				else if(n == 1) {
					/*colors_map[n][color_index] = 1;
					colors_map[n][color_index + 1] = 1;
					colors_map[n][color_index + 2] = 1;*/
				    assign_value(colors_map, img_data2.pixel_arr, n, color_index, i, j);
				}
				else if (n == 2) {
					/*colors_map[n][color_index] = 0.5;
					colors_map[n][color_index + 1] = 0.5;
					colors_map[n][color_index + 2] = 0.5;*/
					assign_value(colors_map, img_data.pixel_arr, n, color_index, i, j);
				}
				else if(n == 3) assign_value(colors_map, img_data2.pixel_arr, n, color_index, i, j);
				else if(n == 4) assign_value(colors_map, img_data.pixel_arr, n, color_index, i, j);
				else if(n == 5) assign_value(colors_map, img_data.pixel_arr, n, color_index, i, j);
				else if(n == 6) assign_value(colors_map, img_data2.pixel_arr, n, color_index, i, j);
				else if(n == 7) assign_value(colors_map, img_data2.pixel_arr, n, color_index, i, j);
				else if(n == 8) assign_value(colors_map, img_data.pixel_arr, n, color_index, i, j);
				else if(n == 9) assign_value(colors_map, img_data.pixel_arr, n, color_index, i, j);
				else if(n == 10) assign_value(colors_map, img_data2.pixel_arr, n, color_index, i, j);
				else if(n == 11) assign_value(colors_map, img_data2.pixel_arr, n, color_index, i, j);
				// {
				//     colors_map[n][color_index] = (float)pixel_arr1[i][j][2] / 255.0;
				//     colors_map[n][color_index + 1] = (float)pixel_arr1[i][j][1] / 255.0;
				//     colors_map[n][color_index + 2] = (float)pixel_arr1[i][j][0] / 255.0;
				// }
				pixel_index += 2;
				color_index += 3;
			}
		}
		pixel_index = 0;
		color_index = 0;
	}
	printf("Load done.\n");
	printf("Used memory: %fMB\n", (double)3 * 5 * img_data.width * img_data.height * sizeof(GLfloat) / 8 / 1000 / 1000);

	int pointNum = img_data.width * img_data.height;

	while (!glfwWindowShouldClose(window))
	{
		glClear(GL_COLOR_BUFFER_BIT);

		glEnableClientState(GL_VERTEX_ARRAY);
		glEnableClientState(GL_COLOR_ARRAY);

		glVertexPointer(2, GL_FLOAT, 0, pixels_map[bit_index]);
		glColorPointer(3, GL_FLOAT, 0, colors_map[bit_index]);
		glDrawArrays(GL_POINTS, 0, pointNum);

		glDisableClientState(GL_COLOR_ARRAY);
		glDisableClientState(GL_VERTEX_ARRAY);

		glfwSwapBuffers(window);
		glfwPollEvents();

		bit_index++;
		if (bit_index == BIT_NUM) bit_index = 0;
	}

	glfwTerminate();

	return 0;
}
