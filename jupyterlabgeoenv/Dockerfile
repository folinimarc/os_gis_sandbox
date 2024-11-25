ARG GDAL_VERSION=3.9.3
ARG POSTGRESQL_CLIENT_VERSION=17

FROM ghcr.io/osgeo/gdal:ubuntu-small-${GDAL_VERSION}

LABEL description="Python/JupyterLab instance with various Python geoprocessing components \
    (GeoPandas, GDAL bindings, rasterio, ...) neatly working together."

# #-----------------
# # Postgresql client (psql command line)
# #-----------------
# # Kudos to https://techviewleo.com/how-to-install-postgresql-database-on-ubuntu/
RUN apt update && \
    apt-get install -y --no-install-recommends \
    gnupg2 \
    wget \
    lsb-release && \
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt update && \
    apt-get install -y --no-install-recommends \
    postgresql-client=${POSTGRESQL_CLIENT_VERSION}*

#-----------------
# Python & PIP & Packages
#-----------------
# Copy requirements
RUN mkdir /assets
COPY ./copy_to_image/requirements-base.txt /assets/requirements-base.txt

# Install dependencies and create a Python virtual environment
RUN apt update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    libgeos-dev && \
    python3 -m venv /opt/venv

# Update PATH to use the virtual environment by default
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /assets/requirements-base.txt

#-----------------
# Final clean up
#-----------------
RUN apt purge -y \
    gnupg2 \
    wget \
    lsb-release && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#-----------------
# Misc setup
#-----------------
# Make sure jupyter lab terminal uses bash
ENV SHELL=/bin/bash
# Deactivate extension manager (extension should only be installed from pypi via
# requirements-override.txt)
RUN jupyter labextension disable @jupyterlab/extensionmanager-extension

# Copy readme about file persistence which will be copied to home directory in entrypoint.sh
# if HOME_DIR_PERSISTED is true. Defaults to false for the docker standalone usecase without volume.
ENV HOME_DIR_PERSISTED=false
COPY ./copy_to_image/_README.md /assets/_README.md

# Copy pip installation and entrypoint scripts and make both executable.
COPY ./copy_to_image/entrypoint.sh /assets/entrypoint.sh
RUN chmod 0700 /assets/entrypoint.sh
COPY ./copy_to_image/pip_download_install.sh /assets/pip_download_install.sh
RUN chmod 0700 /assets/pip_download_install.sh

WORKDIR /home

ENTRYPOINT ["/assets/entrypoint.sh"]
CMD ["jupyter", "lab" ,"--ip=0.0.0.0", "--port=8888", "--allow-root", "--no-browser", "--autoreload"]
