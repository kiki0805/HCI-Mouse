FLAGS=`pkg-config --cflags --libs libdrm`
FLAGS+=-Wall -O0 -g
FLAGS+=-D_FILE_OFFSET_BITS=64

all:
	gcc -o modeset-vsync modeset-vsync.c -lm $(FLAGS)
	gcc -o location location-modeset-vsync.c -lm $(FLAGS)
