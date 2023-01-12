FROM nvidia/cuda:11.3.1-devel-ubuntu20.04
WORKDIR /home
RUN apt-get update
RUN apt install  -y python3-pip
ENV TZ Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6 && \
    apt-get install -y wget &&\
    apt-get -y install git &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda

ENV home /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda 

# Put conda in path so we can use conda activate
ADD .  .
ENV PATH=$home/bin:$PATH
RUN conda update -n base -c defaults conda &&\
    conda env create -f  environment.yml

SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y


#EXPOSE 8505
#ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "myenv", "python", "backend.py"]

# RUN pip install -r requirements.txt
# CMD ["python3","test.py"]