import json
from pathlib import Path

out_path = Path("/Users/siili/coding/repos/os_gis_sandbox/content/copy_to_image/content_root/tutorials_jupyterlabgeoenv/005_python_gis_ecosystem_demo.ipynb")

cells = [
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "# Python GIS Ecosystem Demo: End-to-End Geospatial Workbench\n",
            "\n",
            "This notebook provides concise, practical demos across the Python GIS stack.\n",
            "\n",
            "It focuses on **offline-friendly examples** for reproducibility, and marks internet-dependent examples as optional.\n",
            "\n",
            "Covered packages include: `geopandas`, `shapely`, `pyogrio`, `fiona`, `pyproj`, `rasterio`, `xarray`, `rioxarray`, `rasterstats`, `pysal`, `pyarrow`, `sqlalchemy`, `geoalchemy2`, `folium`, `ipyleaflet`, `movingpandas`, `momepy`, `pystac`, `stackstac`, `osmnx`, `OWSLib`."
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "import json\n",
            "import warnings\n",
            "from pathlib import Path\n",
            "\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "import geopandas as gpd\n",
            "from shapely.geometry import Point, Polygon, LineString\n",
            "from shapely.ops import unary_union\n",
            "import pyproj\n",
            "\n",
            "import rasterio\n",
            "from rasterio.transform import from_origin\n",
            "from rasterio.io import MemoryFile\n",
            "import xarray as xr\n",
            "import rioxarray\n",
            "from rasterstats import zonal_stats\n",
            "\n",
            "from libpysal.weights import Queen\n",
            "from esda.moran import Moran\n",
            "\n",
            "import pyarrow as pa\n",
            "import pyarrow.parquet as pq\n",
            "from sqlalchemy import Table, Column, Integer, MetaData, select\n",
            "from geoalchemy2 import Geometry\n",
            "\n",
            "import folium\n",
            "from ipyleaflet import Map, GeoData\n",
            "import contextily as cx\n",
            "\n",
            "import movingpandas as mpd\n",
            "import momepy\n",
            "import networkx as nx\n",
            "\n",
            "import pystac\n",
            "\n",
            "np.random.seed(42)\n",
            "warnings.filterwarnings('ignore')"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# Quick environment snapshot\n",
            "versions = {\n",
            "    'geopandas': gpd.__version__,\n",
            "    'rasterio': rasterio.__version__,\n",
            "    'pyproj': pyproj.__version__,\n",
            "    'xarray': xr.__version__,\n",
            "}\n",
            "print(json.dumps(versions, indent=2))"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 1) Vector Modeling with GeoPandas + Shapely\n",
            "\n",
            "Create synthetic districts and observation points, then aggregate point measurements per district."
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# 4 square districts in a local metric CRS\n",
            "district_polys = [\n",
            "    Polygon([(0, 0), (1000, 0), (1000, 1000), (0, 1000)]),\n",
            "    Polygon([(1000, 0), (2000, 0), (2000, 1000), (1000, 1000)]),\n",
            "    Polygon([(0, 1000), (1000, 1000), (1000, 2000), (0, 2000)]),\n",
            "    Polygon([(1000, 1000), (2000, 1000), (2000, 2000), (1000, 2000)]),\n",
            "]\n",
            "districts = gpd.GeoDataFrame(\n",
            "    {'district': ['A', 'B', 'C', 'D']}, geometry=district_polys, crs='EPSG:3857'\n",
            ")\n",
            "\n",
            "# 150 random sensor points with synthetic PM2.5 signal\n",
            "pts = [Point(x, y) for x, y in np.random.uniform(0, 2000, size=(150, 2))]\n",
            "obs = gpd.GeoDataFrame(\n",
            "    {'pm25': np.random.gamma(shape=2.0, scale=8.0, size=150)}, geometry=pts, crs='EPSG:3857'\n",
            ")\n",
            "\n",
            "joined = gpd.sjoin(obs, districts, predicate='within', how='left')\n",
            "district_stats = joined.groupby('district', dropna=True).agg(pm25_mean=('pm25', 'mean'), n=('pm25', 'size')).reset_index()\n",
            "districts = districts.merge(district_stats, on='district', how='left')\n",
            "districts"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "ax = districts.plot(column='pm25_mean', cmap='viridis', edgecolor='black', legend=True, figsize=(6, 6))\n",
            "obs.plot(ax=ax, color='white', edgecolor='black', markersize=10, alpha=0.6)\n",
            "ax.set_title('District PM2.5 mean and monitoring points')\n",
            "ax.set_axis_off()"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 2) Geometry Operations and Morphology (Shapely)"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# Union districts and build a 150 m boundary buffer ring\n",
            "city = unary_union(districts.geometry)\n",
            "outer = city.buffer(150)\n",
            "ring = outer.difference(city)\n",
            "\n",
            "geom_demo = gpd.GeoDataFrame(\n",
            "    {'layer': ['city', 'buffer_ring'], 'area_m2': [city.area, ring.area]},\n",
            "    geometry=[city, ring],\n",
            "    crs=districts.crs,\n",
            ")\n",
            "geom_demo"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 3) CRS and Coordinate Transformation (pyproj)"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# Transform Zurich coordinates from WGS84 to Swiss LV95\n",
            "lon, lat = 8.5417, 47.3769\n",
            "transformer = pyproj.Transformer.from_crs('EPSG:4326', 'EPSG:2056', always_xy=True)\n",
            "e, n = transformer.transform(lon, lat)\n",
            "print(f'WGS84: ({lon:.4f}, {lat:.4f}) -> LV95: ({e:.1f}, {n:.1f})')"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 4) Vector I/O Engines: pyogrio, fiona, and GDAL bindings"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "tmp_dir = Path('/tmp/python_gis_demo')\n",
            "tmp_dir.mkdir(parents=True, exist_ok=True)\n",
            "gpkg = tmp_dir / 'districts.gpkg'\n",
            "\n",
            "districts.to_file(gpkg, layer='districts', driver='GPKG', engine='pyogrio')\n",
            "districts_fiona = gpd.read_file(gpkg, layer='districts', engine='fiona')\n",
            "print('rows read with fiona:', len(districts_fiona))\n",
            "\n",
            "from osgeo import ogr\n",
            "ds = ogr.Open(str(gpkg))\n",
            "print('layers via GDAL/OGR:', [ds.GetLayerByIndex(i).GetName() for i in range(ds.GetLayerCount())])"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 5) Raster Synthesis and Analysis (rasterio + numpy)"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "width = height = 100\n",
            "pixel = 20\n",
            "transform = from_origin(0, 2000, pixel, pixel)\n",
            "\n",
            "x = np.linspace(-2, 2, width)\n",
            "y = np.linspace(-2, 2, height)\n",
            "xx, yy = np.meshgrid(x, y)\n",
            "elev = (np.exp(-(xx**2 + yy**2)) * 1200 + (xx + 2) * 100).astype('float32')\n",
            "\n",
            "memfile = MemoryFile()\n",
            "with memfile.open(\n",
            "    driver='GTiff',\n",
            "    height=height,\n",
            "    width=width,\n",
            "    count=1,\n",
            "    dtype='float32',\n",
            "    crs='EPSG:3857',\n",
            "    transform=transform,\n",
            ") as ds:\n",
            "    ds.write(elev, 1)\n",
            "\n",
            "with memfile.open() as ds:\n",
            "    arr = ds.read(1)\n",
            "    gy, gx = np.gradient(arr, pixel, pixel)\n",
            "    slope = np.sqrt(gx**2 + gy**2)\n",
            "\n",
            "arr.min(), arr.max(), slope.mean()"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 6) xarray + rioxarray: Raster Metadata, Clip, and Reproject"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "with memfile.open() as ds:\n",
            "    da = rioxarray.open_rasterio(ds).squeeze(drop=True)\n",
            "\n",
            "# Clip to district A footprint\n",
            "clip_geom = [districts.loc[districts['district'] == 'A', 'geometry'].iloc[0]]\n",
            "da_clip = da.rio.clip(clip_geom, districts.crs)\n",
            "da_4326 = da_clip.rio.reproject('EPSG:4326')\n",
            "\n",
            "print('original shape:', tuple(da.shape), 'clipped:', tuple(da_clip.shape), 'reprojected:', tuple(da_4326.shape))"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 7) Vector-Raster Bridge: Zonal Statistics (rasterstats)"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "zs = zonal_stats(\n",
            "    vectors=districts.geometry,\n",
            "    raster=elev,\n",
            "    affine=transform,\n",
            "    stats=['mean', 'min', 'max', 'std'],\n",
            ")\n",
            "zonal_df = pd.DataFrame(zs)\n",
            "districts_zonal = pd.concat([districts[['district']].reset_index(drop=True), zonal_df], axis=1)\n",
            "districts_zonal"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 8) Spatial Autocorrelation (PySAL)"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "w = Queen.from_dataframe(districts, use_index=False)\n",
            "w.transform = 'r'\n",
            "y = districts['pm25_mean'].fillna(districts['pm25_mean'].mean()).to_numpy()\n",
            "mi = Moran(y, w)\n",
            "print({'I': float(mi.I), 'p_sim': float(mi.p_sim)})"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 9) Geospatial Storage: GeoParquet and Arrow"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "parquet_path = tmp_dir / 'districts.parquet'\n",
            "districts.to_parquet(parquet_path, index=False)\n",
            "districts_back = gpd.read_parquet(parquet_path)\n",
            "\n",
            "# Arrow table for a tabular projection without geometry\n",
            "attrs_tbl = pa.Table.from_pandas(districts.drop(columns='geometry'))\n",
            "pq.write_table(attrs_tbl, tmp_dir / 'district_attrs.parquet')\n",
            "\n",
            "print('GeoParquet rows:', len(districts_back), 'columns:', districts_back.columns.tolist())"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 10) SQL Geometry Typing with SQLAlchemy + GeoAlchemy2"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# Build SQL metadata without connecting to a DB (safe offline demo).\n",
            "meta = MetaData()\n",
            "tbl = Table(\n",
            "    'district_measurements',\n",
            "    meta,\n",
            "    Column('id', Integer, primary_key=True),\n",
            "    Column('geom', Geometry('POLYGON', srid=3857)),\n",
            "    Column('pm25_mean', Integer),\n",
            ")\n",
            "stmt = select(tbl.c.id, tbl.c.pm25_mean).where(tbl.c.pm25_mean > 10)\n",
            "print(stmt)"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 11) Interactive Mapping: Folium and ipyleaflet"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "districts_wgs84 = districts.to_crs(4326)\n",
            "m = folium.Map(location=[47.38, 8.54], zoom_start=11, tiles='cartodbpositron')\n",
            "folium.GeoJson(districts_wgs84.to_json(), name='districts').add_to(m)\n",
            "m"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "m2 = Map(center=(47.38, 8.54), zoom=10)\n",
            "m2.add_layer(GeoData(geo_dataframe=districts_wgs84, style={'color': 'black', 'fillOpacity': 0.3}))\n",
            "m2"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 12) Trajectories and Urban Morphology (movingpandas + momepy)"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# Synthetic moving object trajectory\n",
            "t = pd.date_range('2025-01-01', periods=20, freq='5min')\n",
            "traj_df = pd.DataFrame({\n",
            "    'id': 1,\n",
            "    't': t,\n",
            "    'x': np.linspace(100, 1800, len(t)) + np.random.normal(0, 30, len(t)),\n",
            "    'y': np.linspace(200, 1600, len(t)) + np.random.normal(0, 30, len(t)),\n",
            "})\n",
            "traj_gdf = gpd.GeoDataFrame(traj_df, geometry=gpd.points_from_xy(traj_df.x, traj_df.y), crs='EPSG:3857')\n",
            "traj_collection = mpd.TrajectoryCollection(traj_gdf, traj_id_col='id', t='t')\n",
            "traj = traj_collection.trajectories[0]\n",
            "print('trajectory length (m):', round(traj.get_length(), 2))\n",
            "\n",
            "# Minimal momepy demo: convert synthetic street centerlines to network graph\n",
            "streets = gpd.GeoDataFrame(\n",
            "    geometry=[\n",
            "        LineString([(0, 500), (2000, 500)]),\n",
            "        LineString([(0, 1500), (2000, 1500)]),\n",
            "        LineString([(500, 0), (500, 2000)]),\n",
            "        LineString([(1500, 0), (1500, 2000)]),\n",
            "    ],\n",
            "    crs='EPSG:3857',\n",
            ")\n",
            "G = momepy.gdf_to_nx(streets, approach='primal')\n",
            "print('street graph nodes/edges:', G.number_of_nodes(), G.number_of_edges())"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 13) STAC and Optional Cloud/API Integrations"
        ],
    },
    {
        "cell_type": "code",
        "metadata": {"language": "python"},
        "execution_count": None,
        "outputs": [],
        "source": [
            "# Offline STAC object construction\n",
            "item = pystac.Item(\n",
            "    id='synthetic-scene-001',\n",
            "    geometry={\n",
            "        'type': 'Polygon',\n",
            "        'coordinates': [[[8.5, 47.3], [8.6, 47.3], [8.6, 47.4], [8.5, 47.4], [8.5, 47.3]]],\n",
            "    },\n",
            "    bbox=[8.5, 47.3, 8.6, 47.4],\n",
            "    datetime=pd.Timestamp('2025-01-01T10:00:00Z').to_pydatetime(),\n",
            "    properties={'eo:cloud_cover': 7.2},\n",
            ")\n",
            "print('STAC item id:', item.id)\n",
            "\n",
            "# Optional internet-dependent demos\n",
            "try:\n",
            "    import pystac_client\n",
            "    client = pystac_client.Client.open('https://planetarycomputer.microsoft.com/api/stac/v1')\n",
            "    print('STAC API reachable:', client.id)\n",
            "except Exception as exc:\n",
            "    print('STAC API demo skipped (offline or blocked):', type(exc).__name__)\n",
            "\n",
            "try:\n",
            "    import osmnx as ox\n",
            "    G_drive = ox.graph_from_place('Zurich, Switzerland', network_type='drive', simplify=True)\n",
            "    print('OSMnx graph nodes:', len(G_drive.nodes))\n",
            "except Exception as exc:\n",
            "    print('OSMnx demo skipped (offline or blocked):', type(exc).__name__)\n",
            "\n",
            "try:\n",
            "    from owslib.wms import WebMapService\n",
            "    wms = WebMapService('https://ahocevar.com/geoserver/wms', version='1.3.0')\n",
            "    print('WMS title:', wms.identification.title)\n",
            "except Exception as exc:\n",
            "    print('OWSLib demo skipped (offline or blocked):', type(exc).__name__)"
        ],
    },
    {
        "cell_type": "markdown",
        "metadata": {"language": "markdown"},
        "source": [
            "## 14) Takeaways\n",
            "\n",
            "- `GeoPandas + Shapely` handles vector ETL and geometry analytics elegantly.\n",
            "- `Rasterio + rioxarray + xarray` covers raster IO, metadata-aware transformations, and N-D workflows.\n",
            "- `rasterstats + PySAL` bridge classic GIS overlays with spatial statistics.\n",
            "- `pyarrow/GeoParquet` improves interoperability and analytics-readiness.\n",
            "- `folium/ipyleaflet` provide rapid interactive map communication in notebooks.\n",
            "- Optional web ecosystem tools (`pystac-client`, `osmnx`, `OWSLib`) unlock cloud and live-service integration when network is available."
        ],
    },
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

out_path.write_text(json.dumps(nb, indent=2))
print(f"Wrote notebook to {out_path} with {len(cells)} cells")
