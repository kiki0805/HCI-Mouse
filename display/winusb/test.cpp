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

#if defined(_MSC_VER) && (_MSC_VER < 1900)
#define snprintf _snprintf
#endif

    int verbose = 0;

static void print_endpoint_comp(const struct libusb_ss_endpoint_companion_descriptor *ep_comp)
{
  printf("      USB 3.0 Endpoint Companion:\n");
  printf("        bMaxBurst:        %d\n", ep_comp->bMaxBurst);
  printf("        bmAttributes:     0x%02x\n", ep_comp->bmAttributes);
  printf("        wBytesPerInterval: %d\n", ep_comp->wBytesPerInterval);
}

static void print_endpoint(const struct libusb_endpoint_descriptor *endpoint)
{
  int i, ret;

  printf("      Endpoint:\n");
  printf("        bEndpointAddress: %02xh\n", endpoint->bEndpointAddress);
  printf("        bmAttributes:     %02xh\n", endpoint->bmAttributes);
  printf("        wMaxPacketSize:   %d\n", endpoint->wMaxPacketSize);
  printf("        bInterval:        %d\n", endpoint->bInterval);
  printf("        bRefresh:         %d\n", endpoint->bRefresh);
  printf("        bSynchAddress:    %d\n", endpoint->bSynchAddress);

  for (i = 0; i < endpoint->extra_length;)
  {
    if (LIBUSB_DT_SS_ENDPOINT_COMPANION == endpoint->extra[i + 1])
    {
      struct libusb_ss_endpoint_companion_descriptor *ep_comp;

      ret = libusb_get_ss_endpoint_companion_descriptor(NULL, endpoint, &ep_comp);
      if (LIBUSB_SUCCESS != ret)
      {
        continue;
      }

      print_endpoint_comp(ep_comp);

      libusb_free_ss_endpoint_companion_descriptor(ep_comp);
    }

    i += endpoint->extra[i];
  }
}

static void print_altsetting(const struct libusb_interface_descriptor *interface)
{
  uint8_t i;

  printf("    Interface:\n");
  printf("      bInterfaceNumber:   %d\n", interface->bInterfaceNumber);
  printf("      bAlternateSetting:  %d\n", interface->bAlternateSetting);
  printf("      bNumEndpoints:      %d\n", interface->bNumEndpoints);
  printf("      bInterfaceClass:    %d\n", interface->bInterfaceClass);
  printf("      bInterfaceSubClass: %d\n", interface->bInterfaceSubClass);
  printf("      bInterfaceProtocol: %d\n", interface->bInterfaceProtocol);
  printf("      iInterface:         %d\n", interface->iInterface);

  for (i = 0; i < interface->bNumEndpoints; i++)
    print_endpoint(&interface->endpoint[i]);
}

static void print_2_0_ext_cap(struct libusb_usb_2_0_extension_descriptor *usb_2_0_ext_cap)
{
  printf("    USB 2.0 Extension Capabilities:\n");
  printf("      bDevCapabilityType: %d\n", usb_2_0_ext_cap->bDevCapabilityType);
  printf("      bmAttributes:       0x%x\n", usb_2_0_ext_cap->bmAttributes);
}

static void print_ss_usb_cap(struct libusb_ss_usb_device_capability_descriptor *ss_usb_cap)
{
  printf("    USB 3.0 Capabilities:\n");
  printf("      bDevCapabilityType: %d\n", ss_usb_cap->bDevCapabilityType);
  printf("      bmAttributes:       0x%x\n", ss_usb_cap->bmAttributes);
  printf("      wSpeedSupported:    0x%x\n", ss_usb_cap->wSpeedSupported);
  printf("      bFunctionalitySupport: %d\n", ss_usb_cap->bFunctionalitySupport);
  printf("      bU1devExitLat:      %d\n", ss_usb_cap->bU1DevExitLat);
  printf("      bU2devExitLat:      %d\n", ss_usb_cap->bU2DevExitLat);
}

static void print_bos(libusb_device_handle *handle)
{
  struct libusb_bos_descriptor *bos;
  int ret;

  ret = libusb_get_bos_descriptor(handle, &bos);
  if (0 > ret)
  {
    return;
  }

  printf("  Binary Object Store (BOS):\n");
  printf("    wTotalLength:       %d\n", bos->wTotalLength);
  printf("    bNumDeviceCaps:     %d\n", bos->bNumDeviceCaps);

  if (bos->dev_capability[0]->bDevCapabilityType == LIBUSB_BT_USB_2_0_EXTENSION)
  {

    struct libusb_usb_2_0_extension_descriptor *usb_2_0_extension;
    ret = libusb_get_usb_2_0_extension_descriptor(NULL, bos->dev_capability[0], &usb_2_0_extension);
    if (0 > ret)
    {
      return;
    }

    print_2_0_ext_cap(usb_2_0_extension);
    libusb_free_usb_2_0_extension_descriptor(usb_2_0_extension);
  }

  if (bos->dev_capability[0]->bDevCapabilityType == LIBUSB_BT_SS_USB_DEVICE_CAPABILITY)
  {

    struct libusb_ss_usb_device_capability_descriptor *dev_cap;
    ret = libusb_get_ss_usb_device_capability_descriptor(NULL, bos->dev_capability[0], &dev_cap);
    if (0 > ret)
    {
      return;
    }

    print_ss_usb_cap(dev_cap);
    libusb_free_ss_usb_device_capability_descriptor(dev_cap);
  }

  libusb_free_bos_descriptor(bos);
}

