ARG GDAL_VERSION=3.12.2
ARG POSTGRESQL_CLIENT_VERSION=18

# Base image already bundles the OSGeo toolchain for the selected GDAL version.
# We layer Python/R runtime pieces on top instead of rebuilding geospatial C libs.
FROM ghcr.io/osgeo/gdal:ubuntu-small-${GDAL_VERSION} AS base

LABEL description="Python/JupyterLab instance with various Python geoprocessing components \
    (GeoPandas, GDAL bindings, rasterio, ...) and R geospatial components \
    (sf, terra, stars, ...) neatly working together."

#-----------------
# Base runtime dependencies
# Keep one shared runtime foundation reused by later stages to reduce rebuild time.
#-----------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    lsb-release \
    ca-certificates && \
    # pgdg gives us a predictable PostgreSQL client version across Ubuntu releases.
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    wget -q -O /etc/apt/trusted.gpg.d/pgdg.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
    arch="$(dpkg --print-architecture)" && \
    release="$(lsb_release -cs)" && \
    # CRAN repo provides current R binaries for Ubuntu.
    wget -q -O- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc > /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc && \
    echo "deb [arch=${arch}] https://cloud.r-project.org/bin/linux/ubuntu ${release}-cran40/" > /etc/apt/sources.list.d/cran-r.list && \
    # Prefer r2u binaries on arm64/noble to avoid costly source builds for most R packages.
    if [ "$arch" = "arm64" ] && [ "$release" = "noble" ]; then \
        wget -q -O- https://eddelbuettel.github.io/r2u/assets/dirk_eddelbuettel_key.asc > /etc/apt/trusted.gpg.d/cranapt_key.asc && \
        echo "deb [arch=${arch}] https://r2u.stat.illinois.edu/ubuntu ${release} main" > /etc/apt/sources.list.d/cranapt.list && \
        printf 'Package: *\nPin: release o=CRAN-Apt Project\nPin: release l=CRAN-Apt Packages\nPin-Priority: 700\n' > /etc/apt/preferences.d/99cranapt; \
    fi && \
    apt-get update && \
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
    wget \
    lsb-release && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#-----------------
# Python builder
# Compile wheels and heavy Python deps in a disposable stage; copy only venv to runtime.
#-----------------
FROM base AS python-builder

COPY ./copy_to_image/requirements-python-preinstalled.txt /tmp/requirements-python.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    python3-dev \
    libgeos-dev && \
    # Dedicated venv keeps Python deps isolated and portable across stages.
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
# R sf builder
# r2u sf/lwgeom binaries may be linked against different GDAL/PROJ versions.
# Building from source here guarantees linkage to the OSGeo stack in this image.
# ubuntu-full is required for headers/tools (gdal-config) missing in ubuntu-small.
#-----------------
FROM ghcr.io/osgeo/gdal:ubuntu-full-${GDAL_VERSION} AS r-sf-builder

# Use OSGeo's internal PROJ first to avoid dual-PROJ symbol conflicts while
# source-installing and loading sf/lwgeom in this stage.
ENV LD_PRELOAD=/usr/local/lib/libinternalproj.so.25

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        lsb-release \
        ca-certificates && \
    arch="$(dpkg --print-architecture)" && \
    release="$(lsb_release -cs)" && \
    wget -q -O- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc \
        > /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc && \
    echo "deb [arch=${arch}] https://cloud.r-project.org/bin/linux/ubuntu ${release}-cran40/" \
        > /etc/apt/sources.list.d/cran-r.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        r-base \
        r-base-dev \
        libgeos-dev \
        libproj-dev \
        libudunits2-dev \
        libssl-dev \
        libcurl4-openssl-dev \
        cmake && \
    # Quick sanity output in build logs when debugging version drift.
    gdal-config --version && \
    Rscript -e "\
        pkgs <- c('sf', 'lwgeom'); \
        # --no-test-load avoids transient linker/test issues during install; we load explicitly below.
        install.packages(pkgs, lib = '/usr/lib/R/library', repos = 'https://cloud.r-project.org', type = 'source', INSTALL_opts = '--no-test-load'); \
        stopifnot(all(pkgs %in% rownames(installed.packages(lib.loc = '/usr/lib/R/library')))); \
        suppressPackageStartupMessages(library(sf, lib.loc = '/usr/lib/R/library')); \
        suppressPackageStartupMessages(library(lwgeom, lib.loc = '/usr/lib/R/library'))" && \
    # Guardrail: fail early if sf is not linked to the expected GDAL ABI.
    sfso="$(Rscript -e "cat(system.file('libs','sf.so',package='sf'))")" && \
    ldd "$sfso" | grep -E 'libgdal' && \
    ldd "$sfso" | grep -q 'libgdal.so.38' && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

