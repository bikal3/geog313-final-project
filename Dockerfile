# Start from the official Miniconda image
FROM continuumio/miniconda3:24.7.1-0

# Copy project files
COPY environment.yml /home/environment.yml

# Activate the Conda environment
RUN echo "conda activate envburn" >> ~/.bashrc
ENV PATH="$PATH:/opt/conda/envs/envburn/bin"

# Create a Conda environment with JupyterLab installed
RUN conda env create -f /home/environment.yml

# Create a non-root user and switch to that user
RUN useradd -m jupyteruser
USER jupyteruser

# Set the working directory to /home/jupyteruser
WORKDIR /home/jupyteruser

# Expose the JupyterLab port
EXPOSE 8888

# Expose the Dask Dashboard port
EXPOSE 8787

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0"]
