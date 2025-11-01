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
set -o errexit
set -o pipefail
trap cleanup EXIT

# ===== Function definitions =====
function cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "Script exited with error code $exit_code."
    fi
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
    txt "This script will setup the environement, docker and the project on the target device."
    sleep $LOW_DELAY
    txt "Please report any issue at ${LINK}${UNDERLINE}${ISSUES_URL}${RESET}."
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
    info "Setting up the OS packages..."

    info "Updating package list..."
    sudo apt-get update

    info "Checking for upgradable packages..."
    local upgradable=$(apt list --upgradable 2>/dev/null | grep -c upgradable || true)
    if [ "$upgradable" -gt 1 ]; then
        info "Upgrading $((upgradable - 1)) packages..."
    sudo apt-get upgrade -y
    else
        info "System is up to date."
    fi

    info "Installing required packages..."
    local packages="git python3-pip python3-venv make build-essential libsixel-dev python3-tk cython3 libcap2-bin"
    local to_install=""
    
    for pkg in $packages; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            to_install="$to_install $pkg"
        fi
    done
    
    if [ -n "$to_install" ]; then
        sudo apt-get install -y --no-install-recommends $to_install
    sudo apt-get clean
        success "Installed packages:$to_install"
    else
        info "All required packages already installed."
    fi

    success "OS setup complete."
    sleep $LOW_DELAY
}

function install_docker() {
    info "Checking Docker installation..."

    if command -v docker >/dev/null 2>&1; then
        local docker_version=$(docker --version)
        info "Docker already installed: $docker_version"
        
        if docker compose version >/dev/null 2>&1; then
            info "Docker Compose plugin already installed."
        else
            warning "Docker Compose plugin not found, will install..."
        fi
    else
        info "Docker not found. Installing Docker..."

        info "Installing prerequisites..."
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl
        
        info "Adding Docker's official GPG key..."
    sudo install -m 0755 -d /etc/apt/keyrings
        if [ ! -f /etc/apt/keyrings/docker.asc ]; then
    sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
        else
            info "Docker GPG key already exists."
        fi

    info "Adding Docker repository to APT sources..."
        if [ ! -f /etc/apt/sources.list.d/docker.list ]; then
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
        else
            info "Docker repository already configured."
        fi
    
    info "Installing Docker Engine, CLI, and Containerd..."
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    fi

    info "Setting up Docker permissions..."
    if groups $USER | grep -q '\bdocker\b'; then
        info "User '$USER' is already in the 'docker' group."
    else
        info "Adding user '$USER' to the 'docker' group..."
        sudo usermod -aG docker $USER
        warning "Group changes will take effect after logout/login or system reboot."
    fi

    info "Ensuring Docker service is enabled and running..."
    sudo systemctl enable docker
    sudo systemctl start docker
    
    if sudo systemctl is-active --quiet docker; then
        success "Docker service is running."
    else
        warning "Docker service is not running. Check with: sudo systemctl status docker"
    fi

    success "Docker installation complete."
    sleep $LOW_DELAY
}

function performance_tweaks() {
    info "Applying performance tweaks..."

    info "Checking CPU isolation configuration..."
    local cmdline_file=""
    
    if [ -f /boot/firmware/cmdline.txt ]; then
        cmdline_file="/boot/firmware/cmdline.txt"
    elif [ -f /boot/cmdline.txt ]; then
        cmdline_file="/boot/cmdline.txt"
    else
        warning "cmdline.txt not found. Skipping CPU isolation."
    fi
    
    if [ -n "$cmdline_file" ]; then
        if grep -q "isolcpus=3" "$cmdline_file"; then
            info "CPU core 3 already isolated in $cmdline_file"
        else
            info "Isolating CPU core 3..."
            sudo cp "$cmdline_file" "${cmdline_file}.bak.$(date +%Y%m%d_%H%M%S)"
            sudo sed -i '$ s/$/ isolcpus=3/' "$cmdline_file"
            success "CPU core 3 isolated in $cmdline_file (requires reboot)"
        fi
    fi

    info "Checking sound module blacklist..."
    local blacklist_file="/etc/modprobe.d/blacklist-rgb-matrix.conf"
    
    if [ -f "$blacklist_file" ] && grep -q "blacklist snd_bcm2835" "$blacklist_file"; then
        info "snd_bcm2835 already blacklisted"
    else
        info "Blacklisting snd_bcm2835 module..."
        echo "blacklist snd_bcm2835" | sudo tee "$blacklist_file" > /dev/null
        success "snd_bcm2835 module blacklisted (requires reboot)"
    fi

    info "Updating initramfs..."
    if command -v update-initramfs >/dev/null 2>&1; then
        sudo update-initramfs -u
        success "initramfs updated"
    else
        warning "update-initramfs not found, skipping..."
    fi

    success "Performance tweaks applied."
    sleep $LOW_DELAY
}

function setup_project() {
    info "Setting up the project..."

    local project_dir="$HOME/$REPOSITORY_NAME"
    
    if [ -d "$project_dir" ]; then
        info "Project directory already exists at $project_dir"
        info "Updating repository..."
        cd "$project_dir"
        
        if [ -d .git ]; then
            git fetch origin
            local_commit=$(git rev-parse HEAD)
            remote_commit=$(git rev-parse origin/main 2>/dev/null || git rev-parse origin/master 2>/dev/null)
            
            if [ "$local_commit" = "$remote_commit" ]; then
                info "Repository is already up to date."
            else
                warning "Local repository differs from remote. Run 'git pull' manually to update."
            fi
            
            if [ -f .gitmodules ]; then
                info "Updating submodules..."
                git submodule update --init --recursive
            fi
        else
            warning "Directory exists but is not a git repository. Skipping update."
        fi
    else
    info "Cloning the repository..."
        cd "$HOME"
    git clone --recurse-submodules "$REPOSITORY_URL"
        cd "$REPOSITORY_NAME"
        success "Repository cloned to $project_dir"
    fi

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