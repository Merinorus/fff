#!/usr/bin/env python3
import os
import re
import sys

# Get branch version
bumpver_output = os.popen("bumpver show -n --env").read()
BRANCH_VERSION = re.findall("CURRENT_VERSION.*", bumpver_output).pop()
print(BRANCH_VERSION)

# Reset the local version to an old date
with open("pyproject.toml", "r+") as f:
    content = f.read()
    content_new = re.sub(
        r"current_version = \"[0-9]+\.[0-9]{4}\.[0-9]{2}\.[0-9]{2}.*\"",
        'current_version = "0.1970.01.01"',
        content,
        flags=re.M,
    )
    f.seek(0)
    f.write(content_new)
    f.truncate()

# # Bump project version according to the distant tags
os.system("bumpver update --patch --no-commit --no-tag-commit --no-push")

# Check if they are uncommitted files
if os.popen("git status --porcelain --untracked-files=no").read():
    # Uncommitted changes
    print("Git repository not clean. Please commit and push your changes to pass CI.")
    sys.exit(1)
else:
    # Working directory clean
    print("Nothing to commit, the version is up-to-date")
