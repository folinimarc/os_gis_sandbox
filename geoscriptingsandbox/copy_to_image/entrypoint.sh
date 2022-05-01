#!/bin/sh


if $SHOW_README_IN_HOME
then
    # Copy readme explaining persistence and overwrite procedure.
    cp /assets/_README.md /home/_README.md
fi

# Copy base requirements for visibility to user what is installed by default in
# image and add warning header.
cp /assets/requirements-base.txt /home/requirements-base.txt
echo 'NOTE: This file is reset upon Sandbox restart! Use requirements-override.txt to add new packages or overwrite versions!\n\n'"$(cat /home/requirements-base.txt)" > /home/requirements-base.txt

# If an requirements-override.txt exists, run pip upgrade. Otherwise create
# empty file.
if [ -f /home/requirements-override.txt ]; then
    pip install --upgrade -r /home/requirements-override.txt
else
    touch /home/requirements-override.txt
fi

# Run the CMD as the main container process
exec "$@"
