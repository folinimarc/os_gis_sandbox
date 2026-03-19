import json, pathlib

NB = {
  "nbformat": 4,
  "nbformat_minor": 5,
  "metadata": {
    "kernelspec": {"display_name": "R", "language": "R", "name": "ir"},
    "language_info": {"name": "R"}
  },
  "cells": [
    {
      "cell_type": "markdown",
      "id": "nb-md-intro",
      "metadata": {},
      "source": "# R GIS Ecosystem Demo: Vector, Raster, Interpolation, and Interactive Maps\n\nA non-trivial geospatial workflow demonstrating:\n\n- **Vector analysis**: `sf`, `lwgeom`, `s2`\n- **Raster analysis**: `terra`, `stars`\n- **Spatial interpolation**: `gstat`\n- **Visualization**: `ggplot2`, `tmap`, `leaflet`, `mapview`\n\nAll data is sourced from R package datasets (`sf::nc`, `datasets::volcano`, `sp::meuse`) — no external downloads needed."
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-libs",
      "metadata": {},
      "outputs": [],
      "source": "suppressPackageStartupMessages({\n  library(sf)\n  library(dplyr)\n  library(ggplot2)\n  library(lwgeom)\n  library(s2)\n  library(terra)\n  library(stars)\n  library(gstat)\n  library(tmap)\n  library(leaflet)\n  library(mapview)\n})\n\ncat(\"sf external software versions:\\n\")\nprint(sf::sf_extSoftVersion())"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s1",
      "metadata": {},
      "source": "## 1. Load and Inspect Vector Data (`sf::nc`)"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-load-nc",
      "metadata": {},
      "outputs": [],
      "source": "nc <- st_read(system.file(\"shape/nc.shp\", package = \"sf\"), quiet = TRUE)\n\ncat(\"Rows:\", nrow(nc), \"\\n\")\ncat(\"CRS:\", st_crs(nc)$input, \"\\n\")\nprint(head(st_drop_geometry(nc), 3))"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-plot-nc",
      "metadata": {},
      "outputs": [],
      "source": "ggplot(nc) +\n  geom_sf(aes(fill = SID74)) +\n  scale_fill_viridis_c(option = \"C\") +\n  labs(title = \"North Carolina SIDS counts (1974)\", fill = \"SID74\") +\n  theme_minimal()"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s2",
      "metadata": {},
      "source": "## 2. CRS Transform and Geometry-Derived Metrics"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-metrics",
      "metadata": {},
      "outputs": [],
      "source": "# Project to NC State Plane (EPSG:32119, metres) before computing area/perimeter.\nnc_32119 <- st_transform(nc, 32119)\n\nnc_metrics <- nc_32119 |>\n  mutate(\n    area_km2          = as.numeric(st_area(geometry)) / 1e6,\n    perimeter_km      = as.numeric(lwgeom::st_perimeter(geometry)) / 1e3,\n    sid74_rate_per1k  = SID74 / BIR74 * 1000,\n    compactness_ratio = (4 * pi * area_km2) / perimeter_km^2\n  )\n\nsummary(nc_metrics[, c(\"area_km2\", \"perimeter_km\", \"sid74_rate_per1k\", \"compactness_ratio\")])"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-plot-metrics",
      "metadata": {},
      "outputs": [],
      "source": "ggplot(nc_metrics) +\n  geom_sf(aes(fill = sid74_rate_per1k), color = \"white\", linewidth = 0.2) +\n  scale_fill_viridis_c(option = \"D\") +\n  labs(title = \"Sudden Infant Death Syndrome rate per 1 000 births (1974)\",\n       fill = \"Rate\") +\n  theme_minimal()"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s3",
      "metadata": {},
      "source": "## 3. Spatial Predicates and Nearest-Neighbour Analysis (`s2` geometry engine)"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-nn",
      "metadata": {},
      "outputs": [],
      "source": "# Great-circle nearest-neighbour distances between county centroids.\ncent <- st_centroid(st_geometry(nc))\n\nnn_idx <- st_nearest_feature(cent, cent)\nself   <- seq_len(length(cent))\n# Avoid self-match\nnn_idx <- ifelse(nn_idx == self, ifelse(self == 1L, 2L, 1L), nn_idx)\n\ndist_km <- as.numeric(st_distance(cent, cent[nn_idx], by_element = TRUE)) / 1e3\n\nnn_tbl <- tibble::tibble(\n  county         = nc$NAME,\n  nearest_county = nc$NAME[nn_idx],\n  dist_km        = round(dist_km, 2)\n)\n\nprint(dplyr::arrange(nn_tbl, dist_km) |> head(10))"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s4",
      "metadata": {},
      "source": "## 4. Raster Processing from `datasets::volcano`"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-terra",
      "metadata": {},
      "outputs": [],
      "source": "r_elev <- rast(volcano)\next(r_elev)   <- ext(0, ncol(volcano), 0, nrow(volcano))\ncrs(r_elev)   <- \"EPSG:3857\"\nnames(r_elev) <- \"elevation\"\n\nslope     <- terrain(r_elev, v = \"slope\",  unit = \"radians\")\naspect    <- terrain(r_elev, v = \"aspect\", unit = \"radians\")\nhillshade <- shade(slope, aspect)\n\npar(mfrow = c(1, 3), mar = c(3, 3, 2, 5))\nplot(r_elev,    main = \"Elevation (volcano dataset)\")\nplot(slope,     main = \"Slope (radians)\")\nplot(hillshade, main = \"Hillshade\")\npar(mfrow = c(1, 1))"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s5",
      "metadata": {},
      "source": "## 5. Vector–Raster Integration: Zonal Statistics on Generated Tiles"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-zonal",
      "metadata": {},
      "outputs": [],
      "source": "tiles   <- makeTiles(r_elev, n = 16)\ntile_sf <- st_as_sf(as.polygons(tiles))\ntile_sf$tile_id <- seq_len(nrow(tile_sf))\n\nzstats          <- terra::extract(r_elev, vect(tile_sf), fun = mean, na.rm = TRUE, ID = FALSE)\ntile_sf$mean_elevation <- zstats$elevation\n\nggplot(tile_sf) +\n  geom_sf(aes(fill = mean_elevation), color = \"grey40\", linewidth = 0.3) +\n  scale_fill_viridis_c(option = \"C\") +\n  labs(title = \"Mean elevation per tile\", fill = \"Mean elev. (m)\") +\n  theme_minimal()"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s6",
      "metadata": {},
      "source": "## 6. Spatial Interpolation with `gstat` (IDW on `sp::meuse`)"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-idw",
      "metadata": {},
      "outputs": [],
      "source": "data(meuse, package = \"sp\")\nmeuse_sf <- st_as_sf(meuse, coords = c(\"x\", \"y\"), crs = 28992)\n\npred_grid <- st_make_grid(meuse_sf, cellsize = 100, what = \"centers\") |>\n  st_as_sf()\n\nidw_out <- gstat::idw(\n  formula   = zinc ~ 1,\n  locations = meuse_sf,\n  newdata   = pred_grid,\n  idp       = 2.0\n)\n\nggplot() +\n  geom_sf(data = idw_out, aes(color = var1.pred), size = 0.7, alpha = 0.85) +\n  geom_sf(data = meuse_sf, color = \"black\", size = 0.6, shape = 3) +\n  scale_color_viridis_c(option = \"B\") +\n  labs(title = \"IDW interpolation — zinc concentration (meuse dataset)\",\n       color = \"Predicted Zn (ppm)\") +\n  theme_minimal()"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s7",
      "metadata": {},
      "source": "## 7. `stars` — Spatiotemporal Arrays"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-stars",
      "metadata": {},
      "outputs": [],
      "source": "s_volcano <- st_as_stars(r_elev)\nprint(s_volcano)\n\nplot(s_volcano, main = \"Maungawhau / Mt Eden — elevation as stars object\")"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s8",
      "metadata": {},
      "source": "## 8. Interactive Visualization (`tmap`, `leaflet`, `mapview`)"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-tmap",
      "metadata": {},
      "outputs": [],
      "source": "tmap_mode(\"plot\")\ntm_shape(nc_metrics) +\n  tm_polygons(\"sid74_rate_per1k\", palette = \"viridis\",\n              title = \"SID rate / 1000 births\") +\n  tm_layout(title = \"tmap static choropleth — North Carolina\")"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-leaflet",
      "metadata": {},
      "outputs": [],
      "source": "nc_wgs84 <- st_transform(nc_metrics, 4326)\npal <- colorNumeric(\"viridis\", domain = nc_wgs84$sid74_rate_per1k)\n\nleaflet(nc_wgs84) |>\n  addProviderTiles(\"CartoDB.Positron\") |>\n  addPolygons(\n    fillColor  = ~pal(sid74_rate_per1k),\n    fillOpacity = 0.8,\n    color       = \"#333\",\n    weight      = 0.6,\n    popup       = ~paste0(\"<b>\", NAME, \"</b><br>SID rate: \",\n                          round(sid74_rate_per1k, 2))\n  ) |>\n  addLegend(pal = pal, values = ~sid74_rate_per1k,\n            title = \"SID rate / 1000 births\")"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-mapview",
      "metadata": {},
      "outputs": [],
      "source": "mapview(nc_wgs84, zcol = \"sid74_rate_per1k\",\n        layer.name = \"SID rate / 1000 births\")"
    },
    {
      "cell_type": "markdown",
      "id": "nb-md-s9",
      "metadata": {},
      "source": "## 9. Persist Results as Parquet (`arrow`)"
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "id": "nb-r-arrow",
      "metadata": {},
      "outputs": [],
      "source": "attrs <- st_drop_geometry(nc_metrics)\narrow::write_parquet(attrs, \"/sandbox/nc_metrics_attributes.parquet\")\ncat(\"Wrote\", nrow(attrs), \"rows\\n\")\n\nback <- arrow::read_parquet(\"/sandbox/nc_metrics_attributes.parquet\")\nstopifnot(nrow(back) == nrow(attrs))\ncat(\"Round-trip OK — columns:\", paste(names(back), collapse = \", \"), \"\\n\")"
    }
  ]
}

out = pathlib.Path("/Users/siili/coding/repos/os_gis_sandbox/content/copy_to_image/content_root/tutorials_jupyterlabgeoenv/004_r_gis_ecosystem_demo.ipynb")
out.write_text(json.dumps(NB, indent=2))
print(f"Written {len(NB['cells'])} cells, {out.stat().st_size} bytes to {out}")
