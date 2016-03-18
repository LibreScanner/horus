#Horus development in Mac OS X

[return to Home](../../README.md)


If you are a developer and you want to modify the code, contribute, build packages, etc. you may follow this steps

## 1. Set up the environment

### Tools

#### Install FTDI driver
* [FTDI USB Driver](http://www.ftdichip.com/Drivers/VCP/MacOSX/FTDIUSBSerialDriver_v2_3.dmg)

#### Atom IDE
Download open source [Atom code editor](https://atom.io/).

#### Install Homebrew
```bash
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

#### Git version control
```bash
brew install git
```

#### Python
Install non-system, framework-based, universal [Python](https://www.python.org/ftp/python/2.7.10/python-2.7.10-macosx10.6.pkg). Not with brew.

#### Python tools
```bash
pip install -U pip setuptools
pip install -U virtualenv
```

### Dependencies

First you need to configure a virtualenv

```bash
virtualenv $HOME/venv
```

In order to use wxPython from the virtualenv this hack is needed

```bash
cp `which python` $HOME/venv/bin/python;
echo 'export PYTHONHOME=$HOME/venv' >> $HOME/venv/bin/activate;
source $HOME/venv/bin/activate
```

Then, you can install the python dependencies into the virtualenv

#### OpenCV
```bash
brew tap homebrew/science
brew info opencv
brew install opencv
```

```bash
ln -s /usr/local/Cellar/opencv/2.4.12_2/lib/python2.7/site-packages/cv.py $HOME/venv/lib/python2.7/site-packages;
ln -s /usr/local/Cellar/opencv/2.4.12_2/lib/python2.7/site-packages/cv2.so $HOME/venv/lib/python2.7/site-packages
```

#### wxPython
```bash
brew install wxpython
```

```bash
ln -s /usr/local/Cellar/wxpython/3.0.2.0/lib/python2.7/site-packages/wx* $HOME/venv/lib/python2.7/site-packages
```

#### Python modules
```bash
pip install -U pyserial pyopengl pyopengl-accelerate numpy scipy matplotlib==1.4.0
```

##### Pyobjc QTKit

* Install Xcode.app. Then, switch xcode commands and accept the xcodebuild license

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
sudo xcodebuild
```

* Downgrade setuptools
```bash
pip install -U setuptools==3.4
```

* Install qtkit 2.5.1
```bash
pip install -U pyobjc-core==2.5.1
pip install -U pyobjc-framework-cocoa==2.5.1
pip install -U pyobjc-framework-quartz==2.5.1
pip install -U pyobjc-framework-qtkit==2.5.1
```

* Restore setuptools
```bash
pip install -U setuptools
```

In order to generate dmg package, some extra dependencies are needed

#### Packaging dependencies
```bash
pip install -U py2app==0.7.2
```

Also some patches are needed to make py2app work

```bash
cd $HOME/venv/lib/python2.7/site-packages/py2app/recipes;

sed -i '' 's/scan_code/_scan_code/g' virtualenv.py;
sed -i '' 's/load_module/_load_module/g' virtualenv.py;

cd $HOME/venv/lib/python2.7/site-packages/macholib;

sed -i '' 's/loader=loader.filename/loader_path=loader.filename/g' MachOGraph.py
```

To reduce the package size, "tests" directories must be removed

```bash
cd $HOME/venv/lib/python2.7/site-packages;
find . -name tests -type d -exec rm -r {} +
```

## 2. Download source code

All source code is available on GitHub. You can download main Horus project by doing:

### Horus
```bash
git clone https://github.com/bq/horus.git
cd horus
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
