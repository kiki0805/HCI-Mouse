// #include <glad/glad.h> 
//////////////////// WINDOWS
// #include "pch.h"
// #include <GL/glew.h>
// #include <GL/wglew.h>
// #define OS_STRING "Windows"

//////////////////UBUNTU
#include <GL/glew.h>
#include <GL/glxew.h>
#define OS_STRING "Ubuntu"

//////////////////////////////

#include <GLFW/glfw3.h>

#include <stdio.h>
#include <iostream>
#include "utils.h"
#include "layer_utils.h"
// g++ display.cpp -o display-lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm  -ldl

using namespace std;

int main() {
    int init_ret = glfwInit();
    assert(init_ret == 1);

    int monitorCount;
    GLFWmonitor** pMonitor = glfwGetMonitors(&monitorCount);

    int holographic_screen = -1;
    for(int i=0; i<monitorCount; i++){
        int screen_x, screen_y;
        const GLFWvidmode * mode = glfwGetVideoMode(pMonitor[i]);
        screen_x = mode->width;
        screen_y = mode->height;
        std::cout << "Screen size is X = " << screen_x << ", Y = " << screen_y << std::endl;
        if(screen_x==1920 && screen_y==1080){
            holographic_screen = i;
        }
    }
    std::cout << holographic_screen << std::endl;

    GLFWwindow* window;
    if (OS_STRING == "Ubuntu")
        window = glfwCreateWindow(800, 600, "My Title", NULL, NULL);
    else
        window = glfwCreateWindow(1920, 1080, "Holographic projection", pMonitor[holographic_screen], NULL);
    if (!window) {
        printf("Window or OpenGL context creation failed\n");
    }
    glfwMakeContextCurrent(window);
    if (OS_STRING == "Ubuntu")
        glViewport(0, 0, 800, 600);
        // glViewport(0, 0, 1366, 768);
    else
        glViewport(0, 0, 1920, 1080);

    GLenum err = glewInit();
    assert(GLEW_OK == err);
    fprintf(stdout, "Status: Using GLEW %s\n", glewGetString(GLEW_VERSION));

#ifdef __linux__ 
    if (glxewIsSupported("GLX_MESA_swap_control")) {
        printf("OK, we can use GLX_MESA_swap_control\n");
    } else {
        printf("[WARNING] GLX_MESA_swap_control is NOT supported.\n");
    }
    glXSwapIntervalMESA(1);
    printf("Swap interval: %d\n", glXGetSwapIntervalMESA());

#elif _WIN32
    if (wglewIsSupported("WGL_EXT_swap_control")) {
        printf("OK, we can use WGL_EXT_swap_control\n");
    } else {
        printf("[WARNING] WGL_EXT_swap_control is NOT supported.\n");
    }
    wglSwapIntervalEXT(1);
#else

#endif

    BaseLayer base = BaseLayer("test.png");
    DataBlock data0 = DataBlock(0, 0, 300, 300, -10);
    DataBlock data1 = DataBlock(0, 0, 300, 300, 10);

    bool flag = false;
    while (!glfwWindowShouldClose(window)) {
        // glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        // glClear(GL_COLOR_BUFFER_BIT);

        if(flag)
            show_layers(base, data0);
        else
            show_layers(base, data1);
        flag = !flag;

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwTerminate();
    return 0;
}
