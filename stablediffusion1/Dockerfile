FROM nvidia/cuda:11.3.1-devel-ubuntu20.04
RUN apt-get update
RUN apt install  -y python3-pip
ENV TZ Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6 && \
    apt-get install -y wget &&\
    apt-get -y install git &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
# Install miniconda
ENV home /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda 

# Put conda in path so we can use conda activate
WORKDIR /home
ADD .  .
ENV PATH=$home/bin:$PATH
RUN conda update -n base -c defaults conda &&\
    conda env create -f  environment.yaml 
#SHELL ["conda", "run", "-n", "ldm", "/bin/bash", "-c"]
#EXPOSE 8504
#ENTRYPOINT ["conda", "run", "-n", "ldm", "python3", "backend.py"]
#ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "ldm", "python", "backend.py"]