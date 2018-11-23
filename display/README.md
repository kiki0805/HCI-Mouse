## Introduction

- 稍微漂亮的名字的是：基于鼠标光电传感器的新型人机交互，实际上就是用鼠标（receiver）采集灰度像素值，用屏幕（transmitter）发送信号的一个信道。



## Code Tree & Data Structure

- 主要分成transmitter和receiver两个部分来写
  - 根目录下大多是python文件，负责receiver部分，是一些信号处理的代码，现在暂时不会动它
  - transmitter主要在`/openGL`目录下
- 图像处理的功能代码我用openCV写了一些在`/OpenCV/image_process.h`里

- `/display`是新建的文件夹，原来的代码有点脏，我们分工新写的部分暂时都放在这里面吧，方便看



### Display

- `display.cpp`主要是openGL的代码框架，基本写好了（创建窗口、vsync同步、全屏显示），需要实现下`show_layer`函数
- `layer_utils.h` 里面定义了几个数据结构：
  - `BaseLayer` 就是显示画面的底图，之后需要做一个事件监听，更新底图（井字棋下一个子，模拟门把手旋转的frame sequences）
  - `DataBlock` 是一个像素点组成的区域，在一个block里面的所有像素点都apply一个固定的色彩偏移值
  - `DataLayerSlice` 是一个time interval/一帧图片内显示的数据图层，由多个`DataBlock`组成
  - `DataLayer` 由`DataLayerSlice`组成的时域序列（length==BITS_NUM），每帧数据图层都从`DataLayer`里面遍历提取出来

- 然后是几个功能函数：
  - `show_layer(BaseLayer, DataLayer)` 把底图和数据图层合并以后渲染出来
  - `convert_blocks2slice(DataBlock** blocks, int m, int n)` 将多个`DataBlock`转换为`DataLayerSlice`的函数
- `data_generator.h`定义了测试用的函数（used in TEST CASE）
  - `generate_block_data(int size_x=32, int size_y=32)` ，随机生成一个`DataBlock`二维数组



## Note

- Goals: 

  - 给定一组时域上的偏移值空间数组可以和底图融合显示，把`display.cpp`里面的BASE CASE和TEST CASE显示出来应该就差不多完成了
  - [TODO] 接受信号，更新底图，这个部分暂时还用不到，现在的代码里还没有涉及

- 我编译了一下可以运行了，但是还什么都没有显示，需要完善下代码

- 环境配置在ubuntu和win下有些不同，头文件可能需要改

- 现在主要的任务是把显示端的信号调制和编码固定下来，我先用老的代码测试着，等`/display`部分写完善了再把算法补充进来。


