FROM nvidia/cuda:11.8.0-base-ubuntu22.04
ENV TZ Europe/London
ENV home /opt/conda
# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libglib2.0-0 ffmpeg libsm6 libxrender1 libxext6 wget git && \
    rm -rf /var/lib/apt/lists/*
# Install miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda 
# Put conda in path so we can use conda activate
WORKDIR /home
COPY environment.yaml .
ENV PATH=$home/bin:$PATH
RUN conda env update --file environment.yaml --prune && \
    conda clean --all --force-pkgs-dirs
ADD .  .