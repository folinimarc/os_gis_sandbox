#!/bin/sh

# Given a requirements file and a download destination, downloads packages to
# destination and installs them from there. Only requires internet connection for
# first download.

# Example:
# $ ./pip_download_install.sh requirements.txt download_folder

# It is important that the download and install commands use the same version of
# pip. In case of a version mismatch (e.g. because of updated base environment) remove
# all downloaded packages to download them again with new version.

# Make sure a directory exists to download pip packages from
# requirements-override.txt. In case of no internet they can be restored from there.
if [ ! -d $2 ]; then
    mkdir $2
fi
# Path and name of file to use to persist pip version.
FILE_PIP_VERSION=$2/pip.version
# Get pip version currently used and if a version file exists read the previous
# version from it.
CURRENT_PIP_VERSION=$(pip list --format freeze | grep pip)
if [ -f $FILE_PIP_VERSION ]; then
    PREVIOUS_PIP_VERSION=$(<$FILE_PIP_VERSION)
fi
# If the two versions do not match, remove content of download folder.
if [ "$CURRENT_PIP_VERSION" != "$PREVIOUS_PIP_VERSION" ]; then
    rm -r $2/*
fi
# Save current pip version to file future checks.
$CURRENT_PIP_VERSION > $FILE_PIP_VERSION
# Finally download and install the packages
pip download -r $1 -d $2
pip install --no-index -r $1 -f $2
