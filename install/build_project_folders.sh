#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/colors.lib"
source "$SCRIPT_DIR/filepaths.lib"
SERVICE_USER=""

# jq is needed to read our json files
check_jq_installed(){
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}ERROR: jq is not installed. Please install jq to proceed.${NC}"
        exit 1
    fi
}

# Evaluate JSON value with environment variable substitution
eval_json_value() {
    local json_file=$1
    local key=$2
    local value
    value=$(jq -r "$key" "$json_file")
    eval echo "$value"
}

# Check if templates directory exists
check_templates_exists(){
    if [ ! -d "$TEMPLATES_DIR" ]; then
        echo -e "${RED}$TEMPLATES_DIR does not exist or is not a directory. This shouldnt happen. Maybe check the repo?${NC}"
        exit 1
    fi
}


retrieve_json_directories() {
    SRV_SECRETS_DIR=$(eval_json_value "$SRV_CFG_FILE" '.secrets_dir')
    SRV_OUTPUT_DIR=$(eval_json_value "$SRV_CFG_FILE" '.output_dir')
    SRV_LOG_DIR=$(eval_json_value "$SRV_CFG_FILE" '.log_dir')
    SRV_DATA_DIR=$(eval_json_value "$SRV_CFG_FILE" '.data_dir')

    USR_OUTPUT_DIR=$(eval_json_value "$USR_CFG_FILE" '.output_dir')
    USR_LOG_DIR=$(eval_json_value "$USR_CFG_FILE" '.log_dir')
    USR_DATA_DIR=$(eval_json_value "$USR_CFG_FILE" '.dir')

    BUILD_DIRS=(
        "$SRV_SECRETS_DIR"
        "$SRV_OUTPUT_DIR"
        "$SRV_LOG_DIR"
        "$SRV_DATA_DIR/static"
        "$SRV_DATA_DIR/dynamic"
        "$USR_OUTPUT_DIR"
        "$USR_LOG_DIR"
        "$USR_DATA_DIR"
    )
}


build_base_directories() {
    for dir in "${BUILD_DIRS[@]}"; do
        mkdir -p "$dir"
    done
}

# Recursively copy files, while removing "_template" from the destination filename
recursive_copy() {
    local src_dir=$1
    local dest_dir=$2

    find "$src_dir" -type f | while read -r template; do
        local relative_path="${template#$src_dir/}"
        local new_filename="${relative_path/_template.json/.json}"
        new_filename="${new_filename/_template.txt/.txt}"
        local new_filepath="$dest_dir/$new_filename"
        local new_filepath_dir=$(dirname "$new_filepath")

        mkdir -p "$new_filepath_dir" || sudo mkdir -p "$new_filepath_dir"

        if [[ ! -f "$new_filepath" ]]; then
            echo -e "\tCopying $template to $new_filepath"
            cp "$template" "$new_filepath" || sudo cp "$template" "$new_filepath"
        else
            echo -e "\t$new_filepath already exists, skipping."
        fi
    done
}

# !IMPORTANT the templates dir should always have the same child folders that data has.
# This makes things easy to code, and easy to visualize... is what im saying right now.
# Very possible that im just lazy and hate looking at bash.
copy_templates() {
    for dir in "$TEMPLATES_DIR"/*; do
        if [ -d "$dir" ]; then
            dir_name=$(basename "$dir")

            case "$dir_name" in
                dynamic)
                    echo "DYNAMIC_TEMPLATES:"
                    recursive_copy "$dir" "$SRV_DATA_DIR/dynamic"
                    ;;
                secrets)
                    echo "SECRETS_TEMPLATES:"
                    recursive_copy "$dir" "$SRV_SECRETS_DIR"
                    ;;
                static)
                    echo "STATIC_TEMPLATES:"
                    recursive_copy "$dir" "$SRV_DATA_DIR/static"
                    ;;
                *)
                    echo -e "${YELLOW}WARNING: unexpected templates directory: $dir_name"
                    ;;
            esac
        fi
    done
}

# I know we're going to need it later so may as well code it now
create_SERVICE_USER_and_group() {
    local current_user=$(whoami)
    SERVICE_USER=$(eval_json_value '.SERVICE_USERgroup')
    sudo adduser --system --user-group --no-create-home $SERVICE_USER
    sudo usermod -aG "$SERVICE_USER" "$current_user"
    echo "Service user '$SERVICE_USER' created, and current user '$current_user' added to the group '$SERVICE_USER'."

}

# Set standard data files to rw-r-----
# Set secrets to rw-------
restrict_file_permissions() {
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
    echo "Set ownership and permissions for all service directories."
}

link_user_directories() {
    local user=$(whoami)
    ln -sf "$SRV_OUTPUT_DIR" "$USR_OUTPUT_DIR"
    ln -sf "$SRV_LOG_DIR" "$USR_LOG_DIR"
    ln -sf "$SRV_DATA_DIR" "$USR_DATA_DIR"

    echo "Linked service directories to user directories."
}


debug_json_data() {
    echo "SRV_SECRETS_DIR=$SRV_SECRETS_DIR"
    echo "SRV_OUTPUT_DIR=$SRV_OUTPUT_DIR"
    echo "SRV_LOG_DIR=$SRV_LOG_DIR"
    echo "SRV_DATA_DIR=$SRV_DATA_DIR"
}


main() {
    check_jq_installed
    retrieve_json_directories
    check_templates_exists
    build_base_directories
    copy_templates
    restrict_file_permissions
    link_user_directories
}

main
