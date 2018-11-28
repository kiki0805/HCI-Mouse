#ifdef _WIN32
// #include "pch.h"
#include <GL/glew.h>
#include <GL/wglew.h>
#define OS_STRING "Windows"
#endif

#ifdef __linux__
//////////////////// UBUNTU
#include <GL/glew.h>
#include <GL/glxew.h>
#define OS_STRING "Ubuntu"
#endif
//////////////////////////////

#include <GLFW/glfw3.h>

#include <stdio.h>
#include <cassert>
#include <iostream>
// #include "utils.h"
// #include "layer_utils.h"
// #include "data_generator.h"
// g++ display.cpp -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl `pkg-config --cflags --libs opencv`

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

    // ======================================================
    // =================== BASE CASE ========================
    // ======================================================

    BaseLayer base = BaseLayer("test.png");
    DataBlock data0 = DataBlock(0, 0, 300, 300, -10);
    DataBlock data1 = DataBlock(0, 0, 300, 300, 10);
    DataBlock** blocks0 = (DataBlock**) malloc(sizeof(DataBlock*));
    blocks0[0] = (DataBlock*) malloc(sizeof(DataBlock));
    DataBlock** blocks1 = (DataBlock**) malloc(sizeof(DataBlock*));
    blocks1[0] = (DataBlock*) malloc(sizeof(DataBlock));
    blocks0[0][0] = data0;
    blocks1[0][0] = data1;
    DataLayerSlice data_slice0 = convert_blocks2slice(blocks0, 1, 1);
    DataLayerSlice data_slice1 = convert_blocks2slice(blocks1, 1, 1);
    // DataLayerSlice data_slice0 = DataLayerSlice(0, 0, 300, 300, 1, 1);
    // DataLayerSlice data_slice1 = DataLayerSlice(0, 0, 300, 300, 1, 1);
    DataLayerSlice* slices = (DataLayerSlice*) malloc(sizeof(DataLayerSlice) * 2);
    slices[0] = data_slice0;
    slices[1] = data_slice1;
    DataLayer data_layer = DataLayer(2, slices);


    // ======================================================
    // =================== TEST CASE ========================
    // ======================================================

    // DataLayerSlice slice0 = convert_blocks2slice(generate_block_data(), 32, 32);
    // DataLayerSlice slice1 = convert_blocks2slice(generate_block_data(), 32, 32);
    // DataLayerSlice* slices = (DataLayerSlice*) malloc(sizeof(DataLayerSlice) * 2);
    // slices[0] = data_slice0;
    // slices[1] = data_slice1;
    // DataLayer data_layer = DataLayer(2, slices);

    while (!glfwWindowShouldClose(window)) {
        // glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        // glClear(GL_COLOR_BUFFER_BIT);

        show_layer(base, data_layer);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwTerminate();
    return 0;
}
