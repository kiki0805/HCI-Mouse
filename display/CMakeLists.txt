cmake_minimum_required(VERSION 3.0)

project(HCI_Display)

set (CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set (CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

set(MOUSECORE_NATIVE ON CACHE BOOL "USE WINUSB BACKEND" FORCE)

#set this to on to test winusb overlapped io, set to off when doing the demo for best performance.
set(MOUSECORE_NATIVE_ASYNC OFF CACHE BOOL "USB WINUSB WITH OVERLAPPED IO" FORCE)

if(MOUSECORE_NATIVE)
  add_definitions(-DUSE_MOUSECORE_NATIVE)
endif()

if(MOUSECORE_NATIVE_ASYNC)
  add_definitions(-DUSE_MOUSECORE_NATIVE_ASYNC)
endif()

find_package(OpenCV REQUIRED)
message(STATUS opencv_inc " " ${OpenCV_INCLUDE_DIRS})

set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL " " FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL " " FORCE)
set(GLFW_BUILD_DOCS OFF CACHE BOOL " " FORCE)
set(GLFW_BUILD_INSTALL OFF CACHE BOOL " " FORCE)
set(GLFW_INSTALL OFF CACHE BOOL " " FORCE)
set(GLFW_USE_CHDIR OFF CACHE BOOL " " FORCE)
set(BUILD_SHARED_LIBS ON CACHE BOOL " " FORCE)
add_subdirectory(3rdParty/glfw)

include_directories(3rdParty/glew/include)
include_directories(3rdParty/glfw/include)
include_directories(${OpenCV_INCLUDE_DIRS})

# Required core libraries on various platforms
if (WIN32)
  list(APPEND HCI_EXTRA_LIBS opengl32)
elseif (APPLE)
  find_library(cocoa_library Cocoa)
  find_library(opengl_library OpenGL)
  find_library(corevideo_library CoreVideo)
  find_library(iokit_library IOKit)
  list(APPEND HCI_EXTRA_LIBS ${cocoa_library} ${opengl_library} ${corevideo_library} ${iokit_library})
elseif(CMAKE_SYSTEM MATCHES "Linux" OR CMAKE_SYSTEM_NAME MATCHES "BSD")
  list(APPEND HCI_EXTRA_LIBS GL Xxf86vm Xrandr Xinerama Xcursor Xi X11 pthread )
  if (NOT CMAKE_SYSTEM_NAME MATCHES "OpenBSD")
    list(APPEND HCI_EXTRA_LIBS rt)
  endif()
  if(CMAKE_SYSTEM MATCHES "Linux")
    list(APPEND HCI_EXTRA_LIBS dl)
  endif()
endif()

add_definitions(-DNPNX_DATA_PATH="${CMAKE_CURRENT_SOURCE_DIR}/data")
add_definitions(-DNPNX_PY_PATH="${CMAKE_CURRENT_SOURCE_DIR}/../py_dev")
add_definitions(-DNPNX_PY_EXECUTABLE="hci.py")
add_definitions(-DUNICODE)

if (NOT WIN32 AND NOT APPLE) 
add_compile_options(-std=c++11)
endif()

add_subdirectory(winusb)
include_directories(${NPNXWINUSB_INC})
link_directories(${NPNXWINUSB_LIBPTH})

# add_subdirectory(3rdParty/ffmpeg)
# include_directories(${FFMPEG_INCLUDE_DIRS})
# link_directories(${FFMPEG_LIB_DIRS})
# link_libraries(${FFMPEG_LIBS})

set(GLEW_ARC ${CMAKE_CURRENT_SOURCE_DIR}/3rdParty/glew/lib/Release/x64/glew32s.lib)
add_definitions(-DGLEW_STATIC)

ADD_LIBRARY(glew STATIC IMPORTED)
set_target_properties(glew PROPERTIES
    IMPORTED_LOCATION ${GLEW_ARC})

link_libraries(${NPNXWINUSB_LIB} glfw glew ${HCI_EXTRA_LIBS} ${OpenCV_LIBS})

# benchmark option
# when use cmake build for msvc, debug and release chosen at the build time.
# which means should use cmake --build . --config Release
# add_definitions(-DNPNX_BENCHMARK) 
add_compile_options(-O2 -DNDEBUG)

#add source file here
add_executable(
  display 

  main.cpp
  shader.cpp
  renderer.cpp
  layerobject.cpp
  imageUtils.cpp
  videolayer.cpp
)

add_executable(
  chess

  chessdemo.cpp
  shader.cpp
  renderer.cpp
  layerobject.cpp
  imageUtils.cpp
  simpleChess.cpp
)

add_executable(
  drag

  dragdemo.cpp
  dragrectlayer.cpp
  shader.cpp
  renderer.cpp
  layerobject.cpp
  imageUtils.cpp
)

add_library(
  HCI_display

  OBJECT

  hcicontroller.cpp
  multimouse.cpp
  dragrectlayer.cpp
  curvelayer.cpp
  shader.cpp
  renderer.cpp
  layerobject.cpp
  imageUtils.cpp
  videolayer.cpp
)

add_executable(
  winusbdemo

  winusbdemo.cpp
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  test_Pointer

  test_Pointer.cpp
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  test_Ruler

  test_Ruler.cpp
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  test_HCIPointer

  test_HCIPointer.cpp
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  test_Slider

  test_Slider.cpp
  curvedata.cpp 
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  test_HCISlider

  test_HCISlider.cpp
  curvedata.cpp
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  test_Simple

  test_Simple.cpp
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  test_SimpleBG

  test_SimpleBG.cpp
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  demo_go

  demo_go.cpp
  $<TARGET_OBJECTS:HCI_display>
)

add_executable(
  demo_whac

  demo_whac.cpp
  $<TARGET_OBJECTS:HCI_display>
)
