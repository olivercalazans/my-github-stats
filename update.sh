#!/bin/bash

# Configure safe directory (required for Debian/Docker container environments)
git config --global --add safe.directory /__w/github-stats/github-stats

# Set commit identity (can be updated to your personal GitHub credentials if desired)
git config --global user.name 'github-actions[bot]'
git config --global user.email 'github-actions[bot]@users.noreply.github.com'

# Check repository status
git status

# Stage the generated stats SVG file
git add languages_stats.svg

# Commit and push changes only if modifications are detected
git diff --staged --quiet || (git commit -m "chore: update languages stats SVG [skip ci]" && git push)