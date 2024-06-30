#!/bin/bash
SCRIPT_DIR=$(dirname "$(realpath "$0")")
CSV_FILE="$SCRIPT_DIR/dependencies.csv"

# Detect the installed package manager and set the appropriate commands for update and install.
detect_and_set_commands() {
    local header_read=0  # Flag to check if the header has been processed.
    while IFS=',' read -ra CSV_LINE; do
        if [[ $header_read -eq 0 ]]; then
            # Process the header to determine which package manager is available on this system.
            for i in "${!CSV_LINE[@]}"; do
                # Check if the command for the package manager exists on the system.
                if command -v "${CSV_LINE[i]}" &> /dev/null; then
                    PKG_MANAGER="${CSV_LINE[i]}" # Assign the package manager
                    PKG_MANAGER_INDEX="$i"
                    break
                fi
            done
            if [[ -z "$PKG_MANAGER" ]]; then
                echo "No supported package manager found. Exiting."
                exit 1
            fi
            header_read=1  # Set the header as read. so we can continue (below)
        else
            # Process package commands based on the header information.
            case "${CSV_LINE[0]}" in
                update)
                    # Set the command to update the package repository.
                    UPDATE_CMD="${CSV_LINE[$PKG_MANAGER_INDEX]}"
                    ;;
                install)
                    # Set the base command to install packages.
                    INSTALL_CMD="${CSV_LINE[$PKG_MANAGER_INDEX]}"
                    ;;
                *)
                    # Add the correct install command for each package.
                    local package_install_command="${CSV_LINE[$PKG_MANAGER_INDEX]}"
                    if [[ -n "$package_install_command" && "$package_install_command" != "[OVERRIDE]" ]]; then
                        if [[ "$package_install_command" == *"[OVERRIDE]"* ]]; then
                            # Handle override commands by removing the '[OVERRIDE]' tag and using the command directly.
                            package_install_command="${package_install_command//\[OVERRIDE\]/}"
                            INSTALL_COMMANDS+=("$package_install_command")
                        else
                            # Normal package installations prepend the install command.
                            INSTALL_COMMANDS+=("$INSTALL_CMD $package_install_command")
                        fi
                    fi
                    ;;
            esac
        fi
    done < "$CSV_FILE"
}

# Update the package manager using the command specified in the CSV.
update_package_manager() {
    echo "Yo! We need sudo access to install your dependencies!"

    # echo for sudo caching
    sudo echo "" >/dev/null
    if [ $? -eq 0 ]; then
        # If the sudo command succeeded, proceed with the update
        echo "Updating package manager with command: $UPDATE_CMD"
        eval "$UPDATE_CMD"
    else
        # If the sudo command failed, exit the script
        echo "Failed to gain sudo access. Exiting."
        exit 1
    fi
}

# Execute all generated installation commands.
execute_install_commands() {
    echo "Running installation commands..."
    for cmd in "${INSTALL_COMMANDS[@]}"; do
        echo "Executing: $cmd"
        eval "$cmd"
    done
}

# Print all generated installation commands for review.
print_install_commands() {
    echo "Installation commands to be executed:"
    for cmd in "${INSTALL_COMMANDS[@]}"; do
        echo "$cmd"
    done
}

# Initialize the commands array and start the main process flow.
INSTALL_COMMANDS=()
detect_and_set_commands
#print_install_commands  # Switch to execute_install_commands to run the installation instead of printing.
update_package_manager
execute_install_commands