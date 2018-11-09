#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include "utils.h"
using namespace std;

// g++ location.cpp -Ibuild/include build/src/glad.c -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl

struct bit_map* location_data;

#define BITS_NUM 72 // 18 * 3
#define SCREEN_WIDTH 1366
#define SCREEN_HEIGHT 768
#define WIDTH 640 // Display
#define HEIGHT 640 // Display
GLfloat pixels_map[BITS_NUM][WIDTH * HEIGHT * 2];
GLfloat colors_map[BITS_NUM][WIDTH * HEIGHT * 3];
int bit_index = 0;

int main( void )
{
    char file_path[] = "share_data_location";
    location_data = read_location_data(file_path);
	char c;
	printf("Load location data into memory...\n");
    int pixel_index = 0;
    int color_index = 0;
	for(int n = 0; n < BITS_NUM; n++) {
        for(int i = 0; i < WIDTH; i++) {
            for(int j = 0; j < HEIGHT; j++) {
                c = get_bit_by_pixel(i, j, location_data, WIDTH, HEIGHT);
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
        move_next(location_data);
    }
    free_location_data(location_data);
	printf("Load done.\n");
	printf("Used memory: %fMB\n", (double)5*BITS_NUM*WIDTH*HEIGHT*sizeof(GLint)/8/1000/1000);


    //////////////////////////////////////////////////////////////////////
    GLFWwindow *window;
    
    // Initialize the library
    if ( !glfwInit( ) )
    {
        return -1;
    }
    
    // Create a windowed mode window and its OpenGL context
    window = glfwCreateWindow( WIDTH, HEIGHT, "Display  Window", NULL, NULL );
    
    if ( !window )
    {
        glfwTerminate( );
        return -1;
    }
    
    // Make the window's context current
    glfwMakeContextCurrent( window );
    
    glViewport( 0.0f, 0.0f, WIDTH, HEIGHT ); // specifies the part of the window to which OpenGL 
    glOrtho( 0, WIDTH, 0, HEIGHT, 0, 1 ); // essentially set coordinate system

    int pointNum = WIDTH * HEIGHT;

    while ( !glfwWindowShouldClose( window ) )
    {
        // glClearColor(0.5f, 0.5f, 0.5f, 0.5f);
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
