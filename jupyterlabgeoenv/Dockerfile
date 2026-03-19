ARG GDAL_VERSION=3.12.2
ARG POSTGRESQL_CLIENT_VERSION=18
ARG R_BUILD_JOBS=0

FROM ghcr.io/osgeo/gdal:ubuntu-small-${GDAL_VERSION} AS base

LABEL description="Python/JupyterLab instance with various Python geoprocessing components \
    (GeoPandas, GDAL bindings, rasterio, ...) and R geospatial components \
    (sf, terra, stars, ...) neatly working together."

#-----------------
# Base runtime dependencies
#-----------------
RUN apt update && \
    apt-get install -y --no-install-recommends \
    gnupg2 \
    wget \
    lsb-release \
    ca-certificates && \
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt update && \
    apt-get install -y --no-install-recommends \
    postgresql-client=${POSTGRESQL_CLIENT_VERSION}* \
    python3 \
    python3-pip \
    python3-venv \
    r-base \
    \
    # runtime libs for R packages
    libudunits2-0 \
    libxml2 \
    libcurl4 \
    libssl3 \
    libsqlite3-0 \
    libnetcdf19 \
    libzmq5 \
    libgomp1 && \
    \
    apt-get purge -y \
    gnupg2 \
    wget \
    lsb-release && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#-----------------
# Python builder
#-----------------
FROM base AS python-builder

COPY ./copy_to_image/requirements-python-preinstalled.txt /tmp/requirements-python.txt

RUN apt update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    python3-dev \
    libgeos-dev && \
    python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements-python.txt && \
    apt-get purge -y \
    build-essential \
    gfortran \
    python3-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/requirements-python.txt

#-----------------
# R builder
#-----------------
FROM base AS r-builder

COPY ./copy_to_image/requirements-r-preinstalled.txt /tmp/requirements-r.txt

ENV R_LIBS_USER=/opt/r-lib

RUN mkdir -p /opt/r-lib && \
    apt update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    cmake \
    r-base-dev \
    pkg-config \
    \
    # geospatial core
    libgeos-dev \
    libproj-dev \
    libudunits2-dev \
    libtbb-dev \
    libsqlite3-dev \
    \
    # raster / cubes
    libnetcdf-dev \
    \
    # database
    libpq-dev \
    \
    # general
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libfontconfig1-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff5-dev && \
    Rscript -e "\
        options(repos = c(CRAN = 'https://cloud.r-project.org'), pkgType = 'source'); \
        pkgs <- trimws(gsub('#.*$', '', readLines('/tmp/requirements-r.txt'))); \
        pkgs <- unique(pkgs[pkgs != '']); \
        jobs <- as.integer(Sys.getenv('R_BUILD_JOBS', '0')); \
        if (is.na(jobs) || jobs < 1L) jobs <- min(2L, max(1L, parallel::detectCores() - 1L)); \
        install.packages(pkgs, dependencies = NA, Ncpus = jobs, INSTALL_opts = c('--no-test-load')); \
        installed <- rownames(installed.packages(lib.loc = '/opt/r-lib')); \
        missing <- setdiff(pkgs, installed); \
        if (length(missing)) stop(sprintf('Failed to install required R packages: %s', paste(missing, collapse = ', ')))" && \
    apt-get purge -y \
    build-essential \
    gfortran \
    cmake \
    r-base-dev \
    pkg-config \
    libgeos-dev \
    libproj-dev \
    libudunits2-dev \
    libtbb-dev \
    libsqlite3-dev \
    libnetcdf-dev \
    libpq-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libfontconfig1-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff5-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/requirements-r.txt

#-----------------
# Final runtime image
#-----------------
FROM base AS runtime

ENV PATH="/opt/venv/bin:$PATH"
ENV R_LIBS_USER=/opt/r-lib
ENV SHELL=/bin/bash
ENV HOME=/home/sandbox

RUN groupadd sandbox && \
    useradd --gid sandbox --create-home --shell /bin/bash sandbox && \
    install -d -o sandbox -g sandbox /sandbox

COPY --chown=sandbox:sandbox ./copy_to_image/requirements-python-preinstalled.txt /sandbox/requirements-python-preinstalled.txt
COPY --chown=sandbox:sandbox ./copy_to_image/requirements-r-preinstalled.txt /sandbox/requirements-r-preinstalled.txt

COPY --from=python-builder --chown=sandbox:sandbox /opt/venv /opt/venv
COPY --from=r-builder --chown=sandbox:sandbox /opt/r-lib /opt/r-lib

# Register R kernel
RUN Rscript -e "IRkernel::installspec(name = 'ir', displayname = 'R', user = FALSE, prefix = '/opt/venv')"

WORKDIR /sandbox
USER sandbox

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--autoreload"]
