#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
source "$SCRIPT_DIR/common.lib"


#region Function Declarations:
recursive_copy() {
    local src_dir="$1"
    local dest_dir="$2"
    local ignore_list="$3"
    local rsync_exclude=""

    # Check if source directory exists
    if [ ! -d "$src_dir" ]; then
        exit_error "Source directory does not exist: $src_dir"
        return 1
    fi

    # Create the destination directory, including parents if necessary
    if ! run_or_sudo mkdir -p "$dest_dir" >/dev/null; then
        exit_error "Failed to build $dest_dir."
        return 1
    fi

    # Build rsync exclude patterns
    for item in $ignore_list; do
        rsync_exclude+="--exclude=$item "
    done

    # Recursively copy all contents from source to destination, excluding ignored items
    if ! run_or_sudo rsync -a ${rsync_exclude} "${src_dir}/" "${dest_dir}" >/dev/null; then
        exit_error "Failed to copy ${src_dir} to ${dest_dir}."
        return 1
    fi
}

rename_templates() {
    local dir="$1"
    sudo find "$dir" -type f -name '*_template*' | while read -r file; do
        new_name=$(echo "$file" | sed 's/_template//g')
        if ! run_or_sudo mv "$file" "$new_name"; then
            exit_error "Failed to rename template files."
            return 1
        fi
    done
}

update_env_file() {
    local key=$1
    local value=$2

    print_info "\n\nKey:$key\nValue: $value"

#    # Escape special characters in the value
#    # Use sed to update the key in the .env file
#    if grep -q "^$key=" "$DOT_ENV"; then
#        if ! sed -i "s/^$key=.*/$key=$value/" "$DOT_ENV"; then
#            exit_error "Failed to update $key in $DOT_ENV"
#            return 1
#        fi
#    else
#        if ! echo "$key=$value" >> "$DOT_ENV"; then
#            exit_error "Failed to add $key to $DOT_ENV"
#            return 1
#        fi
#    fi
}

create_symlink() {
    local target_dir=$1
    local link_name=$2

    run_or_sudo mkdir -p "$link_name"
    if [[ -e "$link_name" ]]; then
       run_or_sudo rm -rf "$link_name"
    fi

    if ! run_or_sudo ln -sf "$target_dir" "$link_name"; then
        exit_error "Failed to create symbolic link: $link_name -> $target_dir"
        return 1
    fi
}
#endregion



print_title "Building Application Environment..."

# Load variables from the dotenv file
print_info "Loading variables from dotenv file..."
SRC_DOT_ENV="$PROJECT_DIR/.env"

