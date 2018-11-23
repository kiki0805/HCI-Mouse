// #include <glad/glad.h>
// #include "pch.h"
#include <GL/glew.h>
#include <GL/glxew.h>
// #include <GL/wglew.h>
#include <GLFW/glfw3.h>
#include "image_process.h"

#include <stdio.h>
#include <assert.h>
#include "utils.h"
#include <iostream>

using namespace std;

// g++ image_test.cpp -o test -Ibuild/include build/src/glad.c -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl `pkg-config --cflags --libs opencv`

int main( void )
{
    Image4Render img_data = read_pixels_from_image("test-0.png");

    img_data.change_region(100, 100, 300, 300, -10, false, false);
    int pixel_arr[img_data.width][img_data.height][3];
    for(int i = 0; i < img_data.width; i++){
        for(int j = 0; j < img_data.height; j++){
            pixel_arr[i][j][0] = img_data.pixel_arr[i][j][0];
            pixel_arr[i][j][1] = img_data.pixel_arr[i][j][1];
            pixel_arr[i][j][2] = img_data.pixel_arr[i][j][2];
        }
    }
    img_data.change_region(100, 100, 300, 300, 20, false, false);
    
    int pixel_arr2[img_data.width][img_data.height][3];
    for(int i = 0; i < img_data.width; i++){
        for(int j = 0; j < img_data.height; j++){
            pixel_arr2[i][j][0] = img_data.pixel_arr[i][j][0];
            pixel_arr2[i][j][1] = img_data.pixel_arr[i][j][1];
            pixel_arr2[i][j][2] = img_data.pixel_arr[i][j][2];
        }
    }

    int init_ret = glfwInit();
    assert(init_ret == 1);
    
    GLFWwindow* window = glfwCreateWindow(img_data.width, img_data.height, "My Title", NULL, NULL);
    if (!window) {
        printf("Window or OpenGL context creation failed\n");
    }
    glfwMakeContextCurrent(window);
    glViewport(0, 0, img_data.width, img_data.height);
    glOrtho( 0, img_data.width, 0, img_data.height, 0, 1 ); // essentially set coordinate system

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
    
    GLfloat **pixels_map = (GLfloat**) malloc(2 * img_data.width * img_data.height * 2 * sizeof(GLfloat*));
    GLfloat **colors_map = (GLfloat**) malloc(2 * img_data.width * img_data.height * 3 * sizeof(GLfloat*));
    for(int i = 0; i < 2; i++) {
        pixels_map[i] = (GLfloat*)malloc(2 * img_data.width * img_data.height * sizeof(GLfloat));
        colors_map[i] = (GLfloat*)malloc(img_data.width * img_data.height * 3 * sizeof(GLfloat));
    }

    int bit_index = 0;
	printf("Load location data into memory...\n");
    int pixel_index = 0;
    int color_index = 0;
	for(int n = 0; n < 2; n++) {
        for(int i = 0; i < img_data.width; i++) {
            for(int j = 0; j < img_data.height; j++) {
                pixels_map[n][pixel_index] = i;
                pixels_map[n][pixel_index + 1] = j;
                // colors_map[n][color_index] = 0;
                // colors_map[n][color_index + 1] = 0;
                // colors_map[n][color_index + 2] = 0;

                if(n == 0) {
                    colors_map[n][color_index] = (float)pixel_arr[i][j][0] / 255.0;
                    colors_map[n][color_index + 1] = (float)pixel_arr[i][j][1] / 255.0;
                    colors_map[n][color_index + 2] = (float)pixel_arr[i][j][2] / 255.0;
                }
                else {
                    colors_map[n][color_index] = (float)pixel_arr2[i][j][0] / 255.0;
                    colors_map[n][color_index + 1] = (float)pixel_arr2[i][j][1] / 255.0;
                    colors_map[n][color_index + 2] = (float)pixel_arr2[i][j][2] / 255.0;
                }
                pixel_index += 2;
                color_index += 3;
            }
        }
        pixel_index = 0;
        color_index = 0;
    }
	printf("Load done.\n");
	printf("Used memory: %fMB\n", (double)5 * img_data.width * img_data.height * sizeof(GLfloat)/8/1000/1000);

    int pointNum = img_data.width * img_data.height;

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
	    if(bit_index == 2) bit_index = 0;
    }
    
    glfwTerminate( );
    
    return 0;
}
