#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/common.lib"

VENV_DIR=$(jq -r '.venv_dir' "$SRV_CFG_FILE")

if [ ! -d "$VENV_DIR/bin" ]; then
    python -m venv "$VENV_DIR" || exit_error "Failed to create virtual environment in $VENV_DIR"
    source "$VENV_DIR/bin/activate" || exit_error "Failed to activate virtual environment in $VENV_DIR"
else
    source "$VENV_DIR/bin/activate" || exit_error "Failed to activate virtual environment in $VENV_DIR"
fi