# Open-source GIS Sandbox

## What is this about?

The goal is to make it easy and fun to experiment with the amazing geospatial
open source (OS) tools. Examples include PostGIS to store and process spatial
data, GeoServer to make it available via OGC standardized services and Python's
extensive geo-ecosystem. All of this should be possible without worrying about
the sometimes tedious installation of dependencies (yes, I am looking at you
GDAL and GeoPandas) and configuring services to work together properly.

As a secondary objective, this repository is a playground for me to do first
baby steps in expanding my horizon towards the DevOps world to learn about
containerization, orchestration, CI/CD, etc.

# How to run?

## 1) You need Docker (Desktop)

Make sure you have docker engine installed. This might be a little fiddly, just
stick to the [documentation](https://docs.docker.com/engine/install/). Make sure
that after installation docker engine is actually up and running. You are good
when the following terminal command returns some kind of version instead of an
error :pray:

```console
docker --version
```

> _Good to know:_
>
> - When you restart the computer, docker desktop might not be started
>   automatically. If you try to run a docker command and get an error message
>   mentioning a daemon there is a good chance you first might need to start the
>   docker desktop application (e.g. via search menu).
> - Make sure that you have at least a healthy 10gb of free disk space before
>   continuing. No worries, uninstalling is simple and clean as outlined below.

## 2) Start the Sandbox

You only need the single file docker-compose.yml to run the sandbox. You can
either clone the repository or [click here to open its
raw form](https://raw.githubusercontent.com/folinimarc/os_geostack_sandbox/main/docker-compose.yml)
and then go right-click and save as. Just make sure it is still called
docker-compose.yml (with .yml extension).

Open a terminal and navigate into the **same folder** where you placed the
docker-compose.yml. In the terminal run:

```console
docker compose -p sandbox up -d
```

Eventually the terminal will display the blinking cursor again and let you type.
This means all is ready.

**You can now access the Sandbox hub by typing _localhost:8000_ in your browser
window.**

> _Good to know_:
>
> - If you receive an error at this stage, it is probably well-known and related
>   to permissions to create a mount on your computer's file system. An internet
>   search with the error message and your operating system should provide a
>   solution.
> - The first time it will take some minutes because a lot of data is being
>   downloaded, make sure you are connected to a fast and reliable internet
>   connection. This is a one-time thing and subsequent startups will only take
>   seconds.
> - The -p flag used in the commands above specifies the Docker Compose project
>   name, which is used as a prefix for many Docker Compose components such as
>   networks and volumes. By choosing different project names, it is possible for
>   multiple instances of the Sandbox to coexist with separate volumes and hence
>   separate persisted state.
> - You can also avoid the -d flag, which will then display the logs of all
>   containers in the terminal.

## 3) Stop the Sandbox

To stop all containers run:

```console
docker compose -p sandbox down
```

That's it - if you want to start again, run the up command above again, and you
are good to go.

> _Good to know:_
>
> - All your data and configurations (e.g. pgAdmin database connections) will be
>   preserved.
> - If you want to reset the data for ALL containers, add -v to the docker
>   compose down command. If you want to selectively reset the data, open Docker
>   Desktop and delete the respective volume in the volumes tab. Upon running the
>   next docker compose up command you have a nice clean reset.

## (optional) How to run JupyterLab-GeoEnv as stand-alone?

The folder _jupyterlabgeoenv_ contains a Dockerfile that allows to spin up a
JupyterLab instance whose kernel has access to many common packages like Fiona,
Shapely, GeoPandas, Rasterio, etc. which work neatly together. Concentrate on
the fun part of exploring the tools and processing your data without worrying
about setup.

JupyterLab-GeoEnv is very useful beyond the scope of just being a sandbox. It
might be interesting to use it as general environment to perform Python
geoprocessing. Because of this we provide the image on GitHub registry for
download, so you can download and run it with a single command without cloning
the repository or worrying about building the image yourself.

Select a path on your system you want to be accessible through JupyterLab and
replace $MOUNT_PATH in the command below with this path.

```console
docker run -it --rm -p 8888:8888 --volume="$MOUNT_PATH":"/home/host_mount_dir" ghcr.io/folinimarc/os_gis_sandbox/jupyterlabgeoenv:jupyterlabgeoenv-v1.0.7
```

The first run will take some time because a lot of data is being downloaded,
subsequent runs of this command will take merely a second. After some time you
should see a link in the terminal containing 127.0.0.1... - open it in your
browser to open JupyterLab. Opening the data folder in the left pane will show
you the content of <MOUNT_PATH>. Make sure to save everything you want to be
persisted over time in this folder.

When you are done, just hit Ctrl + C in the terminal to shut down the container
and JupyterLab. Run the command above to start a new JupyterLab session.

> _Good to know:_
>
> - By default none of your configurations or installed Python packages will be
>   persisted. If you need this, we recommend using the full Sandbox setup which
>   persists your data, settings and changes to the Python environment.

# How to clean up all of this stuff I did above?

To completely clean up all traces from the steps above, simply uninstall Docker
Desktop, which will remove all images and volumes. To selectively remove images
or volumes, open Docker Desktop and use the Images and Volumes tab.

# Sandbox configuration

Various aspects of the sandbox can be configured, this includes ports,
usernames, versions and what path on the host to make accessible to
JupyterLab-GeoEnv and GeoServer data directory. The list below shows the
variables with their defaults. In order to overwrite these variables, create an
environment file named simply .env in the same directory as the
docker-compose.yml. The environment file should contain one line per variable
you wish to overwrite in the form of VARIABLE=VALUE, for example:
POSTGIS_PORT_EXTERNAL=5433

This is the default way docker compose handles environment variables and more
information can be found in the
[documentation](https://docs.docker.com/compose/environment-variables/).

| Variable                       | Default                        | Notes                                                                                                                                  |
| ------------------------------ | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| HOST_SYSTEM_MOUNT_PATH         | ./                             |                                                                                                                                        |
| HOST_MOUNT_FOLDER_NAME         | \_host_mount_dir               |                                                                                                                                        |
| CONTENT_MOUNT_FOLDER_NAME      | \_content                      |                                                                                                                                        |
| CONTENT_VERSION_TAG            | content-v1.0.4                 |                                                                                                                                        |
| JUPYTERLABGEOENV_VERSION       | jupyterlabgeoenv-v1.0.7        |                                                                                                                                        |
| JUPYTERLABGEOENV_PORT_EXTERNAL | 8004                           |                                                                                                                                        |
| GEOSERVER_VERSION              | 2.24.1                         |                                                                                                                                        |
| GEOSERVER_PORT_EXTERNAL        | 8003                           |                                                                                                                                        |
| GEOSERVER_ADMIN_PASSWORD       | gis                            |                                                                                                                                        |
| GEOSERVER_ADMIN_USER           | gis                            |                                                                                                                                        |
| GEOSERVER_MAXIMUM_MEMORY       | 6G                             |                                                                                                                                        |
| GEOSERVER_SAMPLE_DATA          | true                           |                                                                                                                                        |
| GEOSERVER_STABLE_EXTENSIONS    |                                | [Stable extensions that can be activated](https://github.com/kartoza/docker-geoserver/blob/master/build_data/stable_plugins.txt)       |
| GEOSERVER_COMMUNITY_EXTENSIONS | geostyler-plugin,ogcapi-plugin | [Community extensions that can be activated](https://github.com/kartoza/docker-geoserver/blob/master/build_data/community_plugins.txt) |
| HUB_VERSION                    | hub-v1.0.2                     |                                                                                                                                        |
| HUB_PORT_EXTERNAL              | 8000                             |                                                                                                                                        |
| PGADMIN_VERSION_TAG            | 8.1                            |                                                                                                                                        |
| PGADMIN_PORT_EXTERNAL          | 8002                           |                                                                                                                                        |
| PGADMIN_DEFAULT_EMAIL          | gis@gis.com                    |                                                                                                                                        |
| PGADMIN_DEFAULT_PASSWORD       | gis                            |                                                                                                                                        |
| POSTGIS_VERSION_TAG            | 16-3.4-alpine                  |                                                                                                                                        |
| POSTGIS_PORT_EXTERNAL          | 8001                           |                                                                                                                                        |
| POSTGRES_USER                  | gis                            |                                                                                                                                        |
| POSTGRES_DB                    | gis                            |                                                                                                                                        |
| POSTGRES_PASSWORD              | gis                            |                                                                                                                                        |


# Trouble Shooting

## I am on MacOS and Geoserver does not start...
Run the docker compose up command without the `-d` flag to see all the output in the terminal. If you see multiple lines starting with `chown: changing ownership`, this is related to a [known MacOS related filesystem permission pain](https://stackoverflow.com/questions/43097341/docker-on-macosx-does-not-translate-file-ownership-correctly-in-volumes). Unfortunately, to my knowledge there exists no good solution as of now. The hacky workaround for these permission issues is to point `HOST_SYSTEM_MOUNT_PATH` at a directory where all users have full permissions. Be cautious and only use this for personal setups! This directory will then be where jupyterlabgeoenv and geoserver read and write data to the host machine's filesystem.
1. Create a new directory that should serve as the data directory.
2. Grant all users full permission. In terminal you can run this command `sudo chmod 777 <folder path>`
3. Create a file `.env` in the same directory where your `docker-compose.yml` resides with the following content:
    ```
    HOST_SYSTEM_MOUNT_PATH=<folder path>
    ```
4. Run your docker compose up command normally. Because of its name and location, the content of `.env` will be picked up automatically.
