#Horus development in Mac OS X

[return to Home](../../README.md)


If you are a developer and you want to modify the code, contribute, build packages, etc. you may follow this steps

## 1. Set up the environment

### Tools

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
Install non-system, framework-based, universal [Python](http://www.python.org/ftp/python/2.7.6/python-2.7.6-macosx10.6.dmg). Not with brew

#### Python tools
```bash
sudo easy_install pip
sudo -H pip install -U pip setuptools
```

### Dependencies

Following dependencies are included in dmg package, but if you want to install it manually, they are:

#### OpenCV
```bash
brew tap homebrew/science
brew install opencv
```

#### wxPython
```bash
brew install wxpython
```

NOTE: in order to build Horus for other Mac OS X versions you must to install official dmg

* [wxPython](http://downloads.sourceforge.net/wxpython/3.0.2.0/wxPython3.0-osx-3.0.2.0-cocoa-py2.7.dmg). Not with brew

```bash
sudo installer -pkg /path/to/pkg -target /
```

#### Python modules
```bash
sudo -H pip install -U pyserial pyopengl pyopengl-accelerate numpy scipy matplotlib==1.4.0 pyobjc-framework-qtkit
```

In order to generate dmg package, some extra dependencies are needed

#### Packaging dependencies
```bash
sudo -H pip install -U py2app==0.7.2
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
