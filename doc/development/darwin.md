#Horus development in Mac OS X

[return to Home](../../README.md)


If you are a developer and you want to modify the code, contribute, build packages, etc. you may follow this steps

## 1. Set up the environment

### Tools

#### Install FTDI driver
* [FTDI USB Driver](http://www.ftdichip.com/Drivers/VCP/MacOSX/FTDIUSBSerialDriver_v2_3.dmg)

#### Install Homebrew
```bash
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

#### Atom IDE
Download open source [Atom code editor](https://atom.io/).

#### Git version control
```bash
brew install git
```

#### Python
Install non-system, framework-based, universal [Python](http://www.python.org/ftp/python/2.7.6/python-2.7.6-macosx10.6.dmg). Not with brew.

#### Python tools
```bash
pip install -U pip setuptools
```

### Dependencies

Following dependencies are included in dmg package, but if you want to install it manually, they are:

#### OpenCV
```bash
brew tap homebrew/science
brew info opencv
brew install opencv
```

```bash
sudo ln -s /usr/local/Cellar/opencv/2.4.12_2/lib/python2.7/site-packages/cv.py /Library/Python/2.7/site-packages/cv.py
sudo ln -s /usr/local/Cellar/opencv/2.4.12_2/lib/python2.7/site-packages/cv2.so /Library/Python/2.7/site-packages/cv2.so
```

#### wxPython
```bash
brew install wxpython
```

```bash
sudo ln -s /usr/local/Cellar/wxpython/3.0.2.0/lib/python2.7/site-packages/wx-3.0-osx_cocoa/wx /Library/Python/2.7/site-packages/wx
```

#### Python modules
```bash
pip install -U pyserial pyopengl pyopengl-accelerate numpy scipy matplotlib==1.4.0 pyobjc-framework-qtkit
```

NOTE: if 'xcodebuild' fails, try:

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

In order to generate dmg package, some extra dependencies are needed

#### Packaging dependencies
```bash
pip install -U py2app==0.7.2
```

To reduce the package size, "tests" directories must be removed

```bash
cd /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages
sudo find . -name tests -type d -exec rm -r {} +
```

Also some patches are needed to make py2app work

```bash
cd /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/py2app/recipes

sudo sed -i '' 's/scan_code/_scan_code/g' virtualenv.py
sudo sed -i '' 's/load_module/_load_module/g' virtualenv.py

cd /Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/macholib

sudo sed -i '' 's/loader=loader.filename/loader_path=loader.filename/g' MachOGraph.py
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

## 3. Execute source code

In the project directory, execute the command:

```bash
./horus
```

## 4. Build packages

Horus development comes with a script *package.sh*. This script generates a final release package. You should not need it during development, unless you are changing the release process. If you want to distribute your own version of Horus, then the *package.sh* script will allow you to do that.

```bash
bash package.sh darwin  # Generate dmg package
```
