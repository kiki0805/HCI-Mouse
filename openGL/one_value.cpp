// #include <glad/glad.h>
#include <GL/glxew.h>
#include <GL/gl.h>
#include <GL/glx.h>
#include <GL/glu.h>
#include <GLFW/glfw3.h>
#include <stdio.h>
#include <assert.h>
#include "utils.h"
// g++ one_value.cpp -Ibuild/include build/src/glad.c -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl

// using namespace std;

int main() {
    int init_ret = glfwInit();

    assert(init_ret == 1);
    
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(800, 600, "My Title", NULL, NULL);
    if (!window) {
        printf("Window or OpenGL context creation failed\n");
    }
    glfwMakeContextCurrent(window);
    glViewport(0, 0, 800, 600);
    
    bool flag = true;
    glfwSwapInterval(1);

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
