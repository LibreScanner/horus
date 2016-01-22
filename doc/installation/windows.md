# Horus installation in Windows ![][windows-logo]

[return to Home](../../README.md)

### Not supported for version 0.2
However it can be installed following the next instructions.

First install USB Camera drivers:
* [Logitech Camera C270 Drivers](http://support.logitech.com/en_us/product/hd-webcam-c270)

Generate the executable file with Cygwin following the next [instructions](../development/ubuntu.md).

```bash
bash package.sh win32
```

Execute the installer and follow the wizard. This package contains all dependencies and also Arduino and FTDI drivers.

Reboot the computer to apply the changes.

[windows-logo]: ../images/windows.png
