#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/common.lib"

# Initialize the pyut


# Check for available Python binary
get_PYTHON_BINARYary() {
    local PYTHON_BINARY=""
    if command -v python &> /dev/null; then
        PYTHON_BINARY="python"
    elif command -v python3 &> /dev/null; then
        PYTHON_BINARY="python3"
    else
        print_error "No Python interpreter found."
        return 1
    fi
    echo "$PYTHON_BINARY"
}

update_json_with_python_binary() {
    # Retrieve data_dir from the JSON configuration file
    data_dir=$(jq -r '.data_dir' "$SRV_CFG_FILE")

    if [ -z "$data_dir" ]; then
        print_error "data_dir not found in $SRV_CFG_FILE"
        return 1
    fi

    if [ -f "$SRV_CFG_FILE" ]; then
        tmp_file=$(mktemp)
        jq --arg bin "$PYTHON_BINARY" '.python_binary = $bin' "$SRV_CFG_FILE" > "$tmp_file" && mv "$tmp_file" "$SRV_CFG_FILE"
        print_debug "Updated $SRV_CFG_FILE with python_binary: $PYTHON_BINARY"

        # Save the updated JSON to $data_dir/static/service_config.json
        mkdir -p "$data_dir/static"
        run_or_sudo cp "$SRV_CFG_FILE" "$data_dir/static/service_config.json"
        print_debug "Updated $data_dir/static/service_config.json with python_binary: $PYTHON_BINARY"
    else
        print_error "JSON configuration file not found: $SRV_CFG_FILE"
        return 1
    fi
}

build_venv() {
    VENV_DIR=$(jq -r '.venv_dir' "$SRV_CFG_FILE")

    if [ ! -d "$VENV_DIR/bin" ]; then
        run_or_sudo $PYTHON_BINARY -m venv "$VENV_DIR" || exit_error "Failed to create virtual environment in $VENV_DIR"
        if ! source "$VENV_DIR/bin/activate"; then
            print_error "Failed to activate virtual environment in $VENV_DIR"
            return 1
        fi
    else
        if ! source "$VENV_DIR/bin/activate"; then
            print_error "Failed to activate virtual environment in $VENV_DIR"
            return 1
        fi
    fi
}


main() {
    print_title "Building Python Virtual Environment..."

    # Find the Python Binary
    print_info "Finding Python Binary..."
    PYTHON_BINARY=$(get_PYTHON_BINARYary)
    if [ $? -ne 0 ]; then
        print_error "Failed to restrict file permissions."
        exit 1
    fi
    print_success "File permissions restricted successfully."

    # Add python Binary to config files
    print_info "Updating Config Files with python binary name"
    update_json_with_python_binary
    if [ $? -ne 0 ]; then
        print_error "Failed to update Config Files."
        exit 1
    fi
    print_success "Config Files Updated."

    # Build Venv
    print_info "Building Venv"
    build_venv
    if [ $? -ne 0 ]; then
        print_error "Failed to build Venv."
        exit 1
    fi
    print_success "Venv Built Successfully."
}

