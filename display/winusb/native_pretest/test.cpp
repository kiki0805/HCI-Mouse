#include "../../common.h"

#include <windows.h>
#include <winusb.h>
#include <SetupAPI.h>
#include <Cfgmgr32.h>
#include <Devpkey.h>
#include <iostream>
#include <cstdio>
#include <cstdint>
#include <functional>
#include <chrono>
#include <thread>
#include <string>

using std::cout;
using std::endl;

#define NUM_MOUSE_MAXIMUM 10

#define HID_REPORT_TYPE_INPUT 0x01
#define HID_REPORT_TYPE_OUTPUT 0x02
#define HID_REPORT_TYPE_FEATURE 0x03
int get_hid_record_size(uint8_t *hid_report_descriptor, int size, int type)
{
  uint8_t i, j = 0;
  uint8_t offset;
  int record_size[3] = {0, 0, 0};
  int nb_bits = 0, nb_items = 0;
  bool found_record_marker;

  found_record_marker = false;
  for (i = hid_report_descriptor[0] + 1; i < size; i += offset)
  {
    offset = (hid_report_descriptor[i] & 0x03) + 1;
    if (offset == 4)
      offset = 5;
    switch (hid_report_descriptor[i] & 0xFC)
    {
    case 0x74: // bitsize
      nb_bits = hid_report_descriptor[i + 1];
      break;
    case 0x94: // count
      nb_items = 0;
      for (j = 1; j < offset; j++)
      {
        nb_items = ((uint32_t)hid_report_descriptor[i + j]) << (8 * (j - 1));
      }
      break;
    case 0x80: // input
      found_record_marker = true;
      j = 0;
      break;
    case 0x90: // output
      found_record_marker = true;
      j = 1;
      break;
    case 0xb0: // feature
      found_record_marker = true;
      j = 2;
      break;
    case 0xC0: // end of collection
      nb_items = 0;
      nb_bits = 0;
      break;
    default:
      continue;
    }
    if (found_record_marker)
    {
      found_record_marker = false;
      record_size[j] += nb_items * nb_bits;
    }
  }
  if ((type < HID_REPORT_TYPE_INPUT) || (type > HID_REPORT_TYPE_FEATURE))
  {
    return 0;
  }
  else
  {
    return (record_size[type - HID_REPORT_TYPE_INPUT] + 7) / 8;
  }
}

class HidDevice {
public:
  HidDevice() {
  }
  ~HidDevice() {
    if (pInterface_detail) {
      free(pInterface_detail);
    }
    if (h_winusb) {
      if (h_winusb != h_hidinterface && h_hidinterface) {
        WinUsb_Free(h_hidinterface);
      }
      WinUsb_Free(h_winusb);
    }
    if (h_file) {
      CloseHandle(h_file);
    }
  }

  inline WCHAR* GetDevicePath() {
    return &pInterface_detail->DevicePath[0];
  }

public:
  PSP_DEVICE_INTERFACE_DETAIL_DATA pInterface_detail = NULL;
  HANDLE h_file = NULL, h_winusb = NULL, h_hidinterface = NULL;
  int report_size = 0;

} mouses[NUM_MOUSE_MAXIMUM];

const UINT target_vid = 0x062a, target_pid = 0x8212;
int num_mouses = 0;

void printf_guid(GUID guid)
{
  printf("{%08lX-%04hX-%04hX-%02hhX%02hhX-%02hhX%02hhX%02hhX%02hhX%02hhX%02hhX}\n",
         guid.Data1, guid.Data2, guid.Data3,
         guid.Data4[0], guid.Data4[1], guid.Data4[2], guid.Data4[3],
         guid.Data4[4], guid.Data4[5], guid.Data4[6], guid.Data4[7]);
}

bool shouldClose = false;
std::string interResult;

void interruptTransferSender(HANDLE h_hid, int report_size) {
  interResult.clear();
  interResult.reserve(2000000);
  std::chrono::high_resolution_clock::time_point lastTime;
  int countInter = 0;
  while (!shouldClose) {
    UCHAR buf[200];
    DWORD length;
    NPNX_ASSERT_LOG( WinUsb_ReadPipe(h_hid, 0x82, buf, report_size, &length, NULL),
      GetLastError()
    );
    countInter += 1;
  }
  printf("%s %d\n", "countInter", countInter);
}

