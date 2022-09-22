#!/bin/bash

# Get branch version
eval $(bumpver show -n --env)
BRANCH_VERSION=$CURRENT_VERSION

# Reset the local version to an old date
sed -r -i -e '/current_version = .*[[:digit:]]+.*/ s/= .*/= "0.1970.01.01"/' pyproject.toml

# Bump project version according to the distant tags
bumpver update --patch --no-commit --no-tag-commit --no-push

# Check if they are uncommitted files
if [ -z "$(git status --porcelain)" ]; then
  # Working directory clean
  echo "Nothing to commit, the version is up-to-date"
else
  # Uncommitted changes
  echo "Git repository not clean. Please commit and push your changes to pass CI."
  exit 1
fi
