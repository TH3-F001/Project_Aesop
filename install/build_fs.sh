#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/common.lib"

SERVICE_USER=""
BUILD_DIRS=()

print_title "Entering build_fs.sh script"

# jq is needed to read our json files
check_jq_installed() {
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Please install jq to proceed."
        return 1
    fi
}

# Evaluate JSON value with environment variable substitution
eval_json_value() {
    local json_file=$1
    local key=$2
    local value

    print_debug "Checking if JSON file '$json_file' exists..."

    if [ ! -f "$json_file" ]; then
        print_error "JSON file '$json_file' does not exist. Please check the file path."
        return 1
    fi

    print_debug "Evaluating JSON value for key '$key' in file '$json_file'..."
    value=$(run_or_sudo jq -r "$key" "$json_file")
    eval echo "$value"
}

# Check if templates directory exists
check_templates_exist() {
    print_debug "Templates Dire: $TEMPLATES_DIR"
    if [ ! -d "$TEMPLATES_DIR" ]; then
        print_error "$TEMPLATES_DIR does not exist or is not a directory. This shouldn't happen. Maybe check the repo?"
        return 1
    fi

}

retrieve_json_directories() {
    local build_cfg_files=("$SRV_CFG_FILE" "$USR_CFG_FILE")
    print_debug "Build Config Files: ${build_cfg_files[*]}"

    declare -A dirs=(
        ["SRV_SECRETS_DIR"]=".secrets_dir"
        ["SRV_OUTPUT_DIR"]=".output_dir"
        ["SRV_LOG_DIR"]=".log_dir"
        ["SRV_DATA_DIR"]=".data_dir"
    )

    retrieve_dir() {
        local var_name=$1
        local jq_filter=$2
        local config_file=$3

        local dir=$(run_or_sudo jq -r "$jq_filter" "$config_file")
        if [ $? -ne 0 ] || [ -z "$dir" ]; then
            print_error "Failed to retrieve '$jq_filter' from $config_file"
            return 1
        fi
        eval "$var_name=\"$dir\""
        print_debug "Initialized $var_name=$dir"
    }

    for var_name in "${!dirs[@]}"; do
        retrieve_dir "$var_name" "${dirs[$var_name]}" "$SRV_CFG_FILE" || return 1
    done

    for cfg_file in "${build_cfg_files[@]}"; do
        print_debug "Processing config file '$cfg_file'..."
        local keys=$(run_or_sudo jq -r 'keys[]' "$cfg_file")
        if [ $? -ne 0 ]; then
            print_error "Failed to retrieve keys from $cfg_file"
            return 1
        fi

        for key in $keys; do
            if [[ "$key" == *_dir ]]; then
                value=$(run_or_sudo jq -r --arg key "$key" '.[$key]' "$cfg_file")
                if [ $? -ne 0 ]; then
                    print_error "Failed to retrieve value for key '$key' from $cfg_file"
                    return 1
                fi
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
        run_or_sudo mkdir -p $dir >/dev/null
        if [ $? -eq 0 ]; then
            print_debug "Created directory: $dir"
        else
            print_error "Failed to Build Directory: $dir"
            return 1
        fi
    done
}

recursive_copy() {
    local src_dir=$1
    local dest_dir=$2

    print_debug "Copying file structure from '$src_dir' to '$dest_dir'..."

    # Check if source and destination directories exist
    if [[ ! -d "$src_dir" ]]; then
        print_error "Source directory '$dir' does not exist."
        return 1
    fi


    # Function to create directories and copy files
    copy_file() {
        local source_file=$1
        local relative_path="${source_file#$src_dir/}"
        local new_filename="${relative_path/_template.json/.json}"
        new_filename="${new_filename/_template.txt/.txt}"
        local new_filepath="$dest_dir/$new_filename"
        local new_filepath_dir=$(dirname "$new_filepath")

        run_or_sudo mkdir -p "$new_filepath_dir" >/dev/null || {
            print_error "Failed to create directory: $new_filepath_dir"
            return 1
        }
        print_debug "Created directory: $new_filepath_dir"

        if [[ ! -f "$new_filepath" ]]; then
            print_debug "Copying $source_file to $new_filepath"
            run_or_sudo cp "$source_file" "$new_filepath" >/dev/null || {
                print_error "Failed to copy $source_file to $new_filepath"
                return 1
            }
            print_debug "Copied $source_file to $new_filepath"
        else
            print_debug "File $new_filepath already exists, skipping."
        fi
    }

    # Find and process files
    find "$src_dir" -type f | while read -r source_file; do
        [[ -z "$source_file" ]] && {
            print_error "Error reading source file path."
            return 1
        }
        copy_file "$source_file"
    done
}

copy_templates() {
    print_debug "Copying templates from '$TEMPLATES_DIR'..."

    if [[ ! -d "$TEMPLATES_DIR" ]]; then
        print_error "Templates directory '$TEMPLATES_DIR' does not exist."
        return 1
    fi

    local destinations=(
        [dynamic]="$SRV_DATA_DIR/dynamic"
        [secrets]="$SRV_SECRETS_DIR"
        [static]="$SRV_DATA_DIR/static"
    )

    for dir in "$TEMPLATES_DIR"/*; do
        if [[ -d "$dir" ]]; then
            dir_name=$(basename "$dir")
            print_debug "Processing template directory: $dir_name"

            if [[ -n ${destinations[$dir_name]} ]]; then
                print_debug "${dir_name^^}_TEMPLATES:"
                recursive_copy "$dir" "${destinations[$dir_name]}"
                if [[ $? -ne 0 ]]; then
                    print_error "Failed to copy $dir_name templates from $dir to ${destinations[$dir_name]}"
                    return 1
                fi
            else
                print_warning "Unexpected templates directory: $dir_name"
            fi
        else
            print_warning "Skipping non-directory item: $dir"
        fi
    done
}


create_service_user_and_group() {
    print_debug "Creating service user and group..."

    local current_user=$(whoami)
    if [[ $? -ne 0 ]]; then
        print_error "Failed to get the current user."
        return 1
    fi

    SERVICE_USER=$(eval_json_value '.SERVICE_USERgroup')
    if [[ $? -ne 0 ]]; then
        print_error "Failed to evaluate SERVICE_USER from JSON."
        return 1
    fi

    if ! sudo adduser --system --user-group --no-create-home $SERVICE_USER; then
        print_error "Failed to add service user '$SERVICE_USER'."
        return 1
    fi

    if ! sudo usermod -aG "$SERVICE_USER" "$current_user"; then
        print_error "Failed to add current user '$current_user' to group '$SERVICE_USER'."
        return 1
    fi

    print_debug "Service user '$SERVICE_USER' created, and current user '$current_user' added to the group '$SERVICE_USER'."
}


restrict_file_permissions() {
    print_debug "Restricting file permissions..."
    local user=$(whoami)
    if [[ $? -ne 0 ]]; then
        print_error "Failed to determine the current user."
        return 1
    fi

    change_permissions() {
        local dir=$1
        local file_perms=$2
        local dir_perms=$3

        run_or_sudo chown -R "$user":"$SERVICE_USER" "$dir"  >/dev/null
        if [[ $? -ne 0 ]]; then
            print_error "Failed to change ownership for $dir."
            return 1
        fi

        run_or_sudo find "$dir" -type f -exec chmod "$file_perms" {} \; >/dev/null
        if [[ $? -ne 0 ]]; then
            print_error "Failed to set file permissions for $dir."
            return 1
        fi

        run_or_sudo find "$dir" -type d -exec chmod "$dir_perms" {} \; >/dev/null
        if [[ $? -ne 0 ]]; then
            print_error "Failed to set directory permissions for $dir."
            return 1
        fi
    }

    change_permissions "$SRV_SECRETS_DIR" 640 750 || return 1
    change_permissions "$SRV_OUTPUT_DIR" 660 770 || return 1
    change_permissions "$SRV_LOG_DIR" 660 770 || return 1
    change_permissions "$SRV_DATA_DIR" 640 750 || return 1

    print_debug "Set ownership and permissions for all service directories."
}


link_user_directories() {
    local user=$(whoami)
    if [[ $? -ne 0 ]]; then
        print_error "Failed to determine the current user."
        return 1
    fi

    link_directory() {
        local src_dir=$1
        local dest_dir=$2
        run_or_sudo ln -sf "$src_dir" "$dest_dir" >/dev/null
        if [[ $? -ne 0 ]]; then
            print_error "Failed to link $src_dir to $dest_dir."
            return 1
        fi
    }

    link_directory "$SRV_OUTPUT_DIR" "$USR_OUTPUT_DIR" || return 1
    link_directory "$SRV_LOG_DIR" "$USR_LOG_DIR" || return 1
    link_directory "$SRV_DATA_DIR" "$USR_DATA_DIR" || return 1

    print_debug "Linked service directories to user directories."
}


main() {
    print_title "Building Project FileStructure..."

    # Check for jq
    print_info "Checking if jq is installed..."
    check_jq_installed
    if [ $? -ne 0 ]; then
        exit_error "jq check failed."
        exit 1
    fi
    print_success "jq check completed successfully."

    # Get directories from build_configs
    print_info "Retrieving JSON directories..."
    retrieve_json_directories
    if [ $? -ne 0 ]; then
        exit_error "Failed to retrieve JSON directories."
        exit 1
    fi
    print_success "JSON directories retrieved successfully."

    # Make sure the templates exist
    print_info "Checking if templates directory exists..."
    check_templates_exist
    if [ $? -ne 0 ]; then
        exit_error "Templates Directory Doesnt exist."
        exit 1
    fi
    print_success "Templates Directory Exists."

    # Build the base directory structure
    print_info "Building base directories..."
    build_base_directories
    if [ $? -ne 0 ]; then
        print_error "Failed to build base directories."
        exit 1
    fi
    print_success "Base directories built successfully."

    # Copy templates into the new directory structure
    print_info "Copying templates..."
    copy_templates
    if [ $? -ne 0 ]; then
        print_error "Failed to copy templates."
        exit 1
    fi
    print_success "Templates copied successfully."

    # Restrict file permissions for service level assets
    print_info "Restricting file permissions..."
    restrict_file_permissions
    if [ $? -ne 0 ]; then
        print_error "Failed to restrict file permissions."
        exit 1
    fi
    print_success "File permissions restricted successfully."

    # Link service files to user's home config folder
    print_info "Linking user directories..."
    link_user_directories
    if [ $? -ne 0 ]; then
        print_error "Failed to link user directories."
        exit 1
    fi
    print_success "User directories linked successfully."

    print_debug "Script execution completed."
    print_success "All operations in build_fs.sh completed successfully!"
}

main
