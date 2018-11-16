// #include <glad/glad.h>
#include <GL/glew.h>
#ifdef __linux__ 
    #include <GL/glxew.h>
#elif _WIN32
    #include <GL/wglew.h>
    #include <pch.h>
#else

#endif
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
    
    GLFWwindow* window = glfwCreateWindow(800, 600, "My Title", NULL, NULL);
    if (!window) {
        printf("Window or OpenGL context creation failed\n");
    }
    glfwMakeContextCurrent(window);
    glViewport(0, 0, 800, 600);

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
    
    // bool flag = true;
    char file_path[] = "share_data";
    ::begin = read_swap_data(file_path);
    while (!glfwWindowShouldClose(window)) {
        if(::begin->bit == '0') 
            glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        else
            glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        if (::begin->next == NULL) ::begin = (struct bit_ele*) ::begin->first_bit;
        else ::begin = ::begin->next;
        // if(flag) 
        //     glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        // else
        //     glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        // flag = !flag;

        glClear(GL_COLOR_BUFFER_BIT);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwTerminate();
    return 0;
}
