# Installation

> This is a step-by-step guide to install the project on your local machine.

## Setup the Pi

- Flash the Raspberry Pi OS Lite image to your SD card using the Raspberry Pi Imager. Then boot your Raspberry Pi Zero 2W (or any other model) with the SD card.

- Connect to your machine via SSH **or** using a monitor + keyboard. Be sure to be connected to the same network.

```bash
ssh rasp@pi.local
```

```plaintext
Username: raspberry
Password: raspberry
Hostname: pi
```

- Reset the locale settings.

```bash
sudo dpkg-reconfigure locales
```

```bash
sudo update-locale LANG=en_GB.UTF-8 LC_ALL=en_GB.UTF-8
sudo reboot
```

- Update your system.

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

- Install `git` and `pip`.

```bash
sudo apt install git python3-pip make -y
```

## Improve performance for Matrix

- Add a small flag at the end of the line to add better results:

```bash
sudo nano /boot/firmware/cmdline.txt
```

```plaintext
isolcpus=3
```

## Disable sound module

- Edit the file `/etc/modprobe.d/raspi-blacklist.conf` and add the following line:

```bash
sudo nano /etc/modprobe.d/blacklist-rgb-matrix.conf
```

```bash
blacklist snd_bcm2835
```

- Update the kernel modules.

```bash
sudo update-initramfs -u
```

- Reboot the Raspberry Pi.

```bash
sudo reboot
```

## Install the project

- Clone the repository.

```bash
git clone --recurse-submodules https://github.com/MorganKryze/Athunas.git
```

- Change directory to the project.

```bash
cd Athunas
```

## Build & Run

- We use our `Makefile` to install the project dependencies.

```bash
make setup
```

- (Optional) If you did the wiring, you may try the demo.

```bash
make example
```

> [!TIP]
> If you get any error with the display, open the `Makefile` and try the following steps:
>
> - Add/remove: `--led-no-hardware-pulse`;
> - Check the wiring;
> - Breathe in, breathe out, do it again.

- Finally, run the project.

```bash
make run
```
