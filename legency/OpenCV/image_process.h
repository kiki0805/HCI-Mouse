#include <opencv4/opencv2/core/core.hpp>
#include <opencv4/opencv2/highgui/highgui.hpp>
#include <opencv4/opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <string>

using namespace cv;
using namespace std;

class Image4Render {
  public:
    int width;
    int height;
    int*** pixel_arr;
    bool assigned;
    Mat raw_img;

    Image4Render(int w, int h) {
      width = w;
      height = h;
      pixel_arr = (int***) malloc(sizeof(int**) * w);
      for(int i = 0 ; i < w; i++) {
        *(pixel_arr + i) = (int**) malloc(h * sizeof(int*));
      }
      for(int i=0; i < w; i++) {
        for (int j=0; j < h; j++)
          *(*(pixel_arr + i) + j) = (int*) malloc(3 * sizeof(int*));
      }
      assigned = false;
    }

    ~Image4Render() {
      for(int i=0; i < width; i++) {
        for (int j=0; j < height; j++)
          free(pixel_arr[i][j]);
      }

      for(int i = 0 ; i < width; i++) {
        free(pixel_arr[i]);
      }

      free(pixel_arr);
    }

    void assign_pixel_value(Mat img) {
      Vec3b pixel;
      for(int i = 0; i < img.cols; i++) {
        for(int j = 0; j < img.rows; j++) {
          pixel = img.at<Vec3b>(i, j);
          // cout << (int)pixel.val[0] << " " << (int)pixel.val[1] << " " << (int)pixel.val[2] <<endl;
          // *(*(*(img_data.pixel_arr + i) + j)) = (int)pixel.val[0];
          // *(*(*(img_data.pixel_arr + i) + j) + 1) = (int)pixel.val[1];
          // *(*(*(img_data.pixel_arr + i) + j) + 2) = (int)pixel.val[2];
          pixel_arr[i][j][0] = (int)pixel.val[0];
          pixel_arr[i][j][1] = (int)pixel.val[1];
          pixel_arr[i][j][2] = (int)pixel.val[2];
        }
      }
      assigned = true;
      raw_img = img;
    }

    // bool check_change_valid(int i, int j, int value) {
    //   if(!(pixel_arr[i][j][0] + value <= 255 && pixel_arr[i][j][0] + value >= 0))
    //     return false; 
    //   if(!(pixel_arr[i][j][1] + value <= 255 && pixel_arr[i][j][1] + value >= 0))
    //     return false; 
    //   if(!(pixel_arr[i][j][2] + value <= 255 && pixel_arr[i][j][2] + value >= 0))
    //     return false; 
    // }

    Mat save_new_image(string file_name) {
      Mat mat(width, height, CV_8UC3);
      for (int i = 0; i < mat.rows; ++i) {
        for (int j = 0; j < mat.cols; ++j) {
            Vec3b& rgba = mat.at<Vec3b>(i, j);
            rgba[0] = pixel_arr[i][j][0];
            rgba[1] = pixel_arr[i][j][1];
            rgba[2] = pixel_arr[i][j][2];
        }
      }

      // vector<int> compression_params;
      // compression_params.push_back(CV_IMWRITE_PNG_COMPRESSION);
      // compression_params.push_back(9);

      imwrite(file_name, mat);
      return mat;
    }

    void change_region(int x_start, int y_start, int x_end, int y_end, int value, bool show, bool bordered) {
      assert(assigned);
      for(int i = x_start; i < x_end; i++) {
        for(int j = y_start; j < y_end; j++) {
          // assert(check_change_valid(i, j, value));
          if(bordered) {
            if(i == x_start || i == x_end - 1 || j == y_start || j == y_end - 1) {
              pixel_arr[i][j][0] = 255;
              pixel_arr[i][j][1] = 255;
              pixel_arr[i][j][2] = 255;
              continue;
            }
          }

          if(pixel_arr[i][j][0] + value < 0) pixel_arr[i][j][0] = 0;
          else if(pixel_arr[i][j][0] + value > 255) pixel_arr[i][j][0] = 255;
          else pixel_arr[i][j][0] += value;

          if(pixel_arr[i][j][1] + value < 0) pixel_arr[i][j][1] = 0;
          else if(pixel_arr[i][j][1] + value > 255) pixel_arr[i][j][1] = 255;
          else pixel_arr[i][j][1] += value;

          if(pixel_arr[i][j][2] + value < 0) pixel_arr[i][j][2] = 0;
          else if(pixel_arr[i][j][2] + value > 255) pixel_arr[i][j][2] = 255;
          else pixel_arr[i][j][2] += value;
        }
      }

      if(show) {
        imshow("New_image", save_new_image("New_image.png"));
        waitKey(0);
      }
    }
};



Image4Render read_pixels_from_image(string img_file) {
  Mat img = imread(img_file, CV_LOAD_IMAGE_COLOR);
#ifdef __linux__ 
  resize(img, img, Size(500, 500));
  Image4Render img_data = Image4Render(500, 500);
#elif _WIN32
  resize(img, img, Size(1920, 1080));
  Image4Render img_data = Image4Render(1920, 1080);
#else
#endif

  // imshow("New_image", img);
  img_data.assign_pixel_value(img);
  // waitKey(0);
  return img_data;
}


void add_complementary(Image4Render* raw_img) {

}

// int main()
// {
// Mat img;

// //   img = imread("C:/Users/hashan/Desktop/progtpoint.jpg", CV_LOAD_IMAGE_GRAYSCALE);
// img = imread("test.png", CV_LOAD_IMAGE_COLOR);
// cout<<"Width: "<<img.cols<<" Height: "<<img.rows<<endl;
// int width = img.cols;
// int height = img.rows;
// if (img.empty()) {
// cout << "Error" << endl;
// return -1;
// }

// namedWindow("New_image", CV_WINDOW_AUTOSIZE);

// imshow("New_image", img);

// // print number of channels in image
// cout << "image channels: " << img.channels() <<  endl;

// // check if image is a single channel
// if (img.channels() == 1) {
// Scalar pixel = img.at<uchar>(10, 10);
// cout << "Pixel value at 5,6 cordinate : " << pixel.val[0] << endl;
// }
// // check if image is a 3 channel

// else if (img.channels() == 3) {

// Vec3b pixel = img.at<Vec3b>(10, 10);
// int blue = pixel.val[0];
// int green = pixel.val[1];
// int red = pixel.val[2];
// }

// else {
// cout << "this is not a single channel image" << endl;
// }

// for(int i = 0; i < width; i++) {
// for(int j = 0; j < height; j++) {
// Vec3b pixel = img.at<Vec3b>(i, j);
// int blue = pixel.val[0];
// int green = pixel.val[1];
// int red = pixel.val[2];
// cout<<blue<<" "<<green<<" "<<red<<endl;

// }
// }
// waitKey(0);
// return 0;
// }