FROM python:3.9-slim@sha256:f4efbe5d1eb52c221fded79ddf18e4baa0606e7766afe2f07b0b330a9e79564a

LABEL description="Various python geoprocessing components \
(geopandas, gdal bindings, rasterio, ...) with dependencies neatly working together."

# Install GDAL, GEOS, PROJ (libgdal-dev will install libgeos-dev & libproj-dev)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    binutils=2.35.2-2 \
    build-essential=12.9 \
    libgdal-dev=3.2.2+dfsg-2+deb11u1 \
    gdal-bin=3.2.2+dfsg-2+deb11u1 \
    # Install postgres 13 client
    postgresql-client=13+225 \
    # Clean up
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install python packages for geoprocessing and workflow
# ------------------------------------------------------
# Shapely: Does planar geometric processing (uses GEOS).
# Pygeos: Newer sibling to shapely with focus on performance. Will be integrated in shapely 2.0.
# Fiona: Reads and writes everything (uses OGR).
# Pyproj: Handles projections (uses PROJ).
# Rtree: Spatial indexing (plays well with geopandas).
# Openpyxl: Is required by geopandas to write excel files.
# Matplotlib: Is required by geopandas to visualize geometries.
# Mapclassify: Utility package for classification schemes for Choropleth Maps. Used by geopandas for GeoDataFrame.explore().
# Folium: Provides interactive plotting capbilities. Used by geopandas for GeoDataFrame.explore().
# Geopandas: Extends pandas with geospatial capabilities (uses shapely, pygeos, fiona, pyproj, Rtree, ...)
# Gdal: Low level gdal python bindings. More a nice-to-have as there are higher level packages like rasterio for interacting with gdal.
# Rasterio Makes working with rasters fun (uses GDAL).
# Xarray: Deals with multidimensional data. Ideal to read/writes netCDF files.
# Xarray-spatial: Extends xarray with powerful spatial processing capabilities without depending on GDAL.
# Xarray[io]: Various io plugins to read/write data in xarray, e.g. netCDF, GRIB,...
# Ecmwflibs: Install because of bug in xarray[io] as of 20210104, but in future xarray[io] should suffice.
# Rioxarray: Extension of xarray to seamlessly interface with rasterio for 2D raster data.
# Jupyterlab: Allows to write rich scripts (notebooks) and run code interactively in the browser.
# Pysal: A collection of packages for advanced geospatial statistical modelling and visualization.
# ------------------------------------------------------
RUN mkdir /setup
COPY ./requirements.txt /setup/requirements.txt
# Shapely and pygeos should use the existing GEOS library.
# Append this line to requirements.txt as pip freeze does not account for it.
RUN echo "--no-binary=shapely,pygeos" >> /setup/requirements.txt && \
    pip install --upgrade pip && \
    pip install -r /setup/requirements.txt

# TODO
# Install QGIS and make PyQGIS available in notebooks as kernel.
# Judging from first research this is going to be non-trivial.

# Setup to run jupyterlab when starting container.
COPY ./start_jupyter.sh /setup/start_jupyter.sh
RUN ["chmod", "+x", "/setup/start_jupyter.sh"]

RUN mkdir /geo
WORKDIR /geo

# Copy examples into container
COPY ./examples ./examples

CMD ["/setup/start_jupyter.sh"]
