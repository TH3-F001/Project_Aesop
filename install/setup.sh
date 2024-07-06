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
print_debug "Verbosity: $AESOP_SETUP_VERBOSITY"

# Script Intro
print_title "Setting Up Project Aesop...\n"

# Cache Sudo Creds
print_info "Requesting sudo access for installation..."
sudo echo "" >/dev/null
if [ $? -ne 0 ]; then
    exit_error "\tSudo request failed. Exiting..."
fi

# Make all scripts executable
print_info "\tMaking scripts exectuable..."
chmod +x "$SCRIPT_DIR/"*.sh


# Install Dependencies
print_info "\tInstalling Dependencies..."
$SCRIPT_DIR/install_dependencies.sh
if [ $? -ne 0 ]; then
    exit_error "Failed to install Dependencies."
fi


# Generate File Structure
print_info "\tGenerating File Structure..."
$SCRIPT_DIR/build_fs.sh
if [ $? -ne 0 ]; then
    exit_error "Failed to generate file structure."
fi


## Create and activate python venv
print_info "\tGenerating Python Virtual Environment..."
$SCRIPT_DIR/build_venv.sh
if [ $? -ne 0 ]; then
    exit_error "Failed to Generate Python Virtual Environment."
fi


