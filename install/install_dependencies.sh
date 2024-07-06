#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/common.lib"

INSTALL_COMMANDS=()
PACKAGES=()
INSTALLED_PACKAGES=()
FAILED_PACKAGES=()
UPDATE_CMD=""
INSTALL_CMD=""
CHECK_CMD=""
PKG_MANAGER=""
PKG_MANAGER_INDEX=""

# Get Dependency Data From CSV
detect_package_manager() {
    print_debug "Determining Package Manager..."

    if [[ ! -f "$DEPENDENCIES_CSV_PATH" ]]; then
        print_error "Dependencies CSV file not found at path: $DEPENDENCIES_CSV_PATH"
        return 1
    fi

    IFS=',' read -ra CSV_HEADER < "$DEPENDENCIES_CSV_PATH"
    if [[ $? -ne 0 || ${#CSV_HEADER[@]} -eq 0 ]]; then
        print_error "Failed to read dependencies CSV file or it is empty: $DEPENDENCIES_CSV_PATH"
        return 1
    fi

    for i in "${!CSV_HEADER[@]}"; do
        if [[ "${CSV_HEADER[i]}" != "package" ]] && command -v "${CSV_HEADER[i]}" &> /dev/null; then
            PKG_MANAGER="${CSV_HEADER[i]}"
            PKG_MANAGER_INDEX="$i"
            print_debug "Package manager found: $PKG_MANAGER"
            return
        fi
    done

    print_error "No supported package manager found. Please install the following dependencies manually:"
    list_dependencies
    return 1
}

list_dependencies() {
    awk -F',' '!/^(update|install|check_installed|package)/{print $1}' "$DEPENDENCIES_CSV_PATH"
}

retrieve_package_manager_commands() {
    local commands=(update install check_installed)

    if [[ ! -f "$DEPENDENCIES_CSV_PATH" ]]; then
        print_error "Dependencies CSV file not found: $DEPENDENCIES_CSV_PATH"
        return 1
    fi

    for command in "${commands[@]}"; do
        IFS=',' read -ra CSV_LINE < <(awk -v cmd="$command" -F',' '$1 == cmd {print $0}' "$DEPENDENCIES_CSV_PATH")

        if [[ ${#CSV_LINE[@]} -le $PKG_MANAGER_INDEX ]]; then
            print_error "Invalid package manager index for command: $command"
            return 1
        fi

        case "$command" in
            update)
                if [[ -z "${CSV_LINE[$PKG_MANAGER_INDEX]}" ]]; then
                    print_error "Update command not found in CSV for command: $command"
                    return 1
                fi
                UPDATE_CMD="${CSV_LINE[$PKG_MANAGER_INDEX]}"
                ;;
            install)
                if [[ -z "${CSV_LINE[$PKG_MANAGER_INDEX]}" ]]; then
                    print_error "Install command not found in CSV for command: $command"
                    return 1
                fi
                INSTALL_CMD="${CSV_LINE[$PKG_MANAGER_INDEX]}"
                ;;
            check_installed)
                if [[ -z "${CSV_LINE[$PKG_MANAGER_INDEX]}" ]]; then
                    print_error "Check installed command not found in CSV for command: $command"
                    return 1
                fi
                CHECK_CMD="${CSV_LINE[$PKG_MANAGER_INDEX]}"
                ;;
            *)
                print_error "Unknown command: $command"
                return 1
                ;;
        esac
    done
}


parse_package_rows() {
    if [[ ! -f "$DEPENDENCIES_CSV_PATH" ]]; then
        print_error "Dependencies CSV file not found at path: $DEPENDENCIES_CSV_PATH"
        return 1
    fi

    while IFS=',' read -ra CSV_LINE; do
        local packages_to_install="${CSV_LINE[$PKG_MANAGER_INDEX]}"
        if [[ $? -ne 0 ]]; then
            print_error "Failed to read CSV line"
            return 1
        fi

        if [[ -n "$packages_to_install" && "$packages_to_install" != "[OVERRIDE]" ]]; then
            if [[ "$packages_to_install" == *"[OVERRIDE]"* ]]; then
                INSTALL_COMMANDS+=("${packages_to_install//\[OVERRIDE\]/}")
                if [[ $? -ne 0 ]]; then
                    print_error "Failed to replace [OVERRIDE] in package name: $packages_to_install"
                    return 1
                fi
            else
                PACKAGES+=("$packages_to_install")
                if [[ $? -ne 0 ]]; then
                    print_error "Failed to add package to the list: $packages_to_install"
                    return 1
                fi

                INSTALL_COMMANDS+=("$INSTALL_CMD $packages_to_install")
                if [[ $? -ne 0 ]]; then
                    print_error "Failed to add install command for package: $packages_to_install"
                    return 1
                fi
            fi
        fi
    done < <(awk -F',' '!/^(update|install|check_installed|package)/' "$DEPENDENCIES_CSV_PATH")

    if [[ $? -ne 0 ]]; then
        print_error "Failed to process CSV file: $DEPENDENCIES_CSV_PATH"
        return 1
    fi
}


update_package_manager() {
    print_debug "Updating package manager with command: $UPDATE_CMD"
    eval "$UPDATE_CMD"
}

execute_install_commands() {
    local cmd
    local package_name

    for cmd in "${INSTALL_COMMANDS[@]}"; do
        print_debug "Executing: $cmd"
        package_name=$(echo "$cmd" | awk '{print $NF}')
        if eval "$cmd"; then
            INSTALLED_PACKAGES+=("$package_name")
        else
            print_warning "Failed to install $package_name"
            FAILED_PACKAGES+=("$package_name")
        fi
    done
}

split_packages() {
    if [[ ${#PACKAGES[@]} -eq 0 ]]; then
        print_error "PACKAGES array is empty or undefined."
        return 1
    fi

    # Join all elements into a single string and split them using xargs
    local joined_packages
    joined_packages=$(printf "%s " "${PACKAGES[@]}")

    # Use xargs to split the string into individual packages
    read -r -a PACKAGES <<< "$(echo "$joined_packages" | xargs -n1)"

    if [[ ${#PACKAGES[@]} -eq 0 ]]; then
        print_error "No packages were split or found."
        return 1
    fi
}

final_package_check() {
    if [[ ${#INSTALLED_PACKAGES[@]} -gt 0 ]]; then
        print_success "The following dependencies were installed successfully:"
        for pkg in "${INSTALLED_PACKAGES[@]}"; do
            echo -e "${GREEN}- $pkg${NC}"
        done
    fi

    if [[ ${#FAILED_PACKAGES[@]} -gt 0 ]]; then
        print_warning "Some dependencies failed to install. Please install the following packages manually:"
        for pkg in "${FAILED_PACKAGES[@]}"; do
            echo -e "${RED}- $pkg${NC}"
        done
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

    echo "Failed Packages:"
    for cmd in "${FAILED_PACKAGES[@]}"; do
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
    print_title "Installing System Dependencies..."

    # Determine which package manager is installed
    print_info "\nDetecting Package Manager..."
    detect_package_manager
    if [ $? -ne 0 ]; then
        print_error "Could Not find a supported Package Manager."
        exit 1
    fi
    print_success "Package Manager Found: $PKG_MANAGER"

    # Retrieve package manager commands
    print_info "\nRetrieving Package Manager Commands..."
    retrieve_package_manager_commands
    if [ $? -ne 0 ]; then
        print_error "Could not retrieve package manager commands."
        exit 1
    fi
    print_success "Initialized Package Manager Commands: $PKG_MANAGER"

    # Parse Package Rows
    print_info "\nParsing Packages..."
    parse_package_rows
    if [ $? -ne 0 ]; then
        print_error "Could not parse packages."
        exit 1
    fi
    print_success "Packages Parsed."

    #Split Packages into single array
    print_info "Initializing Packages Array"
    split_packages
    if [ $? -ne 0 ]; then
        print_error "Failed to initialize packages."
        exit 1
    fi
    print_success "Packages Initialized"


    # Update Package Manager Repository
    print_info "\nUpdating $PKG_MANAGER repository..."
    update_package_manager > /dev/null 2>&1 & pid=$!
    show_loading_animation $pid
    wait $pid
    if [ $? -ne 0 ]; then
        print_error "Failed to update repository."
        exit 1
    fi
    print_success "$PKG_MANAGER repository updated"

    # Install Dependency Packages
    print_info "\nInstalling Packages..."
    execute_install_commands > /dev/null 2>&1 & pid=$!
    show_loading_animation $pid
    wait $pid
    if [ $? -ne 0 ]; then
        print_error "Failed to install packages."
        exit 1
    fi
    print_success "Packages Installed."

    # Perform Final Checking
    print_info "\nInitiating final package check..."
    final_package_check
    print_batch_debug
}

main
