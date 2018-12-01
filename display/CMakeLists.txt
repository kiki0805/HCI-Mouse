cmake_minimum_required(VERSION 3.0)

project(HCI_Display)

set (CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set (CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

find_package(OpenCV REQUIRED)
message(STATUS opencv_inc " " ${OpenCV_INCLUDE_DIRS})

add_subdirectory(3rdParty/glew/build/cmake)

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

if (NOT WIN32 AND NOT APPLE) 
add_compile_options(-std=c++11)
endif()

#uncomment this to disable V_SYNC
add_definitions(-DNPNX_BENCHMARK) 

#add source file here
add_executable(
  display 

  main.cpp
  shader.cpp
  renderer.cpp
  layerobject.cpp
  imageUtils.cpp
)

target_link_libraries(display glfw glew ${HCI_EXTRA_LIBS} ${OpenCV_LIBS})
if (NOT MSVC)
  target_compile_options(display PRIVATE -Wl,-rpath=./)
endif()
