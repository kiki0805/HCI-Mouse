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
struct bit_ele* begin;
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
    } else {
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
    } else {
        printf("[WARNING] WGL_EXT_swap_control is NOT supported.\n");
    }
    wglSwapIntervalEXT(1);
#else

#endif
    
    bool flag = true;
    // char file_path[] = "share_data";
    char file_path[] = "filtered_data";
    // ::begin = read_swap_data(file_path);
    vector<double> data = read_filtered_data(file_path);
    int cnt = 0;
    while (!glfwWindowShouldClose(window)) {
        // if (cnt == 25) cnt = 0;
        // double v = data[cnt];
        // glClearColor(v, v, v, 1.0f);
        // cnt ++;
        /////////////////////////////////////////////////////////
        // if(::begin->bit == '0') 
        //     glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        // else
        //     glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        // if (::begin->next == NULL) ::begin = (struct bit_ele*) ::begin->first_bit;
        // else ::begin = ::begin->next;
        ////////////////////////////////////////////////////////
        if(flag) 
            glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        else
            // glClearColor(0.5f, 0.5f, 0.5f, 1.0f);
            glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        flag = !flag;

        glClear(GL_COLOR_BUFFER_BIT);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    // free_bit_arr((struct bit_ele*)::begin->first_bit);

    glfwTerminate();
    return 0;
}
