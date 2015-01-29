# Horus

Horus is a general solution for 3D scanning. It provides some graphic user interfaces for connection, configuration, control, calibration and scanning. It is ready to use with Open Source [Ciclop 3D Scanner](http://diwo.bq.com/en/ciclop-released/)

This project has been developed in Python language and it is distributed under GPL v2 license.

More interest links are shown below:

* [Presentation](http://diwo.bq.com/en/presentacion-ciclop-horus/)
* [Electronics](http://diwo.bq.com/en/zum-scan-released/) 
* [Firmware](http://diwo.bq.com/en/horus-fw-released/)

# Installing

### GNU/Linux Ubuntu

First of all upgrade your system

```bash
sudo apt-get update
sudo apt-get dist-upgrade
```

To install Horus execute .deb file. This package installs all dependencies

```bash
sudo dpkg -i horus_0.1-*.deb
```

If user has no access to serial port, execute:

```bash
sudo usermod -a -G dialout $USER
```

Reboot the computer to apply the changes

```bash
sudo reboot
```

### Windows

To install USB Camera drivers follow this instructions: http://support.logitech.com/en_us/product/hd-webcam-c270

Execute .exe file. This package contains all dependencies

Reboot the computer to apply the changes


# Development

Horus has been developed in [Ubuntu Gnome](http://ubuntugnome.org/). If you are a developer and you want to modify the code, contribute, build packages, etc. you may follow this steps:

## 1. Set up the environment

### Tools

#### Sublime Text 3 IDE
```bash
sudo add-apt-repository ppa:webupd8team/sublime-text-3
sudo apt-get update
sudo apt-get install sublime-text-installer
```

#### Arduino IDE
```bash
sudo apt-get install arduino arduino-core
```

#### Stino plugin
https://github.com/Robot-Will/Stino

#### Git version control
```bash
sudo apt-get install git gitk
```

### Dependencies

Following dependencies are included in deb package, but if you want to install it manually, they are:

#### Python
```bash
sudo apt-get install python-wxgtk2.8
sudo apt-get install python-opengl
sudo apt-get install python-serial
sudo apt-get install python-numpy
sudo apt-get install python-pyglet
sudo apt-get install python-matplotlib
sudo apt-get install python-scipy
sudo apt-get install python-opencv
```

#### FTDI drivers
```bash
sudo apt-get install libftdi1
```

#### Video 4 Linux
```bash
sudo apt-get install v4l-utils
```

In order to build OpenCV and generate Debian and Windows packages, some extra dependencies are needed

#### Packaging
```bash
sudo apt-get install build-essential cmake pkg-config python-dev libv4l-dev libgtk2.0-dev libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev  libjpeg-dev libpng-dev libtiff-dev libjasper-dev p7zip-full curl nsis
```

## 2. Download source code

All source code is available on GitHub. You can download main Horus project by doing:

### Horus
```bash
git clone https://github.com/bq/horus.git
```
or
```bash
git clone git@github.com:bq/horus.git
```

Several improvements and optimizations have been made in GNU/Linux version of OpenCV libraries. If you want to contribute to this custom version, you can download it from:

### Custom OpenCV
```bash
git clone https://github.com/bq/opencv.git
```
or
```bash
git clone git@github.com:bq/opencv.git
```

## 3. Build packages

Horus development comes with a script "package.sh", this script has been designed to run under *nix OSes (Linux, MacOS). For Windows the package.sh script can be run from bash using git.
The "package.sh" script generates a final release package. You should not need it during development, unless you are changing the release process. If you want to distribute your own version of Horus, then the package.sh script will allow you to do that.

### GNU/Linux Ubuntu
```bash
sudo ./package.sh debian_amd64 -j3 # or debian_i386
```

### Windows
```bash
sudo ./package.sh win32
```

### GNU/Linux Fedora

TODO

### Mac OS X

TODO