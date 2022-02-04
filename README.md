# OS Geostack Sandbox
## What is this about?
The goal is to make it easy and fun to experiment with the amazing geospatial open source (OS) tools. Examples include Postgis to store and process spatial data, Geoserver to make it available via OGC standardized services and python's extensive geo-ecosystem. All of this should be possible without worrying about the sometimes tedious installation of dependencies (yes, I am looking at you GDAL and geopandas) and configuring services to work together properly.

As a secondary objective, this repository is a playground for me to do first baby steps in expanding my horizon towards the devops world to learn about containerization, orchestration, CI/CD, etc.

# Components
## Geoscripting Sandbox
The folder _geoscriptingsandbox_ contains a dockerfile that allows to spin up a jupyterlab instance whose kernel has access to many common packages like Fiona, Shapely, Geopandas, Rasterio, etc. which work neatly together. Concentrate on the fun part of exploring the tools and processing your data without worrying about setup.

## OS Geostack Sandbox
The top level docker-compose.yml will start up multiple containers:
- A postgis database.
- A pgadmin instance to interact with the database.
- A geoserver instance.
- The geoscripting sandbox mentioned above.
- A simple central hub as stepping stone (simple flask application listening on localhost:80) that provides an overview and links to all above services.

# How to run?

## 1) You need Docker
Make sure you have docker engine installed. This might be a little fiddly, just stick to the [documentation](https://docs.docker.com/engine/install/). Make sure that after installation docker engine is actually up and running. You are good when the following terminal command returns some kind of version instead of an error :pray:
```console
docker --version
```

> _Good to know:_ When you restart the computer, docker desktop might not be started automatically. If you try to run a docker command and get an error message mentioning a daemon there is a good chance you first might need to start the docker desktop application (e.g. via search menu).

## 2) Start the OS geostack sandbox
Download the two files docker-compose.yml and .env (you can download them directly or clone the whole repository). Then navigate into the folder where docker-compose.yml and .env reside in. Open a terminal in that folder and run:
```console
docker compose up -d
```

Eventually the terminal will display the blinking cursor again and let you type. This means all is ready.

__You can now access the hub by typing localhost in your browser window.__

> Note: The first time it will take some minutes because a lot of data is being downloaded, make sure you are connected to a fast and reliable internet connection. This is a one-time thing and subsequent startups will only take seconds.

> Note: You can also avoid the -d flag, which will then display the logs of all containers in the terminal.

## 3) Stop the OS geostack sandbox

To stop all containers run:
```console
docker compose down
```

That's it - if you want to start again, run the up command above again and you are good to go.

> _Good to know:_ All your data and configurations (e.g. pgadmin database connections) will be preserved.

> _Good to know:_ If you want to reset the data for ALL containers, add -v to the docker-compose down command. If you want to selectively reset the data, open Docker Desktop and delete the respective volume in the volumes tab. Upon running the next docker-compose up command you have a nice clean reset.

# How to run Geoscripting Sandbox alone without cloning the repository?
The jupyterlab setup of the geoscripting sandbox is very useful beyond the scope of just being a sandbox. It might be interesting to use it as general environment to perform python geoprocessing. Because of this we provide the image on github registry for download so you can download and run it with a single command without cloning the repository or worrying about building the image yourself.

Select a path on your system you want to be accessible through jupyterlab and replace $MOUNT_PATH in the command below with this path.

```console
docker run -it --rm -p 8888:8888 --volume="$MOUNT_PATH":"/geo/host_mount_dir" ghcr.io/laiskasiili/os_geostack_sandbox/geoscriptingsandbox:v0.0.1
```

The first run will take some time because a lot of data is being downloaded, subsequent runs of this command will take merely a second. After some time you should see a link in the terminal containing 127.0.0.1... - open it in your browser to open jupyterlab. Opening the data folder in the left pane will show you the content of <MOUNT_PATH>. Make sure to save everything you want to be persisted over time in this folder.

When you are done, just hit Ctrl + C in the terminal to shut down the container and jupyterlab. Run the command above to start a new jupterlab session.

# How to clean up all of this stuff I did above?
To completely clean up all traces from the steps above, open Docker Desktop and remove the images you see in the images tab as well as volumes you see in the volume tab. Then uninstall Docker Desktop.