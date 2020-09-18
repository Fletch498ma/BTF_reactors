import sys
import glob
import serial
from serial.tools import list_ports
import ctypes
from ctypes import util

iokit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('IOKit'))

kIOMasterPortDefault = ctypes.c_void_p.in_dll(iokit, "kIOMasterPortDefault")

iokit.IOServiceMatching.restype = ctypes.c_void_p

iokit.IOServiceGetMatchingServices.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
iokit.IOServiceGetMatchingServices.restype = ctypes.c_void_p

serial_port_iterator = ctypes.c_void_p()

print('kIOMasterPortDefault =', kIOMasterPortDefault)

response = iokit.IOServiceGetMatchingServices(
    kIOMasterPortDefault,
    iokit.IOServiceMatching('bIOSerialBSDClient'),
    ctypes.byref(serial_port_iterator))
print('serial_port_iterator =', serial_port_iterator)

def comports():
    # Scan for all iokit serial ports
    services = GetIOServicesByType('IOSerialBSDClient')
    ports = []
    serial_interfaces = scan_interfaces()
    for service in services:
        # First, add the callout device file.
        device = get_string_property(service, "IOCalloutDevice")
        if device:
            info = list_ports_common.ListPortInfo(device)
            # If the serial port is implemented by IOUSBDevice
            usb_device = GetParentDeviceByType(service, "IOUSBDevice")
            if usb_device:
                # fetch some useful informations from properties
                info.vid = get_int_property(usb_device, "idVendor", kCFNumberSInt16Type)
                info.pid = get_int_property(usb_device, "idProduct", kCFNumberSInt16Type)
                info.serial_number = get_string_property(usb_device, "USB Serial Number")
                info.product = get_string_property(usb_device, "USB Product Name") or 'n/a'
                info.manufacturer = get_string_property(usb_device, "USB Vendor Name")
                locationID = get_int_property(usb_device, "locationID", kCFNumberSInt32Type)
                info.location = location_to_string(locationID)
                info.interface = search_for_locationID_in_interfaces(serial_interfaces, locationID)
                info.apply_usb_info()
            ports.append(info)
    return ports

if __name__ == '__main__':
    print(comports())

