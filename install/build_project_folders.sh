#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/colors.lib"
source "$SCRIPT_DIR/filepaths.lib"


check_jq_installed(){
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}ERROR: jq is not installed. Please install jq to proceed.${NC}"
        exit 1
    fi
}

check_templates_exists(){
    if [ ! -d "$TEMPLATES_DIR" ]; then
        echo -e "${RED}$TEMPLATES_DIR does not exist or is not a directory. This shouldnt happen. Maybe check the repo?${NC}"
        exit 1
    fi
}

eval_json_value() {     # Allows us to use bash $Variables in our json
    local value
    value=$(jq -r "$1" "$BUILD_CFG_FILE")
    eval echo "$value"
}

retrieve_json_directories() {
#    SECRETS_DIR=$(eval_json_value '.secrets_dir')
    SECRETS_DIR="/home/neon/Downloads/__SECRETS_TEST__"
    OUTPUT_DIR=$(eval_json_value '.output_dir')
    LOG_DIR=$(eval_json_value '.log_dir')
    DATA_DIR="/home/neon/Downloads/__COPY_TEST__"
#    DATA_DIR=$(eval_json_value '.data_dir')
    BUILD_DIRS=(
        "$SECRETS_DIR"
        "$OUTPUT_DIR"
        "$LOG_DIR"
        "$DATA_DIR/static"
        "$DATA_DIR/dynamic"
    )
}

recursive_copy() {
    local src_dir=$1
    local dest_dir=$2

    find "$src_dir" -type f | while read -r template; do
        local relative_path="${template#$src_dir/}"
        local new_filename="${relative_path/_template.json/.json}"
        new_filename="${new_filename/_template.txt/.txt}"
        local new_filepath="$dest_dir/$new_filename"
        local new_filepath_dir=$(dirname "$new_filepath")

        mkdir -p "$new_filepath_dir"

        if [[ ! -f "$new_filepath" ]]; then
            echo -e "\tCopying $template to $new_filepath"
            cp "$template" "$new_filepath"
        else
            echo -e "\t$new_filepath already exists, skipping."
        fi
    done
}

#region Debug
debug_json_data() {
    echo "SECRETS_DIR=$SECRETS_DIR"
    echo "OUTPUT_DIR=$OUTPUT_DIR"
    echo "LOG_DIR=$LOG_DIR"
    echo "DATA_DIR=$DATA_DIR"
}

build_base_directories() {
    for dir in "${BUILD_DIRS[@]}"; do
        mkdir -p "$dir"
    done


}
#endregion

main() {
    check_jq_installed
    retrieve_json_directories
    check_templates_exists
    build_base_directories

    for dir in "$TEMPLATES_DIR"/*; do
        if [ -d "$dir" ]; then
            dir_name=$(basename "$dir")

            case "$dir_name" in
                dynamic)
                    echo "DYNAMIC_TEMPLATES:"
                    recursive_copy "$dir" "$DATA_DIR/dynamic"
                    ;;
                secrets)
                    echo "SECRETS_TEMPLATES:"
                    recursive_copy "$dir" "$SECRETS_DIR"
                    ;;
                static)
                    echo "STATIC_TEMPLATES:"
                    recursive_copy "$dir" "$DATA_DIR/static"
                    ;;
                *)
                    echo -e "${YELLOW}WARNING: unexpected templates directory: $dir_name"
                    TARGET_DIR="$dir"
                    ;;
            esac
        fi
    done
}


main


