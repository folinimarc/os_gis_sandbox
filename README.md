# Open-source GIS Sandbox

## What is this about?

The goal is to make it easy and fun to experiment with the amazing geospatial
open source (OS) tools. Examples include PostGIS to store and process spatial
data, GeoServer to make it available via OGC standardized services and Python's
extensive geo-ecosystem. All of this should be possible without worrying about
the sometimes tedious installation of dependencies and configuring services to work together properly.

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

You only need the single file `docker-compose.yml` to run the sandbox. You can
either clone the repository or [right-click this link and choose save-as](https://raw.githubusercontent.com/folinimarc/os_gis_sandbox/main/docker-compose.yml). 
Make sure that:
- The file is called `docker-compose.yml` (with .yml extension).
- You save the file into a folder where you have read/write permissions.
- You save the file into a folder that is on your machine. Continously snyced folders, such as OneDrive, should be avoided.

Open a terminal and navigate into the **same folder** where you placed the
`docker-compose.yml`. In the terminal run:

```console
docker compose -p sandbox up
```

A wall of text will appear in the terminal. Don't worry, these are just the logs of all sandbox components. If something does not work as intended, the logs are helpful when reaching out for help.

**Leave the terminal open and access the Sandbox hub by typing _localhost:8000_ in your browser window.**

> _Good to know_:
>
> - The first time it will take some minutes because a lot of data is being
>   downloaded, make sure you are connected to a fast and reliable internet
>   connection. This is a one-time thing and subsequent startups will only take
>   seconds.
> - If you receive an error at this stage, it is probably well-known and related
>   to permissions to create a mount on your computer's file system. 
>   Check the [Trouble Shooting section](#trouble-shooting) or search the internet 
>   with the error message and your operating system.
> - The -p flag used in the commands above specifies the Docker Compose project
>   name, which is used as a prefix for many Docker Compose components such as
>   networks and volumes. By choosing different project names, it is possible for
>   multiple instances of the Sandbox to coexist with separate volumes and hence
>   separate persisted state.


## 3) Stop the Sandbox

To stop the sandbox, simply click on the terminal where you started the sandbox (with the wall of logs) and press `Ctrl + C`. Give it a second to gracefully shut down.

That's it - if you want to start again, run the up command above again, and you
are good to go.

> _Good to know:_
>
> - All your data and configurations (e.g. pgAdmin database connections) will be
>   preserved.
> - All Sandbox data is persisted on isolated virtual volumes. If you want to reset configuration or data, open Docker
>   Desktop and delete the respective volume in the volumes tab. You may need to first stop and remove the sandbox stack in the Containers tab. Upon running the
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
replace `MOUNT_PATH` in the command below with this path.

```console
docker run -it --rm -p 8888:8888 --volume="MOUNT_PATH":"/sandbox/your_computer" ghcr.io/folinimarc/os_gis_sandbox/jupyterlabgeoenv:jupyterlabgeoenv-v1.0.10
```

The first run will take some time because a lot of data is being downloaded,
subsequent runs of this command will take merely a second. After some time you
should see a link in the terminal containing 127.0.0.1... - open it in your
browser to open JupyterLab. Opening the data folder in the left pane will show
you the content of `MOUNT_PATH`. Make sure to save everything you want to be
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
environment file named simply `.env` in the same directory as the
`docker-compose.yml`. The environment file should contain one line per variable
you wish to overwrite in the form of VARIABLE=VALUE, for example:
OSGS_POSTGIS_PORT=5433

This is the default way docker compose handles environment variables and more
information can be found in the
[documentation](https://docs.docker.com/compose/environment-variables/).


# Trouble Shooting

## I get "Error response from daemon: Conflict. The container name ... is already in use..."
This might happen when a new version of some sandbox components should be used, but the old containers are still there. Either remove all sandbox containers by using the Docker Desktop UI or move to the directory where your `docker-compose.yml`is located and run the following command to remove sandbox containers:
```
docker compose -p sandbox down
```
Afterwards, start the sandbox as usual.

## I am on Linux and I do not have the permission to run Docker...
As a non-root user you either have to use `sudo` for the start and stop commands, if you have a sudo password. Alternatively, you can create a docker group and add your user to it, but this step also requires at least temporary root privileges. Check out the official [documentation on that topic](https://docs.docker.com/engine/install/linux-postinstall/).

## I am on Windows and I do not have the permission to run Docker...
Windows requires admin privileges during the installation of Docker Desktop, which will add the current user to a docker-user group. Other users must be added to this group explicitly. Check out the official [documentation on that topic](https://docs.docker.com/desktop/setup/install/windows-permission-requirements/).

## I am on MacOS and Geoserver does not start...
Check the logs in the terminal. If you see multiple lines starting with `chown: changing ownership`, this is related to a [known MacOS related filesystem permission pain](https://stackoverflow.com/questions/43097341/docker-on-macosx-does-not-translate-file-ownership-correctly-in-volumes). Unfortunately, to my knowledge there exists no good solution as of now. One workaround is to run the sandbox in a directory where all users have full permissions. Be cautious and only use this for personal setups! This directory will then be where jupyterlabgeoenv and geoserver read and write data to the host machine's filesystem.
1. Create a new directory that should serve as the data directory.
2. Grant all users full permission. In terminal you can run this command `sudo chmod 777 <folder path>`
3. Move your `docker-compose.yml` in this new directory, navigate to this new directory in your terminal and start the sandbox.

## In Docker Desktop I see that the content container is not running
That is totally fine. The content container only runs at the beginning to copy its content into other sandbox components, then it shuts down.
