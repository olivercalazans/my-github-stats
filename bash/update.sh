#!/bin/bash

# Configure safe directory (required for Debian/Docker container environments)
git config --global --add safe.directory /__w/github-stats/github-stats

# Set commit identity
git config --global user.name 'github-actions[bot]'
git config --global user.email 'github-actions[bot]@users.noreply.github.com'

# Check repository status
git status

# Stage all changes inside the images folder
git add images/

# Commit and push changes only if modifications are detected in the images folder
git diff --staged --quiet || (git commit -m "update profile stats SVGs [skip ci]" && git push)