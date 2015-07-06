# Horus installation in Raspbian ![][raspbian-logo]

[return to Home](../../README.md)

#### NOTE: this version is experimental for RPi2!

Download our *HorusPi* image:
* Horus Pi

Write this image in a 8G SD card

1. Plug your SD card
2. Unmount SD card partitions
3. Detect your SD card name ```df -h```
	* /dev/mmcblk0
	* /dev/sdd
	* ...
4. Burn the image:
	```
	dd bs=4M if=HorusPi.img of=/dev/mmcblk0
	```

Then, load your SD card into the RPi2 and go ahead!

[raspbian-logo]: ../images/raspbian.png