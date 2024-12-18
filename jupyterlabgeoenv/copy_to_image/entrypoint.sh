#!/bin/bash


if $HOME_DIR_PERSISTED
then
    # Copy readme explaining persistence and overwrite procedure.
    cp /assets/_README.md /sandbox/_README.md
fi

# Activate the python virtual environment
source /opt/venv/bin/activate

# Deactivate extension manager (extension should only be installed from pypi via
# requirements-override.txt)
jupyter labextension disable @jupyterlab/extensionmanager-extension

# Copy base requirements for visibility to user what is installed by default in
# image and add warning header.
cp /assets/requirements-base.txt /sandbox/requirements-base.txt
echo '# NOTE:
# These packages are installed by default and this file is reset upon Sandbox restart!
# Use requirements-override.txt to add new packages.
'"$(cat /sandbox/requirements-base.txt)" > /sandbox/requirements-base.txt

# If an requirements-override.txt exists, run pip upgrade. Otherwise create
# empty file.
if [ ! -f /sandbox/requirements-override.txt ]; then
touch /sandbox/requirements-override.txt
echo '# NOTE:
# Use this requirements file to add new Python packages.
# This file is processed by pip upon each Sandbox start.
# The more packages are added here, the longer the startup time.
# Internet connection is only required the first time after changing this
# file, further startups will use downloaded versions of the packages.
'"$(cat /sandbox/requirements-override.txt)" > /sandbox/requirements-override.txt
fi

# Download and install packages from requirements-override.txt into /pip_overwrite_requirements_download.
/assets/pip_download_install.sh /sandbox/requirements-override.txt /pip_overwrite_requirements_download

# Run the CMD as the main container process
exec "$@"
