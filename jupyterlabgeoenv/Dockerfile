ARG GDAL_VERSION=3.8.1
ARG POSTGRESQL_CLIENT_VERSION=16.1

FROM ghcr.io/osgeo/gdal:ubuntu-small-${GDAL_VERSION}

LABEL description="Python/JupyterLab instance with various Python geoprocessing components \
    (GeoPandas, GDAL bindings, rasterio, ...) neatly working together."

# #-----------------
# # Postgresql 14 client (psql command line)
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

# Install python packages.
# Add directive for shapely and pygeos to use existing
# library (requires python3-dev and build-essentials).
RUN apt update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-pip \
    libgeos-dev
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
