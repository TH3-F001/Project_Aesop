#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/common.lib"

# Initialize the pyut


# Check for available Python binary
get_python_binary() {
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

        # Update the JSON file with the python_binary value
        if ! jq --arg bin "$PYTHON_BINARY" '.python_binary = $bin' "$SRV_CFG_FILE" > "$tmp_file"; then
            print_error "Failed to update $SRV_CFG_FILE with python_binary"
            return 1
        fi

        if ! mv "$tmp_file" "$SRV_CFG_FILE"; then
            print_error "Failed to move temporary file to $SRV_CFG_FILE"
            return 1
        fi

        print_debug "Updated $SRV_CFG_FILE with python_binary: $PYTHON_BINARY"

        # Save the updated JSON to $data_dir/static/service_config.json
        mkdir -p "$data_dir/static"
        if ! run_or_sudo cp "$SRV_CFG_FILE" "$data_dir/static/service_config.json"; then
            print_error "Failed to copy $SRV_CFG_FILE to $data_dir/static/service_config.json"
            return 1
        fi

        print_debug "Updated $data_dir/static/service_config.json with python_binary: $PYTHON_BINARY"
    else
        print_error "JSON configuration file not found: $SRV_CFG_FILE"
        return 1
    fi
}


retrive_json_config_data() {
    SRV_SECRETS_DIR=$(jq -r '.secrets_dir' "$SRV_CFG_FILE")
    SRV_OUTPUT_DIR=$(jq -r '.output_dir' "$SRV_CFG_FILE")
    SRV_LOG_DIR=$(jq -r '.log_dir' "$SRV_CFG_FILE")
    SRV_DATA_DIR=$(jq -r '.data_dir' "$SRV_CFG_FILE")
    SRV_TEMP_DIR=$(jq -r '.temp_dir' "$SRV_CFG_FILE")
    SRV_VENV_DIR=$(jq -r '.venv_dir' "$SRV_CFG_FILE")
    SRV_SRC_DIR=$(jq -r '.src_dir' "$SRV_CFG_FILE")
    SRV_TESTS_DIR=$(jq -r '.tests_dir' "$SRV_CFG_FILE")
    SRV_INSTALL_DIR=$(jq -r '.install_dir' "$SRV_CFG_FILE")
    SRV_INSTALL_DIR=$(jq -r '.assets_dir' "$SRV_CFG_FILE")
    SRV_USRGRP=$(jq -r '.service_usergroup' "$SRV_CFG_FILE")
    USR_OUTPUT_DIR=$(jq -r '.output_dir' "$USR_CFG_FILE")
    USR_LOG_DIR=$(jq -r '.log_dir' "$USR_CFG_FILE")
    USR_DATA_DIR=$(jq -r '.data_dir' "$USR_CFG_FILE")
}

add_environment_vars_to_venv() {
    {
        echo "export SRV_SECRETS_DIR=\"$SRV_SECRETS_DIR\""
        echo "export SRV_OUTPUT_DIR=\"$SRV_OUTPUT_DIR\""
        echo "export SRV_LOG_DIR=\"$SRV_LOG_DIR\""
        echo "export SRV_DATA_DIR=\"$SRV_DATA_DIR\""
        echo "export SRV_TEMP_DIR=\"$SRV_TEMP_DIR\""
        echo "export SRV_VENV_DIR=\"$SRV_VENV_DIR\""
        echo "export SRV_SRC_DIR=\"$SRV_SRC_DIR\""
        echo "export SRV_TESTS_DIR=\"$SRV_TESTS_DIR\""
        echo "export SRV_INSTALL_DIR=\"$SRV_INSTALL_DIR\""
        echo "export SRV_ASSETS_DIR=\"$SRV_ASSETS_DIR\""
        echo "export SRV_USRGRP=\"$SRV_USRGRP\""
        echo "export PYTHON_BINARY=\"$PYTHON_BINARY\""
    } >> "$VENV_DIR/bin/activate"
}



build_venv() {
    VENV_DIR=$(jq -r '.venv_dir' "$SRV_CFG_FILE")
    retrive_json_config_data 2>/dev/null

    if [ ! -d "$VENV_DIR/bin" ]; then
        run_or_sudo $PYTHON_BINARY -m venv "$VENV_DIR" >/dev/null 2>&1 || { print_error "Failed to create virtual environment in $VENV_DIR"; return 1; }
    fi
    sudo chown -R "$(whoami)":"$SRV_USRGRP" "$VENV_DIR" >/dev/null 2>&1

    source "$VENV_DIR/bin/activate" || { print_error "Failed to activate virtual environment in $VENV_DIR"; return 1; }
    add_environment_vars_to_venv 2>/dev/null
}





main() {
    print_title "Building Python Virtual Environment..."

    # Find the Python Binary
    print_info "Finding Python Binary..."
    PYTHON_BINARY=$(get_python_binary)
    if [ $? -ne 0 ]; then
        print_error "Failed to restrict file permissions."
        exit 1
    fi
    print_success "File permissions restricted successfully."

    # Add python Binary to config files
    print_info "\nUpdating Config Files with python binary name..."
    update_json_with_python_binary >/dev/null
    if [ $? -ne 0 ]; then
        print_error "Failed to update Config Files."
        exit 1
    fi
    print_success "Config Files Updated."

    # Build Venv
    print_info "\nBuilding Venv..."
    build_venv
    if [ $? -ne 0 ]; then
        print_error "Failed to build Venv."
        exit 1
    fi
    print_success "Venv Built Successfully."
}

main