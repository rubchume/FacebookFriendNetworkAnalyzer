#!/usr/bin/env bash
pip install poetry
poetry install
poetry update

rm -rf .git

git init
git add --all
git commit -m "Initial commit"

rm README_FOR_DEVELOPER.md
rm -- "$0" # This script removes itself
