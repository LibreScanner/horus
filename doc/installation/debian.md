# Horus installation in Debian ![][debian-logo]

[return to Home](../../README.md)

First you need to build and install our [custom OpenCV](https://github.com/bqlabs/opencv/wiki/Build)

Then, add our ppa for Horus

```bash
sudo apt-get install software-properties-common python-software-properties
sudo add-apt-repository ppa:bqlabs/horus
sudo sed -i 's/jessie/trusty/g' /etc/apt/sources.list.d/bqlabs-*.list
```

Update your system

```bash
sudo apt-get update
```

Install Horus

```bash
sudo apt-get install horus
```

If user has no access to serial port, execute:

```bash
sudo usermod -a -G dialout $USER
```

Reboot the computer to apply the changes

```bash
sudo reboot
```

### Update Horus

If there is a new release just execute:

```bash
sudo apt-get upgrade
```

<br>

NOTE: our packages are hosted in launchpad.net

* [PPA Horus](https://launchpad.net/~bqlabs/+archive/ubuntu/horus/)
* [PPA Horus dev](https://launchpad.net/~bqlabs/+archive/ubuntu/horus-dev/)

[debian-logo]: ../images/debian.png
