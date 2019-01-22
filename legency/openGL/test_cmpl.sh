g++ image_test.cpp -o test -lGLEW -lglfw3 -lGL -lX11 -lXi -lXrandr -lXxf86vm -lXinerama -lXcursor -lrt -lm -pthread -ldl `pkg-config --cflags --libs opencv`
./test
