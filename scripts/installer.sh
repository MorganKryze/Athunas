#!/bin/bash

# ===== Constants =====
VERSION="0.0.0"
LOW_DELAY=0.5
HIGH_DELAY=15
TOOLBOX_URL="https://raw.githubusercontent.com/MorganKryze/bash-toolbox/main/src/prefix.sh"
PROJECT_URL="https://github.com/MorganKryze/Athunas"
REPOSITORY_NAME="Athunas"
REPOSITORY_URL="https://github.com/MorganKryze/Athunas.git"
ISSUES_URL="https://github.com/MorganKryze/Athunas/issues"


# ===== Error handling =====
set -o errexit  # Exit on errorC
set -o pipefail # Exit if any command in a pipe fails
trap cleanup EXIT

# ===== Function definitions =====
function cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "Script exited with error code $exit_code."
    fi
    # TODO: Add any cleanup commands here if needed
    return $exit_code
}

function load_logging_toolbox() {
    if ! source <(curl -s --connect-timeout 10 "$TOOLBOX_URL"); then
        GREEN='\033[0;32m'
        BLUE='\033[0;34m'
        RED='\033[0;31m'
        ORANGE='\033[0;33m'
        RESET='\033[0m'
        LINK='\033[0;36m'
        UNDERLINE='\033[4m'

        function txt() { echo -e "${RESET}$1"; }
        function info() { txt "[${BLUE}  INFO   ${RESET}] ${BLUE}$1${RESET}"; }
        function warning() { txt "[${ORANGE} WARNING ${RESET}] ${ORANGE}$1${RESET}" >&2; }
        function error() {
            txt "[${RED}  ERROR  ${RESET}] ${RED}$1${RESET}" >&2
            return 1
        }
        function success() { txt "[${GREEN} SUCCESS ${RESET}] ${GREEN}$1${RESET}"; }

        warning "Failed to load logging toolbox. Falling back to self-defined functions."
    fi
}

function display_header() {
    txt '                                                                                                                                    '
    txt '    ,o888888o.           .8.          8 888888888o.      ,o888888o.     8 8888      88    d888888o.   8 8888888888   8 8888         '
    txt '   8888     `88.        .888.         8 8888    `88.  . 8888     `88.   8 8888      88  .`8888:'"'"' `88. 8 8888         8 8888         '
    txt ',8 8888       `8.      :88888.        8 8888     `88 ,8 8888       `8b  8 8888      88  8.`8888.   Y8 8 8888         8 8888         '
    txt '88 8888               . `88888.       8 8888     ,88 88 8888        `8b 8 8888      88  `8.`8888.     8 8888         8 8888         '
    txt '88 8888              .8. `88888.      8 8888.   ,88'"'"' 88 8888         88 8 8888      88   `8.`8888.    8 888888888888 8 8888         '
    txt '88 8888             .8`8. `88888.     8 888888888P'"'"'  88 8888         88 8 8888      88    `8.`8888.   8 8888         8 8888         '
    txt '88 8888            .8'"'"' `8. `88888.    8 888`8b       88 8888        ,8P 8 8888      88     `8.`8888.  8 8888         8 8888         '
    txt '`8 8888       .8'"'"' .8'"'"'   `8. `88888.   8 8888 `8b.    `8 8888       ,8P  ` 8888     ,8P 8b   `8.`8888. 8 8888         8 8888         '
    txt '   8888     ,88'"'"' .888888888. `88888.  8 8888   `8b.   ` 8888     ,88'"'"'     8888   ,d8P  `8b.  ;8.`8888 8 8888         8 8888         '
    txt '    `8888888P'"'"'  .8'"'"'       `8. `88888. 8 8888     `88.    `8888888P'"'"'        `Y88888P'"'"'    `Y8888P ,88P'"'"' 8 888888888888 8 888888888888'

    sleep $LOW_DELAY
    txt
    txt "Open-source $REPOSITORY_NAME led matrix dashboard setup script v${VERSION}."
    sleep $LOW_DELAY
    txt "This script will setup the environement on the target device, setup docker and install the project."
    sleep $LOW_DELAY
    txt "If you encounter any issues, please report them at ${LINK}${UNDERLINE}${ISSUES_URL}${RESET}."
    sleep $LOW_DELAY
    txt "Licensed under the GNU GPL v3 License, Yann M. Vidamment © 2025."
    sleep $LOW_DELAY
    txt "Visit ${LINK}${UNDERLINE}${PROJECT_URL}${RESET} for more information."
    sleep $LOW_DELAY
    txt
    txt "=========================================================================================="
    txt
    sleep $LOW_DELAY
}

function setup_os() {
    info "Setting up the os packages..."

    info "Updating and upgrading packages..."
    sudo apt-get update
    sudo apt-get upgrade -y

    info "Installing required packages..."
    sudo apt-get install -y --no-install-recommends git python3-pip python3-venv make build-essential libsixel-dev python3-tk cython3 libcap2-bin
    sudo apt-get clean

    success "OS setup complete."
    sleep $LOW_DELAY
}

function install_docker() {
    info "Installing Docker..."

    info "Adding Docker's official GPG key and repository..."

    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    info "Adding Docker repository to APT sources..."
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    
    info "Installing Docker Engine, CLI, and Containerd..."
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    info "Setting up Docker permissions..."

    if groups $USER | grep &>/dev/null '\bdocker\b'; then
        info "User '$USER' is already in the 'docker' group."
    else
        info "Adding user '$USER' to the 'docker' group..."
        sudo usermod -aG docker $USER
        info "You may need to log out and log back in for the changes to take effect."
    fi

    success "Docker installation complete."
    sleep $LOW_DELAY
}

function performance_tweaks() {
    info "Applying performance tweaks..."

    info "Modifying cmdline.txt to isolate CPU core 3..."
    echo " isolcpus=3" | sudo tee -a /boot/firmware/cmdline.txt

    info "Blacklisting snd_bcm2835 module to free up resources..."
    echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf

    info "Updating initramfs..."
    sudo update-initramfs -u

    success "Performance tweaks applied."
    sleep $LOW_DELAY
}

function setup_project() {
    info "Setting up the project..."

    info "Cloning the repository..."
    git clone --recurse-submodules "$REPOSITORY_URL"
    cd $REPOSITORY_NAME

    success "Project setup complete."
    sleep $LOW_DELAY
}

function display_next_steps() {
    txt
    txt "Next steps:"
    txt "1. After the device reboots, log back in."
    txt "2. Navigate to the project directory: ${BLUE}cd ~/$REPOSITORY_NAME${RESET}"
    txt "3. Build and start the Docker containers: ${BLUE}docker compose up --build -d${RESET}"
    txt "4. Access the $REPOSITORY_NAME dashboard via your web browser at: ${LINK}${UNDERLINE}http://<device-ip>:8000${RESET}"
    txt

    sleep $LOW_DELAY
    warning "The device will reboot in $HIGH_DELAY seconds. Keep this terminal open to continue with the next steps after reboot."
    sleep $HIGH_DELAY
    sudo reboot now
}

# ===== Main script execution =====

function main() {
    load_logging_toolbox

    display_header

    setup_os

    install_docker

    performance_tweaks

    setup_project

    success "$REPOSITORY_NAME setup complete!"
    sleep $LOW_DELAY

    display_next_steps
}

main "$@"