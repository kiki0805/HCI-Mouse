// #include <glad/glad.h>
#include <GL/glew.h>
#include <GL/glxew.h>
#include <GLFW/glfw3.h>
// #include "glxext.h"

#include <stdio.h>
#include <assert.h>
#include "utils.h"
#include <iostream>
// g++ one_value.cpp -Ibuild/include build/src/glad.c -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl

using namespace std;

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

    if (glxewIsSupported("GLX_MESA_swap_control")) {
        printf("OK, we can use GLX_MESA_swap_control\n");
    } else {
        printf("[WARNING] GLX_MESA_swap_control is NOT supported.\n");
    }

    glXSwapIntervalMESA(1);
    bool flag = true;
    // glXSwapIntervalSGI(1);
    // cout<< rtn <<endl;
    // if(rtn==GLX_BAD_CONTEXT || rtn == GLX_BAD_VALUE) return 0;

    // wglSwapIntervalEXT(1);
    float timeValue = glfwGetTime();
    float current = timeValue;
    while (!glfwWindowShouldClose(window)) {
        // if(begin->bit == '0') 
        //     glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        // else
        //     glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        // if (begin->next == NULL) begin = (struct bit_ele*) begin->first_bit;
        // else begin = begin->next;
        if(flag) 
            glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        else
            glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
        flag = !flag;

        current = glfwGetTime();
        if(current-timeValue > (float)1.0/60.0 + 0.001) {
            printf("timeout\n");
            printf("%f\n", current-timeValue);
        }
        timeValue = current;

        glClear(GL_COLOR_BUFFER_BIT);

        glfwSwapBuffers(window);
        glfwPollEvents();
        // Keep running
    }

    glfwTerminate();
    return 0;
}
