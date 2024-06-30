#!/bin/bash

# Usage message
usage() {
    echo "Usage: $0 <filename> [branch]"
    echo "Purpose: This script removes all mentions of a specified file from Git history."
    echo "Arguments:"
    echo "  filename: The name of the file to be purged from the repository's history."
    echo "  branch: Optional. The specific branch to clean. If not specified, all branches will be processed."
    exit 1
}

# Check if at least one argument is provided
if [ $# -lt 1 ]; then
    usage
fi

# Assigning the first argument as filename
FILENAME="$1"

# Optional branch name
BRANCH="$2"

# Function to remove file from history
remove_file_history() {
    local branch=$1
    local file=$2

    # If a branch is specified, work on that branch; otherwise, work on all branches
    if [[ -n "$branch" ]]; then
        git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch $file" \
        --prune-empty --tag-name-filter cat -- --all
    else
        git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch $file" \
        --prune-empty --tag-name-filter cat -- $branch
    fi
}

# Executing the function based on whether the branch is specified
if [[ -n "$BRANCH" ]]; then
    echo "Removing $FILENAME from $BRANCH..."
    remove_file_history "$BRANCH" "$FILENAME"
else
    echo "Removing $FILENAME from all branches..."
    remove_file_history "" "$FILENAME"
fi

# Display cleanup message
echo "Operation completed. If you are satisfied with the state of your repository, run the following command to clean up:"
echo "git push origin --force --all"
