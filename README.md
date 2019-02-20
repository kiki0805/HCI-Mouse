#

- `python3 hci.py idx inpipe outpipe`
    - `idx` 用于向 `outpipe` 指明鼠标编号

---

- Frame on the monitor/screen/displayer to display: `frame_d`.
    - For video of 60Hz, the length of `frame_d` is 1/60 = 0.167s.
- Frame captured by the mouse: `frame_m`.
    - For mouse of 2400Hz fps, the length of `frame_m` is **around** 1/2400 = 0.004s.

## TODO

- ImageProcessing: for imperceptibility & decodability test
- display: final transmitter


---

- 动态加载图层 
    - https://blog.csdn.net/meccaendless/article/details/80238997
    - https://my.oschina.net/mickelfeng/blog/1929917
    - https://www.jianshu.com/p/b9eae892bcc0
    - https://blog.csdn.net/shenwanjiang111/article/details/54349675
- 二维数组和指针的操作
- 在文件中共享1024行
- Mouse轮廓法检测正误
- GRB颜色转强度差最大的色块显示
- 显示系统 / 游戏引擎（贴图） 修改显示内容