std::string controlResult;
void controlTransferSender(HANDLE h_winusb) {
  controlResult.clear();
  controlResult.reserve(2000000);
  int controlCount = 0;
  while (!shouldClose) {
    WINUSB_SETUP_PACKET controltransfer = {
      0x81, 0x06, 0x2100, 0, 4096
    };
    UCHAR buf[4096];
    DWORD length;
    NPNX_ASSERT_LOG( 
      WinUsb_ControlTransfer(h_winusb, controltransfer, buf, 4096, &length, NULL),
      GetLastError()
    );
    std::chrono::duration<double> wait_s(0.01);
    std::this_thread::sleep_for(wait_s);
    controlCount ++;
  }
  printf("%s %d\n", "countCon", controlCount);
}

int main()
{
  
  GUID winUSBSetupGuid = {0x88BAE032, 0x5A81, 0x49f0, 0xBC, 0x3D, 0xA4, 0xFF, 0x13, 0x82, 0x16, 0xD6};
  GUID winUSBInterfaceGuid = {0xA5DCBF10, 0x6530, 0x11D2, 0x90, 0x1F, 0x00, 0xC0, 0x4F, 0xB9, 0x51, 0xED};
  // GUID winUSBInterfaceGuid = {0x0A8FE9DC, 0x086F, 0x4BE7, 0xA6, 0x31, 0x4E, 0x44, 0x15, 0x86, 0x42, 0x2D};
  // printf_guid(winUSBSetupGuid);

  HDEVINFO h_info = SetupDiGetClassDevs(&winUSBInterfaceGuid, NULL, NULL, DIGCF_PRESENT | DIGCF_DEVICEINTERFACE);
  NPNX_ASSERT(h_info && h_info != INVALID_HANDLE_VALUE);

  int mouse_cnt = 0;
  SP_DEVINFO_DATA devinfo_data;
  SP_DEVICE_INTERFACE_DATA interface_data;
  interface_data.cbSize = sizeof(SP_DEVICE_INTERFACE_DATA);
  devinfo_data.cbSize = sizeof(SP_DEVINFO_DATA);
  int dev_count = 0;
  while (SetupDiEnumDeviceInterfaces(h_info, NULL, &winUSBInterfaceGuid, dev_count, &interface_data)) {
    DWORD length;
    bool suc = SetupDiGetDeviceInterfaceDetail(h_info, &interface_data, NULL, 0, &length, NULL);
    NPNX_ASSERT(!suc && GetLastError() == ERROR_INSUFFICIENT_BUFFER);
    

    PSP_DEVICE_INTERFACE_DETAIL_DATA pInterface_detail = (PSP_DEVICE_INTERFACE_DETAIL_DATA) malloc(length);
    pInterface_detail->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);
    NPNX_ASSERT_LOG(SetupDiGetDeviceInterfaceDetail(h_info, &interface_data, pInterface_detail, length, NULL, &devinfo_data), GetLastError());

    printf("%ls\n", pInterface_detail->DevicePath);
    
    // suc = SetupDiGetDevicePropertyKeys(h_info, &devinfo_data, NULL, 0, &length, 0);
    // NPNX_ASSERT(!suc && GetLastError() == ERROR_INSUFFICIENT_BUFFER);
    
    // DEVPROPKEY * keys = (DEVPROPKEY *) malloc(length * sizeof(DEVPROPKEY));

    // NPNX_ASSERT_LOG(SetupDiGetDevicePropertyKeys(h_info, &devinfo_data, keys, length * sizeof(DEVPROPKEY), NULL, 0), GetLastError()); 
    // for(int i=0; i<length; i++) {
    //   printf_guid(keys[i].fmtid);
    //   printf("%d\n", keys[i].pid);
    // }

    DEVPROPTYPE valuetype;
    suc = SetupDiGetDeviceProperty(h_info, &devinfo_data, &DEVPKEY_Device_HardwareIds, &valuetype, NULL, 0, &length, 0);
    NPNX_ASSERT(!suc && GetLastError() == ERROR_INSUFFICIENT_BUFFER);
    
    WCHAR *property_buffer = (WCHAR *) malloc(length);
    
    NPNX_ASSERT_LOG(SetupDiGetDeviceProperty(h_info, &devinfo_data, &DEVPKEY_Device_HardwareIds, &valuetype, (PBYTE)property_buffer, length, NULL, 0), GetLastError());
    // for(int i=0; i<length; i++) {
    //   printf(property_buffer != 0 ? "%lc" : "\\0", property_buffer[i]);
    // }

    if (!memcmp(property_buffer, TEXT("USB\\VID_04D9"), 12 * sizeof(WCHAR)) && !memcmp(&devinfo_data.ClassGuid, &winUSBSetupGuid, sizeof(GUID))){
      mouses[mouse_cnt++].pInterface_detail = pInterface_detail;
    } else {
      free(pInterface_detail);
    }
    free(property_buffer);
    dev_count++;
  }
  NPNX_ASSERT(GetLastError() == ERROR_NO_MORE_ITEMS);
  SetupDiDestroyDeviceInfoList(h_info);
  
  printf("\n");
  for (int i = 0; i < mouse_cnt; i++) {
    printf("found mouse: %ls\n", mouses[i].GetDevicePath());
    HANDLE h_file = CreateFile(mouses[i].GetDevicePath(),
                                GENERIC_WRITE | GENERIC_READ,
                                FILE_SHARE_WRITE | FILE_SHARE_READ,
                                NULL,
                                OPEN_EXISTING,
                                FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OVERLAPPED,
                                NULL);
    if (h_file == INVALID_HANDLE_VALUE) {
      NPNX_ASSERT_LOG(!"h_file_invalid", GetLastError());
    }
    mouses[i].h_file = h_file;
    HANDLE h_winusb;
    NPNX_ASSERT_LOG(WinUsb_Initialize(h_file, &h_winusb), GetLastError());
    mouses[i].h_winusb = h_winusb;

    WINUSB_SETUP_PACKET controltransfer = {
      0x81, 0x06, 0x2100, 0, 4096
    };

    UCHAR buf[4096];
    DWORD length;
    NPNX_ASSERT_LOG( 
      WinUsb_ControlTransfer(h_winusb, controltransfer, buf, 4096, &length, NULL),
      GetLastError()
    );
    
    for(int i = 0; i < length; i++){
      printf("%02hhx ", buf[i]);
    }
    printf("\n");

    controltransfer = {
      0x81, 0x06, 0x2200, 0, 4096
    };
    NPNX_ASSERT_LOG( 
      WinUsb_ControlTransfer(h_winusb, controltransfer, buf, 4096, &length, NULL),
      GetLastError()
    );
    for(int i = 0; i < length; i++){
      printf("%02hhx ", buf[i]);
    }
    printf("\n");

    HANDLE h_hidinterface;
    NPNX_ASSERT_LOG(WinUsb_GetAssociatedInterface(h_winusb, 0, &h_hidinterface),
      GetLastError()
    );
    mouses[i].h_hidinterface = h_hidinterface;

    ULONG report_size = get_hid_record_size(buf, length, HID_REPORT_TYPE_INPUT);
    mouses[i].report_size = report_size;
    printf("%d \n", report_size);
  }

  std::thread t1(interruptTransferSender, mouses[0].h_hidinterface, mouses[0].report_size);
  std::thread t2(controlTransferSender, mouses[0].h_winusb);

  std::chrono::duration<double> wait_s(5.0);
  std::this_thread::sleep_for(wait_s);

  shouldClose = true;
  t1.join();
  t2.join();
  std::cout << controlResult << interResult;
  while (true) {
    UCHAR buf[200];
    DWORD length;
    auto lastTime = std::chrono::high_resolution_clock::now();
    NPNX_ASSERT_LOG( WinUsb_ReadPipe(mouses[0].h_hidinterface, 0x82, buf, mouses[0].report_size, &length, NULL),
      GetLastError()
    );
    double timelapse = std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::high_resolution_clock::now() - lastTime).count();
    printf("%.7lf", timelapse / 1000000);
    for(int i = 0; i < length; i++){
      printf("%02hhx ", buf[i]);
    }
    printf("\n");
  }
  return 0;
}
