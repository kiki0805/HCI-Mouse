## Introduction

- 稍微漂亮的名字的是：基于鼠标光电传感器的新型人机交互，实际上就是用鼠标（receiver）采集灰度像素值，用屏幕（transmitter）发送信号的一个信道。

## Code Tree & Data Structure

- 主要分成transmitter和receiver两个部分来写
  - 根目录下大多是python文件，负责receiver部分，是一些信号处理的代码，现在暂时不会动它
  - transmitter主要在`/openGL`目录下
- 图像处理的功能代码我用openCV写了一些在`/OpenCV/image_process.h`里

- `/display`是新建的文件夹，原来的代码有点脏，我们分工新写的部分暂时都放在这里面吧，方便看

## Compile
首次编译使用 autoBuild_linux.sh 或者是 autoBuild_windows.sh 来做。windows的命令行环境用git bash就可以了。

生成build目录以后如果再改代码，可以在build目录里 "cmake --build ." 即可重新编译，这样是增量编译，比第一遍快很多。

linux上gdb可用，win上用vs打开build里的sln文件，选display项目按调试也可以正常调试，非常方便。

data里的文件(包括shader)是动态读取的，修改它们不用重新编译，重新运行display就行。

### Display

渲染图元OOP层次:
```
Renderer              
  map容器存储 - layerObject         
                继承- RectObject

Shader -独立，可以被任何以上图元使用

texture -独立，可以被任何以上图元使用

```
  
一个Renderer对应一个VAO，一个输出FBO。
并且有指针指向一个默认Shader，和一个默认Shader对应的默认Texture列表 （vector<GLuint> 容器）。

理论上一个FBO应该能对应多个VAO，一个VAO对应一个MESH，也就是FBO - VAO - LayerObject三层结构，但是我们只有2D图形，并且图元多顶点少，所以手动使用虚函数调用将layerObject的VBO和EBO拼成一个大VAO，然后与FBO合并为一层，即Renderer。每个layer记录自己的 VBO 和 EBO 在大VAO里的 offset。

因为可能有半透明的贴图存在，所以要按z-index从底往上依次draw, 这是使用map容器的原因。

Shader
  - 一个Shader Object对应一个 Shader Program, 由 vertex shader 和 fragment shader两部分组成。

makeTexture 系列函数
  - 读取图片，生成texture，然后返回texture的id。
  - [TECH]使用 unique_ptr 来管理堆内存Buffer。

在类的设计中，Renderer保证每次绘制前Bind VAO, Use Shader Program, 绑定默认texture。 LayerObject 则只保证调用 glDrawElements, 如果要使用自己的 shader 和 texture，则要先保存当前的，画完之后再切回来。我存了一个指向上级renderer的指针，所以可能保存都不用做了，直接切回默认。
  
话是这么说，我目前的shader设计是每个rect绑定各自GL_TEXTURE0, 所以只用一张贴图的话也不用做这个操作。

同时因为是按z-index顺序绘制，所以如果多个图元使用一组shader和texture，可以放在一起，在第一个之前和最后一个之后做读取和恢复。

这非常容易，因为我提供了beforeDraw和afterDraw函数指针接口, 参数是当前帧序号，可以传个lambda进去非常方便，Draw 会按照beforeDraw DrawGL afterDraw 来调用， DrawGL本身是虚函数。

目前可以对layer做的操作只有 visibleCallback, 来决定每一帧画不画。但是如果重载drawGL, 就可以定义每个layer每一帧的行为，并且可以继承出更多类型的图元。

main.cpp 中底图和上层图对应 renderer 和 postRenderer。renderer的结果会被画进texture, 供postRenderer使用。这样就可以实现根据画面颜色改变显示。postRenderer的最下层是利用传入shader 参数实现的全透明层，不然上一层的图像渲染不出来。

所以我们的调整算法要写进adjustShader中，对每个像素不同的参数可以用texture来传参，基本思想就是这样，代码写起来有点tricky，但是灵活度是没有问题的。

关于读入图片，因为使用cv::IMREAD_UNCHANGED，要求图片是RGBA或者RGB，8bit/channel，要支持其他图片类型就照葫芦画瓢加函数就行。在renderer中贴图被用作颜色，是支持alpha通道的，可以实现透明和半透明效果，这也是我为什么只设计了矩形图元，因为可以利用透明贴图显示不同的形状。


## Note

- Goals: 

  - [TODO] 接受信号，更新底图，这个部分暂时还用不到，现在的代码里还没有涉及
  - [TODO] 图元2D Transform支持(矩阵实现)，color 支持。
  - [TODO] 设计好看的UI。
  - [TODO] 游戏逻辑和ui绘制
