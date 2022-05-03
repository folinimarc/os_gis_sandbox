#!/bin/sh


if $HOME_DIR_PERSISTED
then
    # Copy readme explaining persistence and overwrite procedure.
    cp /assets/_README.md /home/_README.md
fi

# Copy base requirements for visibility to user what is installed by default in
# image and add warning header.
cp /assets/requirements-base.txt /home/requirements-base.txt
echo 'NOTE:\n
These packages are installed by default and this file is reset upon Sandbox restart!\n
Use requirements-override.txt to add new packages or overwrite versions!\n\n
'"$(cat /home/requirements-base.txt)" > /home/requirements-base.txt

# If an requirements-override.txt exists, run pip upgrade. Otherwise create
# empty file.
if [ ! -f /home/requirements-override.txt ]; then
    touch /home/requirements-override.txt
fi

# Download and install packages from requirements-override.txt
/assets/pip_download_install.sh /home/requirements-override.txt /home/pip_overwrite_requirements_download

# Run the CMD as the main container process
exec "$@"
