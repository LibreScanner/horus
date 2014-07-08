Horus
=====

Development
===========

Horus is developed in Python.


Debian and Ubuntu Linux
--------

```bash
sudo apt-get install python-wxgtk2.8
sudo apt-get install python-opengl
sudo apt-get install python-serial
sudo apt-get install python-numpy
sudo apt-get install python-opencv
sudo apt-get install python-pyglet
sudo apt-get install python-matplotlib
sudo apt-get install python-scipy
```

Fedora Linux
--------
```bash
sudo yum install wxPython
sudo yum install python-opengl
sudo yum install pyserial
sudo yum install numpy
sudo yum install opencv-python
sudo yum install python-pyglet
sudo yum install python-matplotlib
sudo yum install scipy
```

Mac OS X
--------

TODO


Packaging
=========

Horus development comes with a script "package.sh", this script has been designed to run under *nix OSes (Linux, MacOS). For Windows the package.sh script can be run from bash using git.
The "package.sh" script generates a final release package. You should not need it during development, unless you are changing the release process. If you want to distribute your own version of Horus, then the package.sh script will allow you to do that.

Debian and Ubuntu Linux
--------

```bash
sudo ./package.sh debian_amd64  # or debian_i386

sudo dpkg -i pkg/linux/horus*.deb
```

Fedora Linux
--------

TODO

Windows
--------

```bash
sudo apt-get install curl nsis

sudo ./package.sh win32

wine pkg/win32/Horus*.exe
```

Mac OS X
--------

TODO