ARG GDAL_VERSION=3.12.2
ARG POSTGRESQL_CLIENT_VERSION=18

FROM ghcr.io/osgeo/gdal:ubuntu-small-${GDAL_VERSION}

LABEL description="Python/JupyterLab instance with various Python geoprocessing components \
    (GeoPandas, GDAL bindings, rasterio, ...) neatly working together."

# Create sandbox directory
RUN mkdir /sandbox

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
COPY ./copy_to_image/requirements-preinstalled.txt /sandbox/requirements-preinstalled.txt


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
    pip install --no-cache-dir -r /sandbox/requirements-preinstalled.txt

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
# Create dedicated non-root runtime user for JupyterLab.
# Do not pin UID/GID here because the base image may already use common IDs.
RUN groupadd sandbox && \
    useradd --gid sandbox --create-home --shell /bin/bash sandbox && \
    chown -R sandbox:sandbox /sandbox /home/sandbox /opt/venv

# Make sure jupyter lab terminal uses bash
ENV SHELL=/bin/bash
ENV HOME=/home/sandbox

WORKDIR /sandbox

USER sandbox

CMD ["jupyter", "lab" ,"--ip=0.0.0.0", "--port=8888", "--no-browser", "--autoreload"]
