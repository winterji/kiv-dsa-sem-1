#!/bin/bash

# Exit if any command fails
set -e

# the directory to initialize provided as an argument
if [ -z "$1" ]; then
  echo "No directory provided."
  read -p "Enter the directory to initialize: " DIR
else
  DIR=$1
fi

# Ask for remote repo URL - if not provided as an argument
if [ -z "$2" ]; then
  echo "No remote repository URL provided."
  read -p "Enter the remote Git repository URL: " REMOTE_URL
else
  REMOTE_URL=$2
fi

echo "Initializing Git repository in $DIR with remote $REMOTE_URL"

# # Initialize a new Git repository
# git init

# Add all files
git add .

# Commit the files
git commit -m "Initial commit"

# Add the remote
git remote add origin "$REMOTE_URL"

# Push to the remote repository
git push -u origin master 2>/dev/null || git push -u origin main
