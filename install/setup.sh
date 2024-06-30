#!/bin/bash

# This is the development setup script. the installer will run this,
# it's just the bare minimum setup needed to get the project working


SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/colors.lib"

# Script Intro
echo -e "Setting Up Project Aesop...${NC}"

# Cache Sudo Creds
echo -e "${CYAN} \tRequesting sudo access for installation:${NC}"
sudo echo "" >/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED} \t\tSudo request failed. Exiting...${NC}"
    exit 1
fi

# Relative Directories
echo -e "${NC}\tGetting Relative FilePaths..."
PROJECT_DIR=$(dirname "$SCRIPT_DIR")
BUILD_CFG_PATH="$PROJECT_DIR/data/config/"
echo -e "${GREEN}\t\tDone!${NC}"


# Install Dependencies
echo -e "${NC}\tInstalling Dependencies..."
$SCRIPT_DIR/install_dependencies.sh
if [ $? -ne 0 ]; then
  echo -e "${RED}Error: Failed to install Dependencies.${NC}"
fi


# Get directory paths


## Create and activate python venv
#if [ ! -d "venv" ] ; then
#    python -m venv venv
#    source env/bin/activate
#else
#    source env/bin/activate
#fi

