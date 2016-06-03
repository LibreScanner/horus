# Horus installation in Fedora ![][fedora-logo]

[return to Home](../../README.md)

### Not supported for version 0.2

Versions: 21, 22

However it can be installed following the next instructions.

Add a [Copr repository with horus](https://copr.fedoraproject.org/coprs/churchyard/horus/):

```bash
sudo dnf copr enable churchyard/horus
```

(Use `yum` instead of `dnf` on older Fedoras.)

Install Horus:

```bash
sudo dnf install horus
```

If user has no access to serial port, execute:

```bash
sudo usermod -a -G dialout $USER
```

Log out and in again after adding yourself to the group.

### Update Horus

If there is a new release just execute:

```bash
sudo dnf upgrade horus
```

[fedora-logo]: ../images/fedora.png
