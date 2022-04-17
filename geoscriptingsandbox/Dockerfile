FROM ubuntu:focal-20220404

LABEL description="Python/JupyterLab instance with various python geoprocessing components \
(geopandas, gdal bindings, rasterio, ...) neatly working together."

ARG GDAL_VERSION=3.4.0
ARG POSTGRESQL_CLIENT_VERSION=14

# Preparation: Add ubuntugis ppa (for gdal, geos, proj)
RUN DEBIAN_FRONTEND=noninteractive && \
    apt update && \
    apt-get install -y --no-install-recommends \
        tzdata software-properties-common && \
    add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable

# Preparation: Add repo for postgres 14 client
# Kudos to https://techviewleo.com/how-to-install-postgresql-database-on-ubuntu/
RUN DEBIAN_FRONTEND=noninteractive && \
    apt update && \
    apt-get install -y --no-install-recommends \
        gnupg2 wget lsb-release && \
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# Preparation: Ability to compile python packages (e.g. pygeos against existing geos)
RUN DEBIAN_FRONTEND=noninteractive && \
    apt update && \
    apt-get install -y --no-install-recommends \
    build-essential python3-dev

# Main install:
# - gdal, geos, proj
# - postgresql 14 client
# - python3-dev (e.g. for compiling pygeos against existing geos)
# - pip
RUN DEBIAN_FRONTEND=noninteractive && \
    apt update && \
    # Note: geos, proj installed by libgdal-dev.
    apt-get install -y --no-install-recommends \
        gdal-bin=${GDAL_VERSION}* \
        libgdal-dev=${GDAL_VERSION}* \
        postgresql-client=${POSTGRESQL_CLIENT_VERSION}* \
        python3-pip && \
    pip install --upgrade pip
# Clean up
RUN DEBIAN_FRONTEND=noninteractive && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# According to "install GDAL for python section"
# https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
# Install python packages
# - Copy requirements
# - Add GDAL with correct version
# - Add directive for shapely and pygeos to use existing library
# - Install from requirements.txt
RUN mkdir /setup
COPY ./requirements.txt /setup/requirements.txt
RUN echo "GDAL==${GDAL_VERSION}" >> /setup/requirements.txt && \
    echo "--no-binary=shapely,pygeos" >> /setup/requirements.txt && \
    pip install -r /setup/requirements.txt

# make sure jupyter lab terminal uses bash
ENV SHELL=/bin/bash

# Copy tutorial notebooks into image. Will be copied to /home/tutorial_notebooks in entrypoint.sh
COPY ./tutorial_notebooks /setup/tutorial_notebooks_img
COPY entrypoint.sh /setup
ENTRYPOINT ["/setup/entrypoint.sh"]

WORKDIR /home

CMD ["jupyter", "lab" ,"--ip=0.0.0.0", "--port=8888", "--allow-root", "--no-browser", "--autoreload"]
