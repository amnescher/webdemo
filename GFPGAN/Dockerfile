FROM nvidia/cuda:11.8.0-base-ubuntu22.04
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
WORKDIR /home
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
ADD .  .




