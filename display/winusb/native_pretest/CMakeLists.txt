add_definitions(-DNPNX_CLI_ONLY -DUNICODE)
add_executable(usbtest test.cpp)
target_link_libraries(usbtest hid SetupAPI CfgMgr32 Winusb)