#!/bin/bash

# This is the development setup script. the installer will run this,
# is just the bare minimum setup needed to get the project working

# Constants
SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Install Dependencies
$SCRIPT_DIR/install_dependencies.sh

# ToDo Get directory paths


## Create and activate python venv
#if [ ! -d "venv" ] ; then
#    python -m venv venv
#    source env/bin/activate
#else
#    source env/bin/activate
#fi

