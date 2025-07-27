#!/bin/bash

echo "Starting installation script..."

echo "Updating package lists..."
sudo apt update

echo "Installing nala for faster package management..."
sudo apt install nala -y

echo "Removing unnecessary packages..."
sudo nala autoremove -y

echo "Upgrading system packages..."
sudo nala upgrade -y

echo "Installing required packages..."
sudo nala install git python3-pip python3-venv make -y

echo "Adding performance tweaks..."
echo "isolcpus=3" | sudo tee -a /boot/firmware/cmdline.txt
echo "blacklist snd_bcm2835" | sudo tee -a /etc/modprobe.d/blacklist-rgb-matrix.conf
sudo update-initramfs -u

echo "Installing the repository..."
git clone --recurse-submodules https://github.com/MorganKryze/Athunas.git && cd Athunas