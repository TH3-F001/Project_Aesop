#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "${SCRIPT_DIR}/filepaths.lib"
source "${SCRIPT_DIR}/colors.lib"

INSTALL_COMMANDS=()
PACKAGES=()
INSTALLED_PACKAGES=()
UPDATE_CMD=""
INSTALL_CMD=""
CHECK_CMD=""
PKG_MANAGER=""
PKG_MANAGER_INDEX=""

# Get Dependency Data From CSV
detect_package_manager() {
    echo -e "\tDetermining Package Manager..."
    IFS=',' read -ra CSV_HEADER < "$DEPENDENCIES_CSV_PATH"

    for i in "${!CSV_HEADER[@]}"; do
        if [[ "${CSV_HEADER[i]}" != "package" ]] && command -v "${CSV_HEADER[i]}" &> /dev/null; then
            PKG_MANAGER="${CSV_HEADER[i]}"
            PKG_MANAGER_INDEX="$i"
            echo -e "${GREEN}\t\tPackage manager found: $PKG_MANAGER${NC}"
            return
        fi
    done

    echo -e "${YELLOW}\tERROR: No supported package manager found. Please install the following dependencies manually:"
    list_dependencies
    echo -e "${NC}"
    exit 1
}

list_dependencies() {
    awk -F',' '!/^(update|install|check_installed|package)/{print $1}' "$DEPENDENCIES_CSV_PATH"
}

retrieve_package_manager_commands() {
    local commands=(update install check_installed)
    for command in "${commands[@]}"; do
        IFS=',' read -ra CSV_LINE < <(awk -v cmd="$command" -F',' '$1 == cmd {print $0}' "$DEPENDENCIES_CSV_PATH")
        case "$command" in
            update) UPDATE_CMD="${CSV_LINE[$PKG_MANAGER_INDEX]}" ;;
            install) INSTALL_CMD="${CSV_LINE[$PKG_MANAGER_INDEX]}" ;;
            check_installed) CHECK_CMD="${CSV_LINE[$PKG_MANAGER_INDEX]}" ;;
        esac
    done
}

parse_package_rows() {
    while IFS=',' read -ra CSV_LINE; do
        local packages_to_install="${CSV_LINE[$PKG_MANAGER_INDEX]}"
        if [[ -n "$packages_to_install" && "$packages_to_install" != "[OVERRIDE]" ]]; then
            if [[ "$packages_to_install" == *"[OVERRIDE]"* ]]; then
                INSTALL_COMMANDS+=("${packages_to_install//\[OVERRIDE\]/}")
            else
                PACKAGES+=("$packages_to_install")
                INSTALL_COMMANDS+=("$INSTALL_CMD $packages_to_install")
            fi
        fi
    done < <(awk -F',' '!/^(update|install|check_installed|package)/' "$DEPENDENCIES_CSV_PATH")
}

update_package_manager() {
    echo -e "\tUpdating package manager with command: $UPDATE_CMD"
    eval "$UPDATE_CMD"
}

execute_install_commands() {
    echo "Running installation commands..."
    local new_packages=()
    for cmd in "${INSTALL_COMMANDS[@]}"; do
        echo "Executing: $cmd"
        if eval "$cmd"; then
            local package_name=$(echo "$cmd" | awk '{print $NF}')
            new_packages=()
            for pkg in "${PACKAGES[@]}"; do
                if [[ "$pkg" != "$package_name" ]]; then
                    new_packages+=("$pkg")
                else
                    INSTALLED_PACKAGES+=("$package_name")
                fi
            done
            PACKAGES=("${new_packages[@]}")
        else
            echo -e "${RED}Failed to install $cmd${NC}"
        fi
    done
}

filter_out_installed_packages() {
    split_packages
    local packages_to_install=()
    for package in "${PACKAGES[@]}"; do
        if ! eval "$CHECK_CMD $package" &>/dev/null; then
            packages_to_install+=("$package")
            INSTALL_COMMANDS+=("$INSTALL_CMD $package")
        else
            INSTALLED_PACKAGES+=("$package")
        fi
    done
    PACKAGES=("${packages_to_install[@]}")
}

split_packages() {
    local new_packages=()
    for item in "${PACKAGES[@]}"; do
        for pkg in $item; do
            new_packages+=("$pkg")
        done
    done
    PACKAGES=("${new_packages[@]}")
}

final_package_check() {
    if [[ ${#INSTALLED_PACKAGES[@]} -gt 0 ]]; then
        echo -e "${GREEN}The following dependencies were installed successfully:${NC}"
        for pkg in "${INSTALLED_PACKAGES[@]}"; do
            echo -e "${CYAN}- $pkg${NC}"
        done
        echo ""
    fi

    if [[ ${#PACKAGES[@]} -gt 0 ]]; then
        echo -e "${YELLOW}Some dependencies failed to install. Please install the following packages manually:${NC}"
        for pkg in "${PACKAGES[@]}"; do
            echo -e "${RED}- $pkg${NC}"
        done
    else
        if [[ ${#INSTALLED_PACKAGES[@]} -gt 0 ]]; then
            echo -e "${GREEN}All dependencies installed successfully!${NC}"
        else
            echo -e "${GREEN}No dependencies needed installation.${NC}"
        fi
    fi
}

#region Debug
print_install_commands() {
    echo -e "Installation commands to be executed:"
    for cmd in "${INSTALL_COMMANDS[@]}"; do
        echo -e "\t$cmd"
    done
}

print_packages() {
    echo "Packages to be installed:"
    for cmd in "${PACKAGES[@]}"; do
        echo -e "\t$cmd"
    done

    echo "Installed Packages:"
    for cmd in "${INSTALLED_PACKAGES[@]}"; do
        echo -e "\t$cmd"
    done

}

print_batch_debug() {
    print_install_commands
    print_packages
    echo "Install CMD: $INSTALL_CMD"
    echo "Update CMD: $UPDATE_CMD"
    echo "Check CMD: $CHECK_CMD"
    echo "Package Manager: $PKG_MANAGER"
}
#endregion

main() {
    echo -e "${CYAN}Installing Dependencies...${NC}"
    detect_package_manager
    retrieve_package_manager_commands
    parse_package_rows
    filter_out_installed_packages
    update_package_manager
    execute_install_commands
    final_package_check
#    print_batch_debug
}

main
