# Horus installation in Ubuntu ![][ubuntu-logo]

[return to Home](../../README.md)

### Version 0.2 release candidate 1

##### Add Horus ppa:

*NOTE*: Official versions are hosted in **ppa:bqlabs/horus**. Alpha, beta and rc versions are hosted in **ppa:bqlabs/horus-dev**.

```bash
sudo add-apt-repository ppa:bqlabs/horus-dev
sudo apt-get update
```

##### Remove older OpenCV

*NOTE*: try to remove previous versions of opencv:

```bash
sudo apt-get remove python-opencv
sudo apt-get autoremove
```

##### Install Horus

*NOTE*: this command installs all the dependencies, including custom OpenCV libraries.

```bash
sudo apt-get install horus
```

If user has no access to serial port, execute:

```bash
sudo usermod -a -G dialout $USER
sudo reboot
```

##### Update Horus

If there is a new release just execute:

```bash
sudo apt-get upgrade
```

<br>

NOTE: our packages are hosted in launchpad.net

* [PPA Horus](https://launchpad.net/~bqlabs/+archive/ubuntu/horus/)
* [PPA Horus dev](https://launchpad.net/~bqlabs/+archive/ubuntu/horus-dev/)

[ubuntu-logo]: ../images/ubuntu.png
