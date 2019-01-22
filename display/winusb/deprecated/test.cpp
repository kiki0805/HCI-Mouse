#include "../common.h"

#include <windows.h>
#include <winusb.h>
#include <SetupAPI.h>
#include <Cfgmgr32.h>
#include <iostream>
#include <cstdio>

using std::cout;
using std::endl;

#define NUM_MOUSE_MAXIMUM 10

class HidDevice {
public:
  HidDevice() {
    interface_data.cbSize = sizeof(SP_DEVICE_INTERFACE_DATA);
    devinfo_data.cbSize = sizeof(SP_DEVINFO_DATA);
  }
  ~HidDevice() {
    if (pInterface_detail) {
      free(pInterface_detail);
    }
    if (h_hid) {
      CloseHandle(h_hid);
    }
    if (h_winusb) {
      WinUsb_Free(h_winusb);
    }
  }

  inline WCHAR* GetDevicePath() {
    return &pInterface_detail->DevicePath[0];
  }

public:
  SP_DEVICE_INTERFACE_DATA interface_data;
  PSP_DEVICE_INTERFACE_DETAIL_DATA pInterface_detail = NULL;
  SP_DEVINFO_DATA devinfo_data;
  DEVINST parent_instance_id = 0;
  HANDLE h_hid = NULL, h_winusb = NULL;

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

int main()
{
  GUID hidGuid = {0xFFB701DC, 0x5725, 0x4E29, 0x92, 0xAD, 0x28, 0x15, 0x8C, 0xA1, 0x7C, 0x27};
  printf_guid(hidGuid);

  HDEVINFO h_info = SetupDiGetClassDevs(&hidGuid, NULL, NULL, DIGCF_PRESENT | DIGCF_DEVICEINTERFACE);
  NPNX_ASSERT(h_info && h_info != INVALID_HANDLE_VALUE);

  DWORD idx = 0;
  HidDevice dummyDevice;
  while (num_mouses < NUM_MOUSE_MAXIMUM && SetupDiEnumDeviceInterfaces(h_info, NULL, &hidGuid, idx, &dummyDevice.interface_data)) {
    DWORD requiredSize = 0;
    BOOL br = SetupDiGetDeviceInterfaceDetail(
      h_info, 
      &dummyDevice.interface_data,
      NULL,
      0,
      &requiredSize,
      NULL
    );

    dummyDevice.pInterface_detail = (PSP_DEVICE_INTERFACE_DETAIL_DATA)malloc(requiredSize);
    dummyDevice.pInterface_detail->cbSize = sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA);
    
    br = SetupDiGetDeviceInterfaceDetail(
      h_info,
      &dummyDevice.interface_data,
      dummyDevice.pInterface_detail,
      requiredSize,
      NULL,
      &dummyDevice.devinfo_data
    );
    NPNX_ASSERT_LOG(br, GetLastError());

    NPNX_ASSERT(CR_SUCCESS == CM_Get_Parent(&dummyDevice.parent_instance_id, dummyDevice.devinfo_data.DevInst, 0));
    printf("%ls\n", &dummyDevice.pInterface_detail->DevicePath[0]);
    printf("%d\n", dummyDevice.parent_instance_id);
    
    if (1) {
      bool foundSameParent = false;
      for (int i=0; i<num_mouses; i++){
        if (mouses[i].parent_instance_id == dummyDevice.parent_instance_id) {
          foundSameParent = true;
          break;
        }
      }
      if (!foundSameParent){
        mouses[num_mouses] = dummyDevice;
        dummyDevice.pInterface_detail = NULL;
        num_mouses++;
      }
    }

    idx++;
  }
  NPNX_LOG(num_mouses);
  for(int i=0; i<num_mouses; i++) {
    printf("%ls\n", mouses[i].GetDevicePath());
    HANDLE h_hid = CreateFile(
        mouses[i].GetDevicePath(),
        GENERIC_READ | GENERIC_WRITE,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OVERLAPPED,
        0);
    NPNX_ASSERT(h_hid && h_hid != INVALID_HANDLE_VALUE);
    mouses[i].h_hid = h_hid;

    HANDLE h_winusb = INVALID_HANDLE_VALUE;
    NPNX_ASSERT_LOG(WinUsb_Initialize(h_hid, &h_winusb), GetLastError());
    NPNX_ASSERT(h_winusb && h_winusb != INVALID_HANDLE_VALUE);
    mouses[i].h_winusb = h_winusb;

    

    // WINUSB_SETUP_PACKET costumCommand = {
    //   0x80, 0x06, 0x0001, 0x0000, 0x1200
    // };
    // UCHAR * buffer = (UCHAR *) calloc(1024, 1);
    // ULONG transferredLength = 0;
    // BOOL HR = WinUsb_ControlTransfer(
    //   h_winusb,
    //   costumCommand,
    //   buffer,
    //   1024,
    //   &transferredLength,
    //   NULL
    // );
    // NPNX_ASSERT_LOG(HR, GetLastError());
    // printf("%d\n", transferredLength);
    // printf("%08x %08x\n", ((UINT *)buffer)[0], ((UINT *)buffer)[1]);
    // free(buffer);
  } 
  


  SetupDiDestroyDeviceInfoList(h_info);

  return 0;
}
