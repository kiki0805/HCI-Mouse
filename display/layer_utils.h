#ifndef _LAYER_UTILS_H__
#define _LAYER_UTILS_H__

// #include <opencv4/opencv2/core/core.hpp>
// #include <opencv4/opencv2/imgproc/imgproc.hpp>
// #include <opencv4/opencv2/highgui/highgui.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>
#include <string>
#include <assert.h>

using namespace cv;
using namespace std;

string FIXED_OFFSET = "FIXED_OFFSET";
string VARING_OFFSET = "VARING_OFFSET";

class BaseLayer {
    Mat img;
    
    public:
    BaseLayer(string file_name) {
        img = imread(file_name);
        resize(img, img, Size(1920, 1080));
    }
};

/*
    With fixed offset of RGB value, 
        show the area from (start_x, start_y) to (end_x, end_y) inner an instance of BaseLayer.
    Assert start_x < end_x, start_y < end_y.
*/
class DataBlock {
    int start_x;
    int start_y;
    int end_x;
    int end_y;
    int offset; // -255-255

    public:
    DataBlock(int x0, int y0, int x1, int y1, int val) {
        start_x = x0;
        start_y = y0;
        end_x = x1;
        end_y = y1;
        offset = val;
    }

    ~DataBlock() {

    }
};

class DataLayerSlice {
    int start_x;
    int start_y;
    int end_x;
    int end_y;
    int layer_size[2]; // number of blocks
    int** offset_matrix; // two-dimensional array of offset values, size: m*n

    public:
     DataLayerSlice(int x0, int y0, int x1, int y1, int m=32, int n=32) {
        start_x = x0;
        start_y = y0;
        end_x = x1;
        end_y = y1;
        layer_size[0] = m;
        layer_size[1] = n;
    }

    ~ DataLayerSlice() {

    }

    void assign_offset_mat(string mode, Mat img, int** off_arr) {
        if(mode == FIXED_OFFSET) {
            assert(off_arr != NULL);
            // copy off_arr to offset_matrix
            return;
        }
        else if(mode == VARING_OFFSET) {
            // remain blank
            // wait for an algorithm 
        }


    }
};

class DataLayer {
    int bit_num;
    DataLayerSlice* slide_arr;
    public:
    DataLayer(int bnum, DataLayerSlice* arr) {
        bit_num = bnum;
        // copy arr to slide_arr
    }
    ~DataLayer() {

    }
};

DataLayerSlice convert_blocks2slice(DataBlock** blocks, int m, int n) {
    /*
        Param: blocks is a m*n arr
        Return DataLayerSlice slice 
            with offset in blocks[i][j] assigned to slice.offset_matrix[i][j]
    */
   return DataLayerSlice(0,0,1,1);
}

void show_layer(BaseLayer, DataLayer) {

}



#endif