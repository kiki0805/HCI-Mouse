#include <opencv4/opencv2/core/core.hpp>
#include <opencv4/opencv2/highgui/highgui.hpp>
#include <opencv4/opencv2/imgproc/imgproc.hpp>
#include "image_process.h"
#include <iostream>
#include <string>

using namespace cv;
using namespace std;
int main()
{
    Image4Render img_data = read_pixels_from_image("test-0.png");
    // imshow(img_data.raw_img);
    img_data.change_region(0,0,100,100, 50, true, false);
    return 0;
}
