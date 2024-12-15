# Assessing the climate factors and vegetation conditions influencing wildfires in California

This guide will walk you through running a Docker container using the provided Dockerfile, setting up the Conda environment, and executing these file Jupyter notebook.

## Prerequisites

Ensure that you have the following installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- Clone of this repository

## Steps to Run the Docker Container

### 1. Pull the Docker Image form Dockerhub

It's recommended to pull the Docker image from Dockerhub.

```bash
docker pull bikal3/burn_image
```

Otherwise, if you prefer, you can build your own image go to folder geog313-final-project

```bash
docker build -t bikal3/burn_image .
```

### 2. Run the Docker Container

Go to folder geog313-final-project and run the container using the following command:

```bash
docker run -p 8888:8888 -p 8787:8787 -v $(pwd):/home/jupyteruser --name burn_container bikal3/burn_image
```

Port `8787` is used by Dask Dashboard.

### 3. Access JupyterLab

Once the container is running, JupyterLab will start and an access token will be printed in the terminal.

### 4. Open the Notebook

After logging into JupyterLab, you should see the file name with ipynb extention notebook in the directory. Click to open it, and you can start running the code.

### Stopping the Container

To stop the running container, execute:

```bash
docker stop burn_container
```

### Restarting the Container

If you want to restart the container later, you can use:

```bash
docker start -i burn_container
```

### Removing the Container and Image

To remove the container and image after you are done:

```bash
docker rm burn_container
docker rmi bikal3/burn_image
```

## Folder Structure: SRC

| src                    | Description
| ---------------------  | --------------------------------------------- |
| evi.api.ipynb          | Jupyter notebooks for EVI index analysis      |
| fires_notebook.ipynb   | Python scripts for processing MTBS data.      |
| mtbs_example.ipynb     | Jupyter notebooks for MTBS data by bbox       |
| mtbs_source_coop.ipynb | Python for MTBS data by country               |
| openmeteo_example.ipynb| Jupyter notebooks for weather data            |


## Folder Structure: utils 

| utils                  | Description 
| ---------------------  | --------------------------------------------- | 
| evi_utils.py           | Directory containing shapefiles and datasets. |
| mtbs_utils.py          | Jupyter notebooks for data analysis.          |
| openmeteo_utils.py     | Python scripts for processing data.           |
| source_coop_utils.py   | List of dependencies to install.              |


## File Structure: mtbs_utils 

| mtbs_utils.py             |             Parameters                        |  Description 
| ------------------------- | --------------------------------------------- | ------------------------
| initialize_gee            | ee.Initialize()                               | Authenticate and initialize the Google Earth Engine API.
| get_month_start_end       | Date string in 'YYYY-MM-DD HH:MM:SS' format.  | Given an event date, return the start date and end date of that month
| datetime_to_unix          | Unix timestamp in milliseconds                | Convert a date string in 'YYYY-MM-DD' format to Unix timestamp in milliseconds
|display_mtbs_burn_severity |start_date:'YYYY-MM-DD' format, end_date:'YYYY-MM-DD' format, bbox (list): Bounding box as [min_lon, min_lat, max_lon, max_lat]                                     | Display the MTBS burn severity map within a specified date range and bounding box
| display_mtbs_boundaries   |start_date:'YYYY-MM-DD' format, end_date:'YYYY-MM-DD' format, bbox (list): Bounding box as [min_lon, min_lat, max_lon, max_lat]                                     | Display the MTBS burned area boundaries within a specified bounding box and date range
