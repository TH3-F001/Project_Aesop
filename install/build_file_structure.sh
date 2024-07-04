#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/print.lib"
source "$SCRIPT_DIR/filepaths.lib"

SERVICE_USER=""
BUILD_DIRS=()

# Function to log debug messages


# jq is needed to read our json files
check_jq_installed(){
    print_debug "Checking if jq is installed..."
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Please install jq to proceed."
        exit 1
    fi
    print_debug "jq is installed."
}

# Evaluate JSON value with environment variable substitution
eval_json_value() {
    local json_file=$1
    local key=$2
    local value
    print_debug "Evaluating JSON value for key '$key' in file '$json_file'..."
    value=$(jq -r "$key" "$json_file")
    eval echo "$value"
}

# Check if templates directory exists
check_templates_exists(){
    print_debug "Checking if templates directory '$TEMPLATES_DIR' exists..."
    if [ ! -d "$TEMPLATES_DIR" ]; then
        print_error "$TEMPLATES_DIR does not exist or is not a directory. This shouldnt happen. Maybe check the repo?"
        exit 1
    fi
    print_debug "Templates directory exists."
}

retrieve_json_directories() {
    print_debug "Retrieving JSON directories..."
    local build_cfg_files=("$SRV_CFG_FILE" "$USR_USR_CFG_FILE")

    # Get all directory values from json config files
    for cfg_file in "${build_cfg_files[@]}"; do
        print_debug "Processing config file '$cfg_file'..."
        for key in $(jq -r 'keys[]' "$cfg_file"); do
            if [[ "$key" == *_dir ]]; then
                value=$(jq -r --arg key "$key" '.[$key]' "$cfg_file")
                BUILD_DIRS+=("$value")
                print_debug "Found directory key '$key' with value '$value'."
            fi
        done
    done
    print_debug "Retrieved JSON directories: ${BUILD_DIRS[*]}"
}

build_base_directories() {
    print_debug "Building base directories..."
    for dir in "${BUILD_DIRS[@]}"; do
        mkdir -p "$dir"
        print_debug "Created directory: $dir"
    done
}

# Recursively copy files, while removing "_template" from the destination filename
recursive_copy() {
    local src_dir=$1
    local dest_dir=$2

    print_debug "Starting recursive copy from '$src_dir' to '$dest_dir'..."
    find "$src_dir" -type f | while read -r template; do
        local relative_path="${template#$src_dir/}"
        local new_filename="${relative_path/_template.json/.json}"
        new_filename="${new_filename/_template.txt/.txt}"
        local new_filepath="$dest_dir/$new_filename"
        local new_filepath_dir=$(dirname "$new_filepath")

        mkdir -p "$new_filepath_dir" || sudo mkdir -p "$new_filepath_dir"
        print_debug "Created directory: $new_filepath_dir"

        if [[ ! -f "$new_filepath" ]]; then
            print_info "\tCopying $template to $new_filepath"
            cp "$template" "$new_filepath" || sudo cp "$template" "$new_filepath"
            print_debug "Copied $template to $new_filepath"
        else
            print_info "\t$new_filepath already exists, skipping."
            print_debug "File $new_filepath already exists, skipping."
        fi
    done
}

# !IMPORTANT the templates dir should always have the same child folders that data has.
# This makes things easy to code, and easy to visualize... is what im saying right now.
# Very possible that im just lazy and hate looking at bash.
# Very possible that im just lazy and hate looking at bash.
copy_templates() {
    print_debug "Copying templates from '$TEMPLATES_DIR'..."
    for dir in "$TEMPLATES_DIR"/*; do
        if [ -d "$dir" ]; then
            dir_name=$(basename "$dir")
            print_debug "Processing template directory: $dir_name"

            case "$dir_name" in
                dynamic)
                    print_info "DYNAMIC_TEMPLATES:"
                    recursive_copy "$dir" "$SRV_DATA_DIR/dynamic"
                    ;;
                secrets)
                    print_info "SECRETS_TEMPLATES:"
                    recursive_copy "$dir" "$SRV_SECRETS_DIR"
                    ;;
                static)
                    print_info "STATIC_TEMPLATES:"
                    recursive_copy "$dir" "$SRV_DATA_DIR/static"
                    ;;
                *)
                    print_warning "unexpected templates directory: $dir_name"
                    ;;
            esac
        fi
    done
}

# I know we're going to need it later so may as well code it now
create_SERVICE_USER_and_group() {
    print_debug "Creating service user and group..."
    local current_user=$(whoami)
    SERVICE_USER=$(eval_json_value '.SERVICE_USERgroup')
    sudo adduser --system --user-group --no-create-home $SERVICE_USER
    sudo usermod -aG "$SERVICE_USER" "$current_user"
    print_info "Service user '$SERVICE_USER' created, and current user '$current_user' added to the group '$SERVICE_USER'."
    print_debug "Service user '$SERVICE_USER' created, and current user '$current_user' added to the group '$SERVICE_USER'."
}

# Set standard data files to rw-r-----
# Set secrets to rw-------
restrict_file_permissions() {
    print_debug "Restricting file permissions..."
    local user=$(whoami)

    # Ensure both the current user and the service user group have access to the required directories and set appropriate permissions

    chown -R "$user":"$SERVICE_USER" "$SRV_SECRETS_DIR"
    find "$SRV_SECRETS_DIR" -type f -exec chmod 640 {} \; # rw-r-----
    find "$SRV_SECRETS_DIR" -type d -exec chmod 750 {} \; # rwxr-x---

    chown -R "$user":"$SERVICE_USER" "$SRV_OUTPUT_DIR"
    find "$SRV_OUTPUT_DIR" -type f -exec chmod 660 {} \; # rw-rw----
    find "$SRV_OUTPUT_DIR" -type d -exec chmod 770 {} \; # rwxrwx---

    chown -R "$user":"$SERVICE_USER" "$SRV_LOG_DIR"
    find "$SRV_LOG_DIR" -type f -exec chmod 660 {} \; # rw-rw----
    find "$SRV_LOG_DIR" -type d -exec chmod 770 {} \; # rwxrwx---

    chown -R "$user":"$SERVICE_USER" "$SRV_DATA_DIR"
    find "$SRV_DATA_DIR" -type f -exec chmod 640 {} \; # rw-r-----
    find "$SRV_DATA_DIR" -type d -exec chmod 750 {} \; # rwxr-x---
    print_info "Set ownership and permissions for all service directories."
    print_debug "Set ownership and permissions for all service directories."
}

link_user_directories() {
    print_debug "Linking user directories..."
    local user=$(whoami)
    ln -sf "$SRV_OUTPUT_DIR" "$USR_OUTPUT_DIR"
    ln -sf "$SRV_LOG_DIR" "$USR_LOG_DIR"
    ln -sf "$SRV_DATA_DIR" "$USR_DATA_DIR"

    print_info "Linked service directories to user directories."
    print_debug "Linked service directories to user directories."
}

debug_json_data() {
    print_debug "JSON data:\n\tSRV_SECRETS_DIR=$SRV_SECRETS_DIR\n\tSRV_OUTPUT_DIR=$SRV_OUTPUT_DIR\n\tSRV_LOG_DIR=$SRV_LOG_DIR\n\tSRV_DATA_DIR=$SRV_DATA_DIR"
}

main() {
    print_debug "Starting script execution..."
    check_jq_installed
    retrieve_json_directories
    check_templates_exists
    build_base_directories
    copy_templates
    restrict_file_permissions
    link_user_directories
    print_debug "Script execution completed."
}

main