static void print_interface(const struct libusb_interface *interface)
{
  int i;

  for (i = 0; i < interface->num_altsetting; i++)
    print_altsetting(&interface->altsetting[i]);
}

static void print_configuration(struct libusb_config_descriptor *config)
{
  uint8_t i;

  printf("  Configuration:\n");
  printf("    wTotalLength:         %d\n", config->wTotalLength);
  printf("    bNumInterfaces:       %d\n", config->bNumInterfaces);
  printf("    bConfigurationValue:  %d\n", config->bConfigurationValue);
  printf("    iConfiguration:       %d\n", config->iConfiguration);
  printf("    bmAttributes:         %02xh\n", config->bmAttributes);
  printf("    MaxPower:             %d\n", config->MaxPower);

  for (i = 0; i < config->bNumInterfaces; i++)
    print_interface(&config->interface[i]);
}

static int print_device(libusb_device *dev, int level)
{
  struct libusb_device_descriptor desc;
  libusb_device_handle *handle = NULL;
  char description[256];
  char string[256];
  int ret;
  uint8_t i;

  ret = libusb_get_device_descriptor(dev, &desc);
  if (ret < 0)
  {
    fprintf(stderr, "failed to get device descriptor");
    return -1;
  }

  ret = libusb_open(dev, &handle);
  if (LIBUSB_SUCCESS == ret)
  {
    if (desc.iManufacturer)
    {
      ret = libusb_get_string_descriptor_ascii(handle, desc.iManufacturer, (unsigned char *)string, sizeof(string));
      if (ret > 0)
        snprintf(description, sizeof(description), "%s - ", string);
      else
        snprintf(description, sizeof(description), "%04X - ",
                 desc.idVendor);
    }
    else
      snprintf(description, sizeof(description), "%04X - ",
               desc.idVendor);

    if (desc.iProduct)
    {
      ret = libusb_get_string_descriptor_ascii(handle, desc.iProduct, (unsigned char *)string, sizeof(string));
      if (ret > 0)
        snprintf(description + strlen(description), sizeof(description) - strlen(description), "%s", string);
      else
        snprintf(description + strlen(description), sizeof(description) - strlen(description), "%04X", desc.idProduct);
    }
    else
      snprintf(description + strlen(description), sizeof(description) - strlen(description), "%04X", desc.idProduct);
  }
  else
  {
    snprintf(description, sizeof(description), "%04X - %04X",
             desc.idVendor, desc.idProduct);
  }

  printf("%.*sDev (bus %d, device %d): %s\n", level * 2, "                    ",
         libusb_get_bus_number(dev), libusb_get_device_address(dev), description);

  if (handle && verbose)
  {
    if (desc.iSerialNumber)
    {
      ret = libusb_get_string_descriptor_ascii(handle, desc.iSerialNumber, (unsigned char *)string, sizeof(string));
      if (ret > 0)
        printf("%.*s  - Serial Number: %s\n", level * 2,
               "                    ", string);
    }
  }

  if (verbose)
  {
    for (i = 0; i < desc.bNumConfigurations; i++)
    {
      struct libusb_config_descriptor *config;
      ret = libusb_get_config_descriptor(dev, i, &config);
      if (LIBUSB_SUCCESS != ret)
      {
        printf("  Couldn't retrieve descriptors\n");
        continue;
      }

      print_configuration(config);

      libusb_free_config_descriptor(config);
    }

    if (handle && desc.bcdUSB >= 0x0201)
    {
      print_bos(handle);
    }
  }

  if (handle)
    libusb_close(handle);

  return 0;
}

#define LIBUSB_SAFECALL(A) do {int r = (A); if (r != 0) {printf("%s failed: %s\n", #A, libusb_error_name(r));exit(-1);}} while (0)

#define NUM_MOUSE_MAXIMUM 10

const uint16_t target_vid = 0x04D9;
const uint16_t target_pid = 0xA070;

#define HID_REPORT_TYPE_INPUT 0x01
#define HID_REPORT_TYPE_OUTPUT 0x02
#define HID_REPORT_TYPE_FEATURE 0x03

// HID
static int get_hid_record_size(uint8_t *hid_report_descriptor, int size, int type)
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
      printf("HID report failed with %s\n", libusb_error_name(cnt));
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
        cnt = libusb_interrupt_transfer(mouses_handle[i], 0x82, buf, nn, &nn, 1000);
        if (cnt < 0)
          printf("%s\n", libusb_error_name(cnt));
        for (int k = 0; k < nn; k++)
        {
          printf("%02x ", buf[k]);
        }
        printf("\n");
      }
      libusb_release_interface(mouses_handle[i], 0x01);
  }

  for (int i=0; i<num_mouse; i++) {
    libusb_close(mouses_handle[i]);
  }
  libusb_exit(NULL);
  return 0;
}
