#!/bin/bash

# This script is to package the Horus package for Linux/MacOSX/Windows
# This script should run under Linux and Mac OS X, as well as Windows with Cygwin.

#############################
# CONFIGURATION
#############################

##Select the build target
BUILD_TARGET=${1:-none}
#BUILD_TARGET=win32
#BUILD_TARGET=debian
#BUILD_TARGET=darwin
#BUILD_TARGET=version

EXTRA_ARGS=${2}

##Which version name are we appending to the final archive
export VERSION=0.2rc1
export DATETIME=`git log -1 --pretty=%ci`
export COMMIT=`git log -1 --pretty=%H`
TARGET_DIR=Horus-${VERSION}-${BUILD_TARGET}


##Which versions of external programs to use
WIN_PORTABLE_PY_VERSION=2.7.2.1


#############################
# Support functions
#############################
function checkTool
{
	if [ -z `which $1` ]; then
		echo "The $1 command must be somewhere in your \$PATH."
		echo "Fix your \$PATH or install it"
		exit 1
	fi
}

function downloadURL
{
	filename=`basename "$1"`
	echo "Checking for $filename"
	if [ ! -f "$filename" ]; then
		echo "Downloading $1"
		curl -L -O "$1"
		if [ $? != 0 ]; then
			echo "Failed to download $1"
			exit 1
		fi
	fi
}

function extract
{
	if [ $1 != ${1%%.exe} ] || [ $1 != ${1%%.zip} ] || [ $1 != ${1%%.msi} ]; then
		echo "Extracting $*"
		echo "7z x -y $*" >> log.txt
		7z x -y $* >> log.txt
		if [ $? != 0 ]; then
			echo "Failed to extract $*"
			exit 1
		fi
	elif [ $1 != ${1%%.tar.gz} ]; then
		echo "Extracting $*"
		echo "tar -zxvf $*" >> log.txt
		tar -zxvf $* >> log.txt
		if [ $? != 0 ]; then
			echo "Failed to extract $*"
			exit 1
		fi
	fi
}

#############################
# Actual build script
#############################
if [ "$BUILD_TARGET" = "none" ]; then
	echo "You need to specify a build target with:"
	echo "$0 win32"
	echo "$0 debian"
	echo "$0 darwin"
	exit 0
fi

# Change working directory to the directory the script is in
# http://stackoverflow.com/a/246128
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

checkTool git "git: http://git-scm.com/"
checkTool curl "curl: http://curl.haxx.se/"
if [ $BUILD_TARGET = "win32" ]; then
	#Check if we have 7zip, needed to extract and packup a bunch of packages for windows.
	checkTool 7z "7zip: http://www.7-zip.org/"
fi

# Update version data
if [ $BUILD_TARGET = "darwin" ]; then
	sed -i "" "s/__datetime__ = ''/__datetime__ = '$DATETIME'/;" src/horus/__init__.py
	sed -i "" "s/__commit__ = ''/__commit__ = '$COMMIT'/;" src/horus/__init__.py
else
	sed -i "s/__datetime__ = ''/__datetime__ = '$DATETIME'/;" src/horus/__init__.py
	sed -i "s/__commit__ = ''/__commit__ = '$COMMIT'/;" src/horus/__init__.py
fi

if [ $BUILD_TARGET = "version" ]
then
	echo '{"version": "'$VERSION'", "datetime": "'$DATETIME'", "commit": "'$COMMIT'"}' > version
else
	# Clean sources
	rm -rf version
	rm -rf deb_dist
	rm -rf win_dist
	rm -rf dar_dist
fi

#############################
# Debian packaging
#############################

if [ $BUILD_TARGET = "debian" ]; then
	# Generate Debian source package
	python setup.py --command-packages=stdeb.command sdist_dsc

	# Copy postinst and postrm files
	cp -a pkg/linux/debian/postinst deb_dist/horus-${VERSION}/debian/postinst
	cp -a pkg/linux/debian/postrm deb_dist/horus-${VERSION}/debian/postrm

	# Modify changelog and control files
	cp -a pkg/linux/debian/changelog deb_dist/horus-${VERSION}/debian/changelog
	cp -a pkg/linux/debian/control deb_dist/horus-${VERSION}/debian/control

	cd deb_dist/horus-${VERSION}
	if [ $EXTRA_ARGS ]; then
		if [ $EXTRA_ARGS = "-s" ]; then
			# Build and sign Debian sources
			debuild -S -sa
		elif [ $EXTRA_ARGS = "-i" ]; then
			# Install Debian package
			dpkg-buildpackage
			sudo dpkg -i --force-overwrite ../horus*.deb
			sudo apt-get -f install
		elif [ $EXTRA_ARGS = "-u" ]; then
			# Upload to launchpad
			debuild -S -sa
			PPA=${PPA:="ppa:bqlabs/horus-dev"}
			RELEASES="trusty vivid wily xenial"
			for RELEASE in $RELEASES ;
			do
			  cp debian/changelog debian/changelog.backup
			  sed -i "s/unstable/${RELEASE}/;s/${VERSION}/${VERSION}-${RELEASE}1/;" debian/changelog
			  debuild -S -sa
			  dput -f ${PPA} ../horus_${VERSION}-${RELEASE}1_source.changes
			  mv debian/changelog.backup debian/changelog
			done
		fi
		else
			# Build and sign Debian package
			dpkg-buildpackage
		fi

	# Clean directory
	cd ../..
	rm -rf "src/Horus.egg-info"
