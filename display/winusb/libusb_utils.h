#ifndef DISPLAY_WINUSB_LIBUSB_UTILS_H_
#define DISPLAY_WINUSB_LIBUSB_UTILS_H_

#include <libusb.h>
#include <stdio.h>

#if defined(_MSC_VER) && (_MSC_VER < 1900)
#define snprintf _snprintf
#endif

void print_endpoint_comp(const struct libusb_ss_endpoint_companion_descriptor *ep_comp);
void print_endpoint(const struct libusb_endpoint_descriptor *endpoint);
void print_altsetting(const struct libusb_interface_descriptor *interface);
void print_2_0_ext_cap(struct libusb_usb_2_0_extension_descriptor *usb_2_0_ext_cap);
void print_ss_usb_cap(struct libusb_ss_usb_device_capability_descriptor *ss_usb_cap);
void print_bos(libusb_device_handle *handle);
void print_interface(const struct libusb_interface *interface);
void print_configuration(struct libusb_config_descriptor *config);
int print_device(libusb_device *dev, int level);

#define HID_REPORT_TYPE_INPUT 0x01
#define HID_REPORT_TYPE_OUTPUT 0x02
#define HID_REPORT_TYPE_FEATURE 0x03

int get_hid_record_size(uint8_t *hid_report_descriptor, int size, int type);

#define LIBUSB_ASSERTCALL(A)                                 \
  do                                                       \
  {                                                        \
    int r = (A);                                           \
    if (r < 0)                                             \
    {                                                      \
      printf("%s failed: %s\n", #A, libusb_error_name(r)); \
      exit(-1);                                            \
    }                                                      \
  } while (0)

#define LIBUSB_CHECK_RET(NAME, RET) do { \
  if ((RET) < 0) { \
    printf("%s: ", (#NAME)); \
    printf("failed with %s", libusb_error_name((RET)));\
  }  \
} while (0)

#define LIBUSB_CHECK_RET_BUFFER(NAME, RET, BUFFER) \
  do {                                                                         \
    printf("%s: ", (#NAME));                                                   \
    if ((RET) < 0)                                                            \
    {                                                                       \
      printf("failed with %s\n", libusb_error_name((RET))); \
    }                                                                       \
    else                                                                    \
    {                                                                       \
      for (int i = 0; i < (RET); i++)                                         \
      {                                                                     \
        printf("%02x ", (BUFFER)[i]);                                       \
      }                                                                     \
      printf("\n");                                                         \
    }                                                                       \
  }                                                                         \
  while (0)

#define LIBUSB_CHECK_RET_BUFFER_SIZE(NAME, RET, BUFFER, SIZE) do {          \
  printf("%s: ", (#NAME));                                                  \
  if ((RET) < 0) {                                                         \
    printf("failed with %s\n", libusb_error_name(RET));\
  } else {                                                               \
    for (int i = 0; i < (SIZE); i++) {                                      \
      printf("%02x ", (BUFFER)[i]);                                      \
    }                                                                    \
    printf("\n");                                                        \
  }                                                                      \
} while (0)

#endif // !DISPLAY_LIBUSB_UTILS_H_