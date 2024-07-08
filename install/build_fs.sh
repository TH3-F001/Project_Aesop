#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/common.lib"

SERVICE_USER=""
BUILD_DIRS=()


# jq is needed to read our json files
check_jq_installed() {
    if ! command -v jq &> /dev/null; then
        print_error "jq is not installed. Please install jq to proceed."
        return 1
    fi
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
        ["SRV_SRC_DIR"]=".src_dir"
        ["SRV_TESTS_DIR"]=".tests_dir"
        ["SRV_INSTALL_DIR"]=".install_dir"
        ["SRV_ASSETS_DIR"]=".assets_dir"
    )

    retrieve_dir() {
        local var_name=$1
        local jq_filter=$2
        local config_file=$3

        local dir
        dir=$(run_or_sudo jq -r "$jq_filter" "$config_file")
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
        local keys
        keys=$(run_or_sudo jq -r 'keys[]' "$cfg_file")
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
        run_or_sudo mkdir -p "$dir" >/dev/null
        if [ $? -eq 0 ]; then
            print_debug "Created directory: $dir"
        else
            print_error "Failed to Build Directory: $dir"
            return 1
        fi
    done
}

recursive_copy() {
    local src_dir="$1"
    local dest_dir="$2"

    # Check if source directory exists
    if [ ! -d "$src_dir" ]; then
        echo "Source directory does not exist: $src_dir"
        return 1
    fi

    # Create the destination directory, including parents if necessary
    run_or_sudo mkdir -p "$dest_dir" >/dev/null

    # Check if the destination directory was created successfully
    if [ ! -d "$dest_dir" ]; then
        echo "Failed to create destination directory: $dest_dir"
        return 1
    fi

    # Recursively copy all contents from source to destination
    run_or_sudo cp -r "$src_dir"/* "$dest_dir" >/dev/null

    # Check if the copy was successful
    if [ $? -ne 0 ]; then
        echo "Failed to copy contents from $src_dir to $dest_dir"
        return 1
    fi

    echo "Successfully copied contents from $src_dir to $dest_dir"
    return 0
}


copy_templates() {
    print_debug "Copying templates from '$TEMPLATES_DIR'..."

    if [[ ! -d "$TEMPLATES_DIR" ]]; then
        print_error "Templates directory '$TEMPLATES_DIR' does not exist."
        return 1
    fi

    # Declare the associative array properly
    declare -A destinations=(
        [dynamic]="$SRV_DATA_DIR/dynamic"
        [secrets]="$SRV_SECRETS_DIR/"
        [static]="$SRV_DATA_DIR/static"
    )

    for dir in "$TEMPLATES_DIR"/*; do
        if [[ -d "$dir" ]]; then
            dir_name=$(basename "$dir")
            print_debug "Processing template directory: $dir_name"

            if [[ -n "${destinations[$dir_name]}" ]]; then
                print_debug "Copying ${dir_name} templates..."
                recursive_copy "$dir" "${destinations[$dir_name]}" > /dev/null
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

    local current_user
    current_user=$(whoami)
    if [[ $? -ne 0 ]]; then
        print_error "Failed to get the current user."
        return 1
    fi

    SERVICE_USER=$(run_or_sudo jq -r '.service_usergroup' "$SRV_CFG_FILE")
    if [[ $? -ne 0 ]]; then
        print_error "Failed to evaluate SERVICE_USER from JSON."
        return 1
    fi

    if ! sudo useradd --system --user-group --no-create-home $SERVICE_USER; then
        print_error "Failed to add service user '$SERVICE_USER'."
        return 1
    fi

    if ! sudo usermod -aG "$SERVICE_USER" "$current_user"; then
        print_error "Failed to add current user '$current_user' to group '$SERVICE_USER'."
        return 1
    fi

    print_debug "Service user '$SERVICE_USER' created, and current user '$current_user' added to the group '$SERVICE_USER'."
}

copy_project_structure() {
    # Define source and destination directories
    local sources=("$PROJECT_DIR/src" "$PROJECT_DIR/tests" "$PROJECT_DIR/install" "$PROJECT_DIR/assets")
    local destinations=("$SRV_SRC_DIR" "$SRV_TESTS_DIR" "$SRV_INSTALL_DIR" "$SRV_ASSETS_DIR")

    # Iterate over the arrays and copy each source to its corresponding destination
    for i in "${!sources[@]}"; do
        local src="${sources[$i]}"
        local dest="${destinations[$i]}"
        recursive_copy "$src" "$dest"
    done
}


copy_build_cfgs() {
    run_or_sudo mkdir -p "$SRV_DATA_DIR"/static/
    run_or_sudo cp "$SRV_CFG_FILE" "$SRV_DATA_DIR/static/"
    if [[ $? -ne 0 ]]; then
        print_error "Failed to copy $SRV_CFG_FILE to $SRV_DATA_DIR/static"
        return 1
    fi

    run_or_sudo cp "$USR_CFG_FILE" "$SRV_DATA_DIR/static/"
    if [[ $? -ne 0 ]]; then
        print_error "Failed to copy $USR_CFG_FILE to $USR_DATA_DIR/static"
        return 1
    fi
    update_usr_cfg_file
}

update_usr_cfg_file() {
    local CURRENT_USER
    CURRENT_USER=$(whoami)

    local json_content
    json_content=$(<"$USR_CFG_FILE")  # Use < for reading file content

    # Avoid potential rogue new lines by trimming input and output
    local modified_content
    modified_content=$(echo "$json_content" | sed "s|\$(whoami)|$(whoami)|g" | tr -d '\r')

    local output_file
    output_file="$SRV_DATA_DIR/static/$(basename "$USR_CFG_FILE")"
    echo -n "$modified_content" | sudo tee "$output_file" > /dev/null
}

restrict_file_permissions() {
    print_debug "Restricting file permissions..."
    local user
    user=$(whoami)
    if [[ $? -ne 0 ]]; then
        print_error "Failed to determine the current user."
        return 1
    fi

    change_permissions() {
        local dir=$1
        local file_perms=$2
        local dir_perms=$3

        sudo chown -R "$user":"$SERVICE_USER" "$dir"  >/dev/null
        if [[ $? -ne 0 ]]; then
            print_error "Failed to change ownership for $dir."
            return 1
        fi

        sudo find "$dir" -type f -exec chmod "$file_perms" {} \; >/dev/null
        if [[ $? -ne 0 ]]; then
            print_error "Failed to set file permissions for $dir."
            return 1
        fi

        sudo find "$dir" -type d -exec chmod "$dir_perms" {} \; >/dev/null
        if [[ $? -ne 0 ]]; then
            print_error "Failed to set directory permissions for $dir."
            return 1
        fi
    }

    change_permissions "$SRV_SECRETS_DIR" 660 770 || return 1
    change_permissions "$SRV_OUTPUT_DIR" 660 770 || return 1
    change_permissions "$SRV_LOG_DIR" 660 770 || return 1
    change_permissions "$SRV_DATA_DIR" 660 770 || return 1
    change_permissions "$SRV_SRC_DIR" 770 770 || return 1
    change_permissions "$SRV_TESTS_DIR" 770 770 || return 1
    change_permissions "$SRV_INSTALL_DIR" 770 770 || return 1
    change_permissions "$SRV_ASSETS_DIR" 770 770 || return 1


    print_debug "Ownership and permissions set for all service directories."
}


link_user_directories() {
    local user
    user=$(whoami)
    if [[ $? -ne 0 ]]; then
        print_error "Failed to determine the current user."
        return 1
    fi

    link_directory() {
        local src_dir=$1
        local dest_dir=$2
        run_or_sudo ln -sf "$src_dir"/* "$dest_dir" >/dev/null
        if [[ $? -ne 0 ]]; then
            print_error "Failed to link $src_dir to $dest_dir."
            return 1
        fi
    }

    USR_OUTPUT_DIR=$(run_or_sudo jq -r '.output_dir' "$USR_CFG_FILE" | eval echo "$(cat -)")
    USR_LOG_DIR=$(run_or_sudo jq -r '.log_dir' "$USR_CFG_FILE" | eval echo "$(cat -)")
    USR_DATA_DIR=$(run_or_sudo jq -r '.data_dir' "$USR_CFG_FILE" | eval echo "$(cat -)")

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

          # Create Aesop Service user and group
    print_info "\nCreating Aesop service user and group..."
    create_service_user_and_group
    if [[ $? -ne 0 ]]; then
        print_error "Service user creation failed"
        exit 1
    fi
    print_success "Service user and group created successfully."

    # Get directories from build_configs
    print_info "\nRetrieving JSON directories..."
    retrieve_json_directories
    if [ $? -ne 0 ]; then
        exit_error "Failed to retrieve JSON directories."
        exit 1
    fi
    print_success "JSON directories retrieved successfully."

    # Make sure the templates exist
    print_info "\nChecking if templates directory exists..."
    check_templates_exist
    if [ $? -ne 0 ]; then
        exit_error "Templates Directory Doesnt exist."
        exit 1
    fi
    print_success "Templates Directory Exists."

    # Build the base directory structure
    print_info "\nBuilding base directories..."
    build_base_directories
    if [ $? -ne 0 ]; then
        print_error "Failed to build base directories."
        exit 1
    fi
    print_success "Base directories built successfully."

    # Copy templates into the new directory structure
    print_info "\nCopying templates..."
    copy_templates
    if [ $? -ne 0 ]; then
        print_error "Failed to copy templates."
        exit 1
    fi
    print_success "Templates copied successfully."

    # Copy the build configs to data/static
    print_info "\nCopying Build Configs..."
    copy_build_cfgs >/dev/null
    if [[ $? -ne 0 ]]; then
        print_error "Build configs could not be copied"
        exit 1
    fi
    print_success "Build configs copied successfully."

    # Copy the source files
    print_info "\nCopying project file structure..."
    copy_project_structure >/dev/null
    if [[ $? -ne 0 ]]; then
        print_error "Project file structure could not be copied"
        exit 1
    fi
    print_success "Project file structure copied successfully."

    # Restrict file permissions for service level assets
    print_info "\nRestricting file permissions..."
    restrict_file_permissions
    if [ $? -ne 0 ]; then
        print_error "Failed to restrict file permissions."
        exit 1
    fi
    print_success "File permissions restricted successfully."

    # Link service files to user's home config folder
    print_info "\nLinking user directories..."
    link_user_directories
    if [ $? -ne 0 ]; then
        print_error "Failed to link user directories."
        exit 1
    fi
    print_success "User directories linked successfully."

    print_success "File Structure Built Successfully!"
}

main
