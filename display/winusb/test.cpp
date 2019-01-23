/*
* Test suite program based of libusb-0.1-compat testlibusb
* Copyright (c) 2013 Nathan Hjelm <hjelmn@mac.ccom>
*
* This library is free software; you can redistribute it and/or
* modify it under the terms of the GNU Lesser General Public
* License as published by the Free Software Foundation; either
* version 2.1 of the License, or (at your option) any later version.
*
* This library is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
* Lesser General Public License for more details.
*
* You should have received a copy of the GNU Lesser General Public
* License along with this library; if not, write to the Free Software
* Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "libusb.h"
#include "libusb_utils.h"

#define NUM_MOUSE_MAXIMUM 10

const uint16_t target_vid = 0x04D9;
const uint16_t target_pid = 0xA070;

int
main(int argc, char *argv[])
{
  libusb_device **devs;
  ssize_t cnt;
  int num_mouse = 0;
  int r;

  r = libusb_init(NULL);
  if (r < 0)
    return r;

  cnt = libusb_get_device_list(NULL, &devs);
  if (cnt < 0)
    return (int)cnt;

  libusb_device *mouses[NUM_MOUSE_MAXIMUM];
  libusb_device_handle *mouses_handle[NUM_MOUSE_MAXIMUM];
  memset(mouses, 0, NUM_MOUSE_MAXIMUM * sizeof(libusb_device *));
  memset(mouses_handle, 0, NUM_MOUSE_MAXIMUM *sizeof(libusb_device_handle *));
  for (int i = 0; i < cnt; ++i)
  {
    print_device(devs[i], 0);
    libusb_device_descriptor desc;
    LIBUSB_SAFECALL(libusb_get_device_descriptor(devs[i],&desc));
    if (desc.idVendor == target_vid && desc.idProduct == target_pid) {
      printf("found\n");
      mouses[num_mouse++] = devs[i];
      if (num_mouse >= NUM_MOUSE_MAXIMUM) break;
    }
  }
  
  for(int i = 0; i < num_mouse; i++) {
    LIBUSB_SAFECALL(libusb_open(mouses[i], &mouses_handle[i]));

    unsigned char buf[4096];
    int cnt = libusb_get_descriptor(mouses_handle[i], LIBUSB_DT_DEVICE, 0, buf, 4096);
    if (cnt < 0) {
      printf("Device descriptor failed with %s\n", libusb_error_name(cnt));
    } else {
      for (int i = 0; i < cnt; i++){
        printf("%02x ", buf[i]);
      }
      printf("\n");
    }
    
    cnt = libusb_get_descriptor(mouses_handle[i], LIBUSB_DT_CONFIG, 0, buf, 4096);
    if (cnt < 0)
    {
      printf("CONFIG report failed with %s\n", libusb_error_name(cnt));
    }
    else
    {
      for (int i = 0; i < cnt; i++)
      {
        printf("%02x ", buf[i]);
      }
      printf("\n");
    }
  }
  libusb_free_device_list(devs, 1);

  for(int i = 0; i < num_mouse; i++) {
      unsigned char buf[1024];
      int cnt;
      printf("HID descriptor:");
      cnt = libusb_control_transfer(mouses_handle[i], 0x81, 0x06, 0x2100, 0, buf, 1024, 1000);
      if (cnt < 0) printf("%s\n", libusb_error_name(cnt));
      for (int i = 0; i < cnt; i++)
      {
        printf("%02x ", buf[i]);
      }
      printf("\n");
      printf("HID report descriptor:");
      cnt = libusb_control_transfer(mouses_handle[i], 0x81, 0x06, 0x2200, 0, buf, 1024, 1000);
      if (cnt < 0)
        printf("%s\n", libusb_error_name(cnt));
      for (int i = 0; i < cnt; i++)
      {
        printf("%02x ", buf[i]);
      }
      int nn = get_hid_record_size(buf, cnt, HID_REPORT_TYPE_INPUT);

      printf("\n");
      printf("send config:");
      cnt = libusb_control_transfer(mouses_handle[i], 0x00, 0x09, 0x0001, 0, buf, 0, 1000);
      if (cnt < 0)
        printf("%s\n", libusb_error_name(cnt));
      for (int i = 0; i < cnt; i++)
      {
        printf("%02x ", buf[i]);
      }
      printf("\n");
      // printf("send set_idle:");
      // cnt = libusb_control_transfer(mouses_handle[i], 0x21, 0x0a, 0x0010, 0, buf, 0, 1000);
      // if (cnt < 0){
      //   printf("%s\n", libusb_error_name(cnt));
      //   libusb_clear_halt(mouses_handle[i], 0);
      // }
      // for (int i = 0; i < cnt; i++)
      // {
      //   printf("%02x ", buf[i]);
      // }
      // printf("\n");
      // printf("send set_idle 2:");
      // cnt = libusb_control_transfer(mouses_handle[i], 0x21, 0x0a, 0x0000, 1, buf, 0, 1000);
      // if (cnt < 0){
      //   printf("%s\n", libusb_error_name(cnt));
      //   libusb_clear_halt(mouses_handle[i], 0);
      // }
      // for (int i = 0; i < cnt; i++)
      // {
      //   printf("%02x ", buf[i]);
      // }
      // printf("\n");
      // printf("send set_idle 3:");
      // cnt = libusb_control_transfer(mouses_handle[i], 0x21, 0x0a, 0x0000, 2, buf, 0, 1000);
      // if (cnt < 0){
      //   printf("%s\n", libusb_error_name(cnt));
      //   libusb_clear_halt(mouses_handle[i], 0);
      // }
      // for (int i = 0; i < cnt; i++)
      // {
      //   printf("%02x ", buf[i]);
      // }
      // printf("\n");
      // printf("send set_report:");
      // cnt = libusb_control_transfer(mouses_handle[i], 0x21, 0x09, 0x0000, 0, buf, 1, 1000);
      // if (cnt < 0){
      //   printf("%s\n", libusb_error_name(cnt));
      //   libusb_clear_halt(mouses_handle[i], 0);
      // }
      // for (int i = 0; i < cnt; i++)
      // {
      //   printf("%02x ", buf[i]);
      // }
      // printf("\n");
      // // for (int j = 0; j < 10000000; j++) {
      // //   int r = libusb_interrupt_transfer(mouses_handle[i], 0x02, buf, 1024, &cnt, 1000);
      // //   if (r < 0)
      // //     printf("%s\n", libusb_error_name(r));
      // //   for (int k = 0; k < cnt; k++)
      // //   {
      // //     printf("%02x ", buf[k]);
      // //   }
      // // }
      libusb_clear_halt(mouses_handle[i], 0);
      libusb_clear_halt(mouses_handle[i], 1);
      libusb_clear_halt(mouses_handle[i], 2);
      libusb_clear_halt(mouses_handle[i], 3);
      printf("nn%d\n",nn);
      printf("get report:");
      int config_num = 0;
      LIBUSB_SAFECALL(libusb_get_configuration(mouses_handle[i], &config_num));
      LIBUSB_SAFECALL(libusb_set_configuration(mouses_handle[i], 0x01));
      printf("%d\n", config_num);
      LIBUSB_SAFECALL(libusb_claim_interface(mouses_handle[i], 0x01));
      for (int j = 0; j < 1000; j++) {

        int ret = libusb_interrupt_transfer(mouses_handle[i], 0x82, buf, nn, &cnt, 1000);
        if (ret < 0 && ret != LIBUSB_ERROR_TIMEOUT) {
          printf("%s\n", libusb_error_name(ret));
        } else if (cnt != 0) {
          for (int k = 0; k < cnt; k++)
          {
            printf("%02x ", buf[k]);
          }
          printf("\n");
        }

        
      }
      libusb_release_interface(mouses_handle[i], 0x01);
  }

  for (int i=0; i<num_mouse; i++) {
    libusb_close(mouses_handle[i]);
  }
  libusb_exit(NULL);
  return 0;
}
