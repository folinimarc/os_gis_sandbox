FROM ubuntu:focal-20220404

LABEL description="Python/JupyterLab instance with various python geoprocessing components \
(geopandas, gdal bindings, rasterio, ...) neatly working together."

ARG GDAL_VERSION=3.4.0
ARG POSTGRESQL_CLIENT_VERSION=14
ARG NODEJS_VERSION=18

# Use default anywhere without requiring intervention
ARG DEBIAN_FRONTEND=noninteractive

#-----------------
# Timezone config
#-----------------
# To avoid interactive configuration prompt when installing tzdata later, set TZ
# variable here.
# Kudos to https://rtfm.co.ua/en/docker-configure-tzdata-and-timezone-during-build/
ENV TZ=Europe/Zurich
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#-----------------
# GDAL, GEOS, PROJ (via libgdal-dev)
#-----------------

RUN apt update && \
    apt-get install -y --no-install-recommends \
        tzdata \
        software-properties-common && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
RUN apt update && \
    apt-get install -y --no-install-recommends \
        gdal-bin=${GDAL_VERSION}* \
        libgdal-dev=${GDAL_VERSION}*

#-----------------
# Postgresql 14 client (psql command line)
#-----------------

# Kudos to https://techviewleo.com/how-to-install-postgresql-database-on-ubuntu/
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

# According to "install GDAL for python section"
# https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html
ARG CPLUS_INCLUDE_PATH=/usr/include/gdal
ARG C_INCLUDE_PATH=/usr/include/gdal

# Install python-dev (required for gdal bindings it seems).
# Append GDAL with correct version to requirements-base.txt.
# Add directive for shapely and pygeos to use existing library (requires build-essentials).
RUN apt update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        python3-pip
RUN echo "GDAL==${GDAL_VERSION}" >> /assets/requirements-base.txt && \
    echo "--no-binary=shapely,pygeos" >> /assets/requirements-base.txt && \
    pip install --upgrade pip && \
    pip install -r /assets/requirements-base.txt

#-----------------
# Final clean up
#-----------------
RUN apt purge -y \
        software-properties-common \
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
# if SHOW_README_IN_HOME is true. Defaults to false for the docker standalone usecase without volume.
ENV SHOW_README_IN_HOME=false
COPY ./copy_to_image/_README.md /assets/_README.md

# Copy entrypoint and make executable
COPY ./copy_to_image/entrypoint.sh /assets/entrypoint.sh
RUN chmod 0700 /assets/entrypoint.sh

WORKDIR /home

ENTRYPOINT ["/assets/entrypoint.sh"]
CMD ["jupyter", "lab" ,"--ip=0.0.0.0", "--port=8888", "--allow-root", "--no-browser", "--autoreload"]
