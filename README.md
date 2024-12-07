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

Otherwise, if you prefer, you can build your own image go to folder assignment-5

```bash
docker build -t bikal3/burn_image .
```

### 2. Run the Docker Container

Go to folder assignment-7 and run the container using the following command:

```bash
docker run -p 8888:8888 -p 8787:8787 -v $(pwd):/home/jupyteruser --name assignment-7-container bikal3/bikal3/burn_image
```

Port `8787` is used by Dask Dashboard.

### 3. Access JupyterLab

Once the container is running, JupyterLab will start and an access token will be printed in the terminal.

### 4. Open the Notebook

After logging into JupyterLab, you should see the `main.ipynb` notebook in the directory. Click to open it, and you can start running the code.

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
