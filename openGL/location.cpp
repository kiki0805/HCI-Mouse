// #include <glad/glad.h>
#ifdef _WIN32
    #include "pch.h"
#endif
#include <GL/glew.h>
#ifdef __linux__ 
    #include <GL/glxew.h>
#elif _WIN32
    #include <GL/wglew.h>
#else

#endif
#include <GLFW/glfw3.h>

#include <stdio.h>
#include <assert.h>
#include "utils.h"
#include <iostream>

using namespace std;

// g++ location.cpp -Ibuild/include build/src/glad.c -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl

struct bit_map* location_data;

#define BITS_NUM 72 // 18 * 4
#define SCREEN_WIDTH 1366
#define SCREEN_HEIGHT 768
#define WIDTH 640 // Display
#define HEIGHT 640 // Display
GLfloat pixels_map[BITS_NUM][WIDTH * HEIGHT * 2];
GLfloat colors_map[BITS_NUM][WIDTH * HEIGHT * 3];
int bit_index = 0;

int main( void )
{
    int init_ret = glfwInit();
    assert(init_ret == 1);
    
    GLFWwindow* window = glfwCreateWindow(WIDTH, HEIGHT, "My Title", NULL, NULL);
    if (!window) {
        printf("Window or OpenGL context creation failed\n");
    }
    glfwMakeContextCurrent(window);
    glViewport(0, 0, WIDTH, HEIGHT);
    glOrtho( 0, WIDTH, 0, HEIGHT, 0, 1 ); // essentially set coordinate system

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

    char file_path[] = "share_data_location";
    ::location_data = read_location_data(file_path);
	char c;
	printf("Load location data into memory...\n");
    int pixel_index = 0;
    int color_index = 0;
	for(int n = 0; n < BITS_NUM; n++) {
        for(int i = 0; i < WIDTH; i++) {
            for(int j = 0; j < HEIGHT; j++) {
                c = get_bit_by_pixel(i, j, ::location_data, WIDTH, HEIGHT);
                pixels_map[n][pixel_index] = i;
                pixels_map[n][pixel_index + 1] = j;
                if(c == '0') {
                    colors_map[n][color_index] = 255;
                    colors_map[n][color_index + 1] = 255;
                    colors_map[n][color_index + 2] = 255;
                }
                else {
                    colors_map[n][color_index] = 0;
                    colors_map[n][color_index + 1] = 0;
                    colors_map[n][color_index + 2] = 0;
                }
                pixel_index += 2;
                color_index += 3;
            }
        }
        pixel_index = 0;
        color_index = 0;
        move_next(::location_data);
    }
    free_location_data(::location_data);
	printf("Load done.\n");
	printf("Used memory: %fMB\n", (double)5*BITS_NUM*WIDTH*HEIGHT*sizeof(GLint)/8/1000/1000);

    int pointNum = WIDTH * HEIGHT;

    while ( !glfwWindowShouldClose( window ) )
    {
        glClear( GL_COLOR_BUFFER_BIT );

        glEnableClientState( GL_VERTEX_ARRAY );
        glEnableClientState( GL_COLOR_ARRAY );

        glVertexPointer( 2, GL_FLOAT, 0, pixels_map[bit_index] );
        glColorPointer( 3, GL_FLOAT, 0, colors_map[bit_index] );
        glDrawArrays( GL_POINTS, 0, pointNum );

        glDisableClientState( GL_COLOR_ARRAY );
        glDisableClientState( GL_VERTEX_ARRAY );
        
        glfwSwapBuffers( window );
        glfwPollEvents( );

        bit_index ++;
	    if(bit_index == BITS_NUM) bit_index = 0;
    }
    
    glfwTerminate( );
    
    return 0;
}
