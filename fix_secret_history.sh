#!/bin/bash
# Script to remove the secret from git history

set -e

echo "This script will rewrite git history to remove the secret."
echo "WARNING: This will change commit hashes. Make sure you have a backup!"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Check if git-filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo "Installing git-filter-repo..."
    pip install git-filter-repo
fi

# Backup current branch
echo "Creating backup branch..."
git branch backup-before-history-rewrite

# Remove the notebook file from all history
echo "Removing notebook from git history..."
git filter-repo --path "HBWorkshop (2).ipynb" --invert-paths --force

echo ""
echo "Done! The notebook has been removed from all git history."
echo "You can now push with: git push origin main --force"
echo ""
echo "To restore from backup: git checkout backup-before-history-rewrite"

