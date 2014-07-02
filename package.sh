#!/bin/bash

# This script is to package the Horus package for Linux

#############################
# CONFIGURATION
#############################

##Select the build target
BUILD_TARGET=${1:-none}
#BUILD_TARGET=debian_i386
#BUILD_TARGET=debian_amd64

##Do we need to create the final archive
ARCHIVE_FOR_DISTRIBUTION=1
##Which version name are we appending to the final archive
export BUILD_NAME=1.0

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
	echo "$0 debian_i368"
	echo "$0 debian_amd64"
	exit 0
fi

# Change working directory to the directory the script is in
# http://stackoverflow.com/a/246128
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

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
