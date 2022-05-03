#!/bin/sh


if $HOME_DIR_PERSISTED
then
    # Copy readme explaining persistence and overwrite procedure.
    cp /assets/_README.md /home/_README.md
fi

# Copy base requirements for visibility to user what is installed by default in
# image and add warning header.
cp /assets/requirements-base.txt /home/requirements-base.txt
echo '# NOTE:
# These packages are installed by default and this file is reset upon Sandbox restart!
# Use requirements-override.txt to add new packages.
'"$(cat /home/requirements-base.txt)" > /home/requirements-base.txt

# If an requirements-override.txt exists, run pip upgrade. Otherwise create
# empty file.
if [ ! -f /home/requirements-override.txt ]; then
touch /home/requirements-override.txt
echo '# NOTE:
# Use this requirements file to add new python packages.
# This file is processed by pip upon each Sandbox start.
# The more packages are added here, the longer the startup time.
# Internet connection is only required the first time after changing this
# file, further startups will use downloaded versions of the packages.
'"$(cat /home/requirements-override.txt)" > /home/requirements-override.txt
fi

# Download and install packages from requirements-override.txt into /pip_overwrite_requirements_download.
/assets/pip_download_install.sh /home/requirements-override.txt /pip_overwrite_requirements_download

# Run the CMD as the main container process
exec "$@"