if [ -f "$SRC_DOT_ENV" ]; then
    # Read each line from the dotenv file
    while IFS= read -r line
    do
        # Trim whitespace and remove lines that are comments or empty
        line=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        if [[ ! $line =~ ^#.* ]] && [[ $line =~ = ]]; then
            # Split the line into key and value at the first '='
            key=$(echo "$line" | cut -d '=' -f 1 | tr -d '[:space:]')
            value=$(echo "$line" | cut -d '=' -f 2-)
            # Remove quotes around the value
            value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//')
            # Export the variable using eval to handle complex scenarios
            eval "export $key=\"$value\"" || exit_error "Could not export $value to $key."
        fi
    done < "$SRC_DOT_ENV"
    print_success "Dotenv loaded successfully."
else
    exit_error "Could not find .env file in project root: $PROJECT_DIR"
fi
DOT_ENV="$PROJECT_ROOT/.env"

# Creating Service user and group
print_info "\nCreating service user $SERVICE_USERGROUP"
CURRENT_USER=$(whoami)
if ! sudo useradd --system --user-group --no-create-home "$SERVICE_USERGROUP"; then
    exit_error "Failed to add service user '$SERVICE_USERGROUP'."
fi

if ! sudo usermod -aG "$SERVICE_USERGROUP" "$CURRENT_USER"; then
    exit_error "Failed to add current user '$CURRENT_USER' to group '$SERVICE_USERGROUP'."
fi
print_success "Service user created successfully"

#region File Structure

# Build Base Project Structure
print_info "\nBase Project File Structure..."
if ! recursive_copy "$PROJECT_DIR" "$PROJECT_ROOT" "secrets venv .git .gitignore .gitattributes .idea"; then
    exit_error "Failed to copy file structure."
fi

if ! sudo chown :"$SERVICE_USERGROUP" "$PROJECT_ROOT"; then
    exit_error "Failed to take ownership of Project Root: $PROJECT_ROOT"
fi
if ! sudo chmod 2770 "$PROJECT_ROOT"; then
    exit_error "Failed to give group rights to Project Root: $PROJECT_ROOT."
fi
print_success "Base Project File Structure Created Successfully."

#endregion


#region Replace DotEnv Placeholders

# Update PYTHON_BINARY
print_info "\nUpdating PYTHON_BINARY..."
if command -v python &> /dev/null; then
    PYTHON_BINARY="python"
elif command -v python3 &> /dev/null; then
    PYTHON_BINARY="python3"
else
    exit_error "No Python interpreter found."
fi
print_success "Python Binary Updated."

# Update User Paths
print_info "\nUpdating USR_DIRS..."
USR_DIRS=("USR_DATA_DIR" "USR_LOG_DIR" "USR_OUTPUT_DIR")
for var in "${USR_DIRS[@]}"; do
    dir="${!var}"
    new_path=$(echo "$dir" | sed "s/PLACEHOLDER/$CURRENT_USER/g")
    export "$var"="$new_path" || exit_error "Failed to export $new_path to $var"
done
print_success "USR_DIRS successfully updated."

# Link User Directories
print_info "\nLinking user directories to service directories"
create_symlink "$DATA_DIR" "$USR_DATA_DIR" >/dev/null || exit_error "Symlink $DATA_DIR -> $USR_LOG_DIR Failed"
create_symlink "$LOG_DIR" "$USR_LOG_DIR" >/dev/null || exit_error "Symlink $LOG_DIR -> $USR_LOG_DIR Failed"
create_symlink "$OUTPUT_DIR" "$USR_OUTPUT_DIR" >/dev/null || exit_error "Symlink $OUTPUT_DIR -> $USR_OUTPUT_DIR Failed"
print_success "Successfully linked user directories."


# Update ELEVENLABS_API_KEY
print_info "\nPlease Provide your ElevenLabs API Key:"
read -p "> " ELEVENLABS_API_KEY
if [[ "$ELEVENLABS_API_KEY" == *"PLACEHOLDER"* ]]; then
    exit_error "API key contains PLACEHOLDER. Please enter a valid API key. Exiting."
fi
print_success "ELEVENLABS_API_KEY Updated."

# Update GOOGLE_CLIENT_ID
print_info "\nPlease provide your primary Google Client ID:"
read -p "> " GOOGLE_CLIENT_ID
if [[ "$GOOGLE_CLIENT_ID" == *"PLACEHOLDER"* ]]; then
    exit_error "API key contains PLACEHOLDER. Please enter a valid API key. Exiting."
fi
print_success "GOOGLE_CLIENT_ID Updated."

# Update GOOGLE_CLIENT_SECRET
print_info "\nPlease provide your primary Google Client Secret:"
read -p "> " GOOGLE_CLIENT_SECRET
if [[ "$GOOGLE_CLIENT_SECRET" == *"PLACEHOLDER"* ]]; then
    exit_error "API key contains PLACEHOLDER. Please enter a valid API key. Exiting."
fi
print_success "GOOGLE_CLIENT_SECRET Updated."

# Update NEWSAPI_KEY
print_info "\nPlease provide your NewsAPI key:"
read -p "> " NEWSAPI_KEY
if [[ "$NEWSAPI_KEY" == *"PLACEHOLDER"* ]]; then
    exit_error "API key contains PLACEHOLDER. Please enter a valid API key. Exiting."
fi
print_success "NEWSAPI_KEY Updated."

# Update OPENAI API_KEY
print_info "\nPlease Provide your OpenAI API Key:"
read -p "> " OPENAI_API_KEY
if [[ "$OPENAI_API_KEY" == *"PLACEHOLDER"* ]]; then
    exit_error "API key contains PLACEHOLDER. Please enter a valid API key. Exiting."
fi
print_success "OPENAI_API_KEY Updated."

# Update REDDIT_CLIENT_ID
print_info "\nPlease Provide your Reddit Client ID:"
read -p "> " REDDIT_CLIENT_ID
if [[ "$REDDIT_CLIENT_ID" == *"PLACEHOLDER"* ]]; then
    exit_error "Reddit Client ID contains PLACEHOLDER. Please enter a valid Client ID. Exiting."
fi
print_success "REDDIT_CLIENT_ID Updated."

# Update REDDIT_CLIENT_SECRET
print_info "\nPlease Provide your Reddit Client Secret:"
read -p "> " REDDIT_CLIENT_SECRET
if [[ "$REDDIT_CLIENT_SECRET" == *"PLACEHOLDER"* ]]; then
    exit_error "Reddit Client Secret contains PLACEHOLDER. Please enter a valid Client Secret. Exiting."
fi
print_success "REDDIT_CLIENT_SECRET Updated."

# Update REDDIT_USERNAME
print_info "\nPlease Provide your Reddit Username:"
read -p "> " REDDIT_USERNAME
if [[ "$REDDIT_USERNAME" == *"PLACEHOLDER"* ]]; then
    exit_error "Reddit Username contains PLACEHOLDER. Please enter a valid Username. Exiting."
fi
print_success "REDDIT_USERNAME Updated."

# Update REDDIT_USER_AGENT
REDDIT_USER_AGENT_UPDATED=$(echo "$REDDIT_USER_AGENT" | sed "s/USERNAME/$REDDIT_USERNAME/g" | sed "s/CLIENT_ID/$REDDIT_CLIENT_ID/g")
REDDIT_USER_AGENT="\"$REDDIT_USER_AGENT_UPDATED\""

#Update the project dotenv file
print_info "\nSaving current environment variables back to the dotenv file..."

# Temporary file to store new .env content
TMP_DOT_ENV="$(mktemp)"

# Check if the dotenv file exists
if [ -f "$DOT_ENV" ]; then
    # Read each line from the dotenv file
    while IFS= read -r line
    do
        # Check if line is not a comment
        if [[ ! $line =~ ^#.* ]] && [[ $line =~ = ]]; then
            # Extract the key name (before the first '=')
            key=$(echo "$line" | cut -d '=' -f 1 | tr -d '[:space:]')

            # Fetch the current value of the environment variable
            current_value=$(eval echo "\$$key")

            # Handle cases where the variable may contain special characters
            if [[ $current_value =~ [^a-zA-Z0-9_@%/+=:,.-] ]]; then
                current_value="\"$current_value\""
            fi

            # Write the key and current value to the temp file
            echo "$key=$current_value" >> "$TMP_DOT_ENV"
        else
            # Write comments and empty lines as is to the temp file
            echo "$line" >> "$TMP_DOT_ENV"
        fi
    done < "$DOT_ENV"

    # Replace the old .env file with the new one
    sudo mv "$TMP_DOT_ENV" "$DOT_ENV"
    print_success "Environment variables saved back to dotenv file."
else
    exit_error "Could not find .env file in project root: $PROJECT_DIR"
fi

#endregion



#region Build Python Environment

# Install Poetry
print_info "\nInstalling Poetry..."
curl -sSL https://install.python-poetry.org | $PYTHON_BINARY -
if [ $? -ne 0 ]; then
    exit_error "Failed to install Poetry."
fi
print_success "Poetry installed successfully"

# Build venv
print_info "\nCreating virtual environment in $VENV_DIR using $PYTHON_BINARY..."
if ! "$PYTHON_BINARY" -m venv "$VENV_DIR"; then
    exit_error "Failed to create virtual environment."
fi
cd "$PROJECT_ROOT" && poetry install --no-root
print_success "Virtual environment created."

# Add dotenv path and secrets_dir to activate script
print_info "\nAdding DOT_ENV and SECRETS_DIR to activate script..."
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

if [[ ! -f "$ACTIVATE_SCRIPT" ]]; then
    exit_error "Activation script not found: $ACTIVATE_SCRIPT"
fi

echo "export DOT_ENV=\"$DOT_ENV\"" >> "$ACTIVATE_SCRIPT"
echo "export SECRETS_DIR=\"$SECRETS_DIR\"" >> "$ACTIVATE_SCRIPT"

print_success "DOT_ENV added to the activation script."

# Import the python environment
print_info "\nImporting virtual environment..."
source "$ACTIVATE_SCRIPT"
print_success "Python virtual environment set up successfully."
print_notice "---[! Remember to point your IDE to use the virtual environment at $VENV_DIR !]---"

#endregion








#endregion

# build the environment structure
#if run_or_sudo mkdir -p