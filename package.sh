#!/bin/bash

# This script is to package the Horus package for Windows/Linux
# This script should run under Linux and Mac OS X, as well as Windows with Cygwin.

#############################
# CONFIGURATION
#############################

##Select the build target
BUILD_TARGET=${1:-none}
#BUILD_TARGET=win32
#BUILD_TARGET=debian_i386
#BUILD_TARGET=debian_amd64

##Do we need to create the final archive
ARCHIVE_FOR_DISTRIBUTION=1
##Which version name are we appending to the final archive
export BUILD_NAME=1.0
TARGET_DIR=Horus-${BUILD_NAME}-${BUILD_TARGET}

##Which versions of external programs to use
WIN_PORTABLE_PY_VERSION=2.7.2.1 #TODO: 2.7.6.1


#############################
# Support functions
#############################
function checkTool
{
	if [ -z `which $1` ]; then
		echo "The $1 command must be somewhere in your \$PATH."
		echo "Fix your \$PATH or install $2"
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
	echo "Extracting $*"
	echo "7z x -y $*" >> log.txt
	7z x -y $* >> log.txt
	if [ $? != 0 ]; then
        echo "Failed to extract $*"
        exit 1
	fi
}

#############################
# Actual build script
#############################
if [ "$BUILD_TARGET" = "none" ]; then
	echo "You need to specify a build target with:"
	echo "$0 win32"
	echo "$0 debian_i368"
	echo "$0 debian_amd64"
	exit 0
fi

# Change working directory to the directory the script is in
# http://stackoverflow.com/a/246128
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

checkTool curl "curl: http://curl.haxx.se/"
if [ $BUILD_TARGET = "win32" ]; then
	#Check if we have 7zip, needed to extract and packup a bunch of packages for windows.
	checkTool 7z "7zip: http://www.7-zip.org/"
fi

#############################
# Debian 32bit .deb
#############################

if [ "$BUILD_TARGET" = "debian_i386" ]; then
	rm -rf pkg/linux/${BUILD_TARGET}/usr/share/horus
	mkdir -p  pkg/linux/${BUILD_TARGET}/usr/share/horus
	cp -a doc  pkg/linux/${BUILD_TARGET}/usr/share/horus/
	cp -a res  pkg/linux/${BUILD_TARGET}/usr/share/horus/
	cp -a src  pkg/linux/${BUILD_TARGET}/usr/share/horus/
	echo $BUILD_NAME >  pkg/linux/${BUILD_TARGET}/usr/share/horus/version
	sudo chown root:root  pkg/linux/${BUILD_TARGET} -R
	sudo chmod 755  pkg/linux/${BUILD_TARGET}/usr -R
	sudo chmod 755  pkg/linux/${BUILD_TARGET}/DEBIAN -R
	cd  pkg/linux
	dpkg-deb --build ${BUILD_TARGET} $(dirname ${TARGET_DIR})/horus_${BUILD_NAME}-${BUILD_TARGET}.deb
	sudo chown `id -un`:`id -gn` ${BUILD_TARGET} -R
	exit
fi

#############################
# Debian 64bit .deb
#############################

if [ "$BUILD_TARGET" = "debian_amd64" ]; then
	rm -rf  pkg/linux/${BUILD_TARGET}/usr/share/horus
	mkdir -p  pkg/linux/${BUILD_TARGET}/usr/share/horus
	cp -a doc  pkg/linux/${BUILD_TARGET}/usr/share/horus/
	cp -a res  pkg/linux/${BUILD_TARGET}/usr/share/horus/
	cp -a src  pkg/linux/${BUILD_TARGET}/usr/share/horus/
	echo $BUILD_NAME >  pkg/linux/${BUILD_TARGET}/usr/share/horus/version
	sudo chown root:root  pkg/linux/${BUILD_TARGET} -R
	sudo chmod 755  pkg/linux/${BUILD_TARGET}/usr -R
	sudo chmod 755  pkg/linux/${BUILD_TARGET}/DEBIAN -R
	cd  pkg/linux
	dpkg-deb --build ${BUILD_TARGET} $(dirname ${TARGET_DIR})/horus_${BUILD_NAME}-${BUILD_TARGET}.deb
	sudo chown `id -un`:`id -gn` ${BUILD_TARGET} -R
	exit
fi


#############################
# Rest
#############################

#############################
# Download all needed files.
#############################

if [ $BUILD_TARGET = "win32" ]; then
	mkdir -p \$_WIN
	cd \$_WIN
	#Get portable python for windows and extract it. (Linux and Mac need to install python themselfs)
	downloadURL http://ftp.nluug.nl/languages/python/portablepython/v2.7/PortablePython_${WIN_PORTABLE_PY_VERSION}.exe
	#downloadURL https://www.python.org/ftp/python/2.7.8/python-2.7.8.msi
	#downloadURL http://sourceforge.net/projects/wxpython/files/wxPython/3.0.0.0/wxPython3.0-win32-3.0.0.0-py27.exe
	downloadURL http://sourceforge.net/projects/pyserial/files/pyserial/2.7/pyserial-2.7.win32.exe
	downloadURL http://sourceforge.net/projects/pyopengl/files/PyOpenGL/3.0.1/PyOpenGL-3.0.1.win32.exe
	downloadURL https://pypi.python.org/packages/any/p/pyparsing/pyparsing-2.0.1.win32-py2.7.exe
	downloadURL http://sourceforge.net/projects/numpy/files/NumPy/1.8.1/numpy-1.8.1-win32-superpack-python2.7.exe
	downloadURL http://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.9/opencv-2.4.9.exe
	downloadURL https://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.3.0/matplotlib-1.3.0.win32-py2.7.exe
	downloadURL http://sourceforge.net/projects/scipy/files/scipy/0.14.0/scipy-0.14.0-win32-superpack-python2.7.exe
	downloadURL http://videocapture.sourceforge.net/VideoCapture-0.9-5.zip
	downloadURL http://sourceforge.net/projects/comtypes/files/comtypes/0.6.2/comtypes-0.6.2.win32.exe
	mkdir -p pyglet; cd pyglet;
	downloadURL http://pyglet.googlecode.com/files/pyglet-1.1.4.msi; cd .. 
fi

#############################
# Build the packages
#############################
rm -rf ${TARGET_DIR}
mkdir -p ${TARGET_DIR}

rm -f log.txt
if [ $BUILD_TARGET = "win32" ]; then
	#For windows extract portable python to include it.
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/App
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/Lib/site-packages
	extract PortablePython_${WIN_PORTABLE_PY_VERSION}.exe \$_OUTDIR/dateutil
	#extract python-2.7.8.msi 
	#extract wxPython3.0-win32-3.0.0.0-py27.exe
	extract pyserial-2.7.win32.exe PURELIB
	extract comtypes-0.6.2.win32.exe PURELIB
	extract PyOpenGL-3.0.1.win32.exe PURELIB
	extract pyparsing-2.0.1.win32-py2.7.exe PURELIB
	extract numpy-1.8.1-win32-superpack-python2.7.exe numpy-1.8.1-sse2.exe
	extract numpy-1.8.1-sse2.exe PLATLIB
	extract scipy-0.14.0-win32-superpack-python2.7.exe scipy-0.14.0-sse2.exe
	extract scipy-0.14.0-sse2.exe PLATLIB
	extract matplotlib-1.3.0.win32-py2.7.exe PLATLIB
	extract opencv-2.4.9.exe opencv/build/python/2.7/x86/cv2.pyd
	extract VideoCapture-0.9-5.zip VideoCapture-0.9-5/Python27/DLLs/vidcap.pyd
	cd pyglet; extract pyglet-1.1.4.msi; cd ..

	mkdir -p ${TARGET_DIR}/python
	mv \$_OUTDIR/App/* ${TARGET_DIR}/python
	mv \$_OUTDIR/Lib/site-packages/wx* ${TARGET_DIR}/python/Lib/site-packages
	mv \$_OUTDIR/dateutil ${TARGET_DIR}/python/Lib
	mv PURELIB/serial ${TARGET_DIR}/python/Lib
	mv PURELIB/comtypes ${TARGET_DIR}/python/Lib
	mv PURELIB/OpenGL ${TARGET_DIR}/python/Lib
	mv PURELIB/pyparsing.py  ${TARGET_DIR}/python/Lib
	mv PLATLIB/numpy ${TARGET_DIR}/python/Lib
	mv PLATLIB/scipy ${TARGET_DIR}/python/Lib
	mv PLATLIB/matplotlib ${TARGET_DIR}/python/Lib
	touch PLATLIB/mpl_toolkits/__init__.py
	mv PLATLIB/mpl_toolkits ${TARGET_DIR}/python/Lib
	mv opencv/build/python/2.7/x86/cv2.pyd ${TARGET_DIR}/python/DLLs
	mv VideoCapture-0.9-5/Python27/DLLs/vidcap.pyd ${TARGET_DIR}/python/DLLs
	mv pyglet ${TARGET_DIR}/python/Lib
	
	rm -rf \$_OUTDIR
	rm -rf opencv
	rm -rf PURELIB
	rm -rf PLATLIB
	rm -rf VideoCapture-0.9-5
	rm -rf Win32
	rm -rf pyglet

	#Clean up portable python a bit, to keep the package size down.
	rm -rf ${TARGET_DIR}/python/PyScripter.*
	rm -rf ${TARGET_DIR}/python/Doc
	rm -rf ${TARGET_DIR}/python/locale
	rm -rf ${TARGET_DIR}/python/tcl
	rm -rf ${TARGET_DIR}/python/Lib/test
	rm -rf ${TARGET_DIR}/python/Lib/site-packages/wx-2.8-msw-unicode/wx/tools
	rm -rf ${TARGET_DIR}/python/Lib/site-packages/wx-2.8-msw-unicode/wx/locale
	#Remove the gle files because they require MSVCR71.dll, which is not included. We also don't need gle, so it's safe to remove it.
	rm -rf ${TARGET_DIR}/python/Lib/OpenGL/DLLS/gle*
fi

#add Horus
mkdir -p ${TARGET_DIR}/doc ${TARGET_DIR}/res ${TARGET_DIR}/src
cp -a ../doc/* ${TARGET_DIR}/doc
cp -a ../res/* ${TARGET_DIR}/res
cp -a ../src/* ${TARGET_DIR}/src
#Add horus version file
echo $BUILD_NAME > ${TARGET_DIR}/version

#add script files
if [ $BUILD_TARGET = "win32" ]; then
	cp -a ../pkg/${BUILD_TARGET}/*.bat $TARGET_DIR/
else
	cp -a ../pkg/${BUILD_TARGET}/*.sh $TARGET_DIR/
fi

#package the result
if (( ${ARCHIVE_FOR_DISTRIBUTION} )); then
	if [ $BUILD_TARGET = "win32" ]; then
		rm -rf ../pkg/win32/dist
		ln -sf `pwd`/${TARGET_DIR} ../pkg/win32/dist
		makensis -DVERSION=${BUILD_NAME} ../pkg/win32/installer.nsi
		if [ $? != 0 ]; then echo "Failed to package NSIS installer"; exit 1; fi
		rm -rf ../pkg/win32/dist
		#cd ../
		#rm -rf \$_WIN
	fi
else
	echo "Installed into ${TARGET_DIR}"
fi