fi

#############################
# Darwin packaging
#############################

if [ $BUILD_TARGET = "darwin" ]; then

	mkdir -p dar_dist

	python setup_mac.py py2app -b dar_dist/build -d dar_dist/dist

	chmod 755 dar_dist/dist/Horus.app/Contents/Resources/res/tools/darwin/avrdude
	chmod 755 dar_dist/dist/Horus.app/Contents/Resources/res/tools/darwin/avrdude_bin
	chmod 755 dar_dist/dist/Horus.app/Contents/Resources/res/tools/darwin/lib/

	pkg/darwin/create-dmg/create-dmg \
		--volname "Horus Installer" \
		--volicon "res/horus.icns" \
		--background "res/images/installer_background.png" \
		--window-pos 200 120 \
		--window-size 700 400 \
		--icon-size 100 \
		--icon Horus.app 180 280 \
		--hide-extension Horus.app \
		--app-drop-link 530 275 \
		dar_dist/Horus_${VERSION}.dmg \
		dar_dist/dist/Horus.app

	rm -rf .eggs
fi

#############################
# Rest
#############################

#############################
# Download all needed files
#############################

function downloadDependencies
{
	DIR=`pwd`
	mkdir -p $WIN_DEP
	cd $WIN_DEP

	# Get portable python for windows and extract it. (Linux and Mac need to install python themselfs)
	downloadURL http://ftp.nluug.nl/languages/python/portablepython/v2.7/PortablePython_${WIN_PORTABLE_PY_VERSION}.exe
	downloadURL http://sourceforge.net/projects/pyserial/files/pyserial/2.7/pyserial-2.7.win32.exe
	downloadURL http://sourceforge.net/projects/comtypes/files/comtypes/0.6.2/comtypes-0.6.2.win32.exe
	downloadURL http://sourceforge.net/projects/pyopengl/files/PyOpenGL/3.0.1/PyOpenGL-3.0.1.win32.exe
	downloadURL http://pypi.python.org/packages/any/p/pyparsing/pyparsing-2.0.1.win32-py2.7.exe
	downloadURL http://sourceforge.net/projects/numpy/files/NumPy/1.8.1/numpy-1.8.1-win32-superpack-python2.7.exe
	downloadURL http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.9/opencv-2.4.9.exe
	downloadURL http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.4.3/windows/matplotlib-1.4.3.win32-py2.7.exe
	downloadURL http://sourceforge.net/projects/scipy/files/scipy/0.14.0/scipy-0.14.0-win32-superpack-python2.7.exe
	downloadURL https://pypi.python.org/packages/source/s/six/six-1.9.0.tar.gz
	downloadURL http://videocapture.sourceforge.net/VideoCapture-0.9-5.zip
	mkdir -p pyglet; cd pyglet;
	downloadURL http://pyglet.googlecode.com/files/pyglet-1.1.4.msi; cd ..

	# For windows extract portable python to include it.
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/App
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/Lib/site-packages
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/dateutil
	extract pyserial-2.7.win32.exe PURELIB
	extract comtypes-0.6.2.win32.exe PURELIB
	extract PyOpenGL-3.0.1.win32.exe PURELIB
	extract pyparsing-2.0.1.win32-py2.7.exe PURELIB
	extract numpy-1.8.1-win32-superpack-python2.7.exe numpy-1.8.1-sse2.exe
	extract numpy-1.8.1-sse2.exe PLATLIB
	extract scipy-0.14.0-win32-superpack-python2.7.exe scipy-0.14.0-sse2.exe
	extract scipy-0.14.0-sse2.exe PLATLIB
	extract matplotlib-1.4.3.win32-py2.7.exe PLATLIB
	extract six-1.9.0.tar.gz six-1.9.0/six.py
	extract opencv-2.4.9.exe opencv/build/python/2.7/x86/cv2.pyd
	extract VideoCapture-0.9-5.zip VideoCapture-0.9-5/Python27/DLLs/vidcap.pyd
	cd pyglet; extract pyglet-1.1.4.msi

	# Remove tests directories
	find . -name tests -type d -exec rm -rf {} \;

	cd $DIR
}

if [ $BUILD_TARGET = "win32" ]; then
	mkdir -p win_dist
	cd win_dist
	if [ ! $EXTRA_ARGS ]; then
		WIN_DEP=/tmp/win_dep
	else
		WIN_DEP=$EXTRA_ARGS
	fi
	if [ ! -d $WIN_DEP ]; then
		downloadDependencies
	fi
fi

#############################
# Build the packages
#############################

if [ $BUILD_TARGET = "win32" ]; then
	rm -rf ${TARGET_DIR}
	mkdir -p ${TARGET_DIR}

	rm -f log.txt

	mkdir -p ${TARGET_DIR}/python
	cp -rf $WIN_DEP/\$_OUTDIR/App/* ${TARGET_DIR}/python
	cp -rf $WIN_DEP/\$_OUTDIR/Lib/site-packages/wx* ${TARGET_DIR}/python/Lib/site-packages
	cp -rf $WIN_DEP/\$_OUTDIR/dateutil ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/PURELIB/serial ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/PURELIB/comtypes ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/PURELIB/OpenGL ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/PURELIB/pyparsing.py  ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/PLATLIB/numpy ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/PLATLIB/scipy ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/PLATLIB/matplotlib ${TARGET_DIR}/python/Lib
	touch $WIN_DEP/PLATLIB/mpl_toolkits/__init__.py
	cp -rf $WIN_DEP/PLATLIB/mpl_toolkits ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/six-1.9.0/six.py ${TARGET_DIR}/python/Lib
	cp -rf $WIN_DEP/opencv/build/python/2.7/x86/cv2.pyd ${TARGET_DIR}/python/DLLs
	cp -rf $WIN_DEP/VideoCapture-0.9-5/Python27/DLLs/vidcap.pyd ${TARGET_DIR}/python/DLLs
	cp -rf $WIN_DEP/pyglet ${TARGET_DIR}/python/Lib

	#if [ ! $EXTRA_ARGS ]; then
	#	rm -rf $WIN_DEP
	#fi

	# Clean up portable python a bit, to keep the package size down.
	rm -rf ${TARGET_DIR}/python/PyScripter.*
	rm -rf ${TARGET_DIR}/python/Doc
	rm -rf ${TARGET_DIR}/python/locale
	rm -rf ${TARGET_DIR}/python/tcl
	rm -rf ${TARGET_DIR}/python/Lib/test
	rm -rf ${TARGET_DIR}/python/Lib/site-packages/wx-2.8-msw-unicode/wx/tools
	rm -rf ${TARGET_DIR}/python/Lib/site-packages/wx-2.8-msw-unicode/wx/locale
	#Remove the gle files because they require MSVCR71.dll, which is not included. We also don't need gle, so it's safe to remove it.
	rm -rf ${TARGET_DIR}/python/Lib/OpenGL/DLLS/gle*

	# Add Horus
	mkdir -p ${TARGET_DIR}/res ${TARGET_DIR}/src
	cp -a ../res/* ${TARGET_DIR}/res
	cp -a ../src/* ${TARGET_DIR}/src
	cp -a ../horus ${TARGET_DIR}/horus.py

	# Add script files
	cp -a ../pkg/${BUILD_TARGET}/*.bat $TARGET_DIR/

	# Package the result
	rm -rf ../pkg/win32/dist
	ln -sf `pwd`/${TARGET_DIR} ../pkg/win32/dist
	makensis -DVERSION=${VERSION} ../pkg/win32/installer.nsi
	if [ $? != 0 ]; then echo "Failed to package NSIS installer"; exit 1; fi
	mv ../pkg/win32/Horus_${VERSION}.exe .
	rm -rf ../pkg/win32/dist

	cd ..
fi

# Restore version data
if [ $BUILD_TARGET = "darwin" ]; then
	sed -i "" "s/__datetime__ = '$DATETIME'/__datetime__ = ''/;" src/horus/__init__.py
	sed -i "" "s/__commit__ = '$COMMIT'/__commit__ = ''/;" src/horus/__init__.py
else
	sed -i "s/__datetime__ = '$DATETIME'/__datetime__ = ''/;" src/horus/__init__.py
	sed -i "s/__commit__ = '$COMMIT'/__commit__ = ''/;" src/horus/__init__.py
fi