#-----------------
# Final runtime image
# Start from the slim base, then add Python venv + validated R packages.
#-----------------
FROM base AS runtime

ENV PATH="/opt/venv/bin:$PATH"
ENV R_LIBS_USER=/opt/r-lib
ENV SHELL=/bin/bash
ENV HOME=/home/sandbox
# Point IPython at the writable sandbox volume instead of the immutable home dir.
ENV IPYTHONDIR=/sandbox/.ipython

RUN groupadd sandbox && \
    useradd --gid sandbox --create-home --shell /bin/bash sandbox && \
    # Central writable workspace shared by notebook sessions.
    install -d -o sandbox -g sandbox /sandbox

COPY --chown=sandbox:sandbox ./copy_to_image/requirements-python-preinstalled.txt /sandbox/requirements-python-preinstalled.txt
COPY --chown=sandbox:sandbox ./copy_to_image/requirements-r-preinstalled.txt /sandbox/requirements-r-preinstalled.txt

COPY --from=python-builder --chown=sandbox:sandbox /opt/venv /opt/venv

# Install R requirements from apt when available (fast path via r2u), then
# verify all required packages are present before overriding sf/lwgeom.
RUN awk 'NF && $1 !~ /^#/{print $1}' /sandbox/requirements-r-preinstalled.txt > /tmp/requirements-r-clean.txt && \
    apt-get update && \
    apt_candidates="$(awk '{print "r-cran-" tolower($0)}' /tmp/requirements-r-clean.txt | tr '\n' ' ')" && \
    apt_installable="" && \
    for pkg in $apt_candidates; do \
        if apt-cache show "$pkg" >/dev/null 2>&1; then \
            apt_installable="$apt_installable $pkg"; \
        fi; \
    done && \
    if [ -z "$apt_installable" ]; then \
        echo "No installable R apt packages found" >&2; \
        exit 1; \
    fi && \
    # Bulk-install all available r-cran-* packages first for speed and reproducibility.
    apt-get install -y --no-install-recommends $apt_installable && \
    Rscript -e "\
        pkgs <- unique(scan('/tmp/requirements-r-clean.txt', what = 'character', quiet = TRUE)); \
        installed <- rownames(installed.packages()); \
        missing <- setdiff(pkgs, installed); \
        if (length(missing)) stop(sprintf('Missing required R packages after apt install: %s', paste(missing, collapse = ', '))); \
        suppressPackageStartupMessages(library(sf)); \
        print(sf::sf_extSoftVersion())" && \
    # Catch unresolved shared libraries before image finalization.
    ldd "$(Rscript -e "cat(system.file('libs', 'sf.so', package = 'sf'))")" | tee /tmp/sf-ldd.txt && \
    ! grep -q 'not found' /tmp/sf-ldd.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/requirements-r-clean.txt /tmp/sf-ldd.txt

# Critical override: site-library is first in .libPaths(), so place source-built
# packages there to shadow r2u binaries and enforce GDAL/PROJ alignment at runtime.
COPY --from=r-sf-builder /usr/lib/R/library/sf     /usr/lib/R/site-library/sf
COPY --from=r-sf-builder /usr/lib/R/library/lwgeom /usr/lib/R/site-library/lwgeom

# Final linkage assertions in runtime image.
RUN sfso="$(Rscript -e "cat(system.file('libs','sf.so',package='sf'))")" && \
    echo "sf.so: $sfso" && \
    ldd "$sfso" | grep -E 'gdal|geos|proj' && \
    ldd "$sfso" | grep -q 'libgdal.so.38' && \
    ! ldd "$sfso" | grep -q 'not found' && \
    lwso="$(Rscript -e "cat(system.file('libs','lwgeom.so',package='lwgeom'))")" && \
    echo "lwgeom.so: $lwso" && \
    ldd "$lwso" | grep -E 'proj' && \
    ! ldd "$lwso" | grep -q 'not found'

# Register R kernel.
# Scope the PROJ preload to the R kernel only: R needs it to avoid a dual-PROJ
# crash in sf/lwgeom, while Python's pyproj/pyogrio crash if it is global.
RUN Rscript -e "IRkernel::installspec(name = 'ir', displayname = 'R', user = FALSE, prefix = '/opt/venv')" && \
    python3 -c "import json, pathlib; p = pathlib.Path('/opt/venv/share/jupyter/kernels/ir/kernel.json'); data = json.loads(p.read_text()); data.setdefault('env', {})['LD_PRELOAD'] = '/usr/local/lib/libinternalproj.so.25'; p.write_text(json.dumps(data, indent=2))"

WORKDIR /sandbox
USER sandbox

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--autoreload"]
