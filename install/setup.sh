#!/bin/bash

# This is the development setup script. the installer will run this,
# it's just the bare minimum setup needed to get the project working
SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/common.lib"\

# Set verbosity level
AESOP_SETUP_VERBOSITY=1
if [ "$1" == "-v" ]; then
    AESOP_SETUP_VERBOSITY=2
elif [ "$1" == "-q" ]; then
    AESOP_SETUP_VERBOSITY=0
fi
export AESOP_SETUP_VERBOSITY


# Script Intro
print_title "Setting Up Project Aesop..."

# Cache Sudo Creds
print_info "Requesting sudo access for installation..."
sudo echo "" >/dev/null
if [ $? -ne 0 ]; then
    exit_error "Sudo request failed. Exiting..."
fi

# Make all scripts executable
print_info "Making scripts exectuable...\n"
chmod +x "$SCRIPT_DIR/"*.sh


# Install Dependencies
bash "$SCRIPT_DIR"/install_dependencies.sh
if [ $? -ne 0 ]; then
    exit_error "Failed to install Dependencies."
fi


# Generate App Environment Structure
echo -e "\n"
bash "$SCRIPT_DIR"/build_app_environment.sh
if [ $? -ne 0 ]; then
    exit_error "Failed to generate app environment."
fi



