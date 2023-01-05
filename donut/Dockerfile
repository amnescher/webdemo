FROM nvidia/cuda:11.3.1-devel-ubuntu20.04
ADD .  /home
RUN apt-get update
RUN apt install  -y python3-pip
ENV TZ Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6 && \
    apt-get install -y wget &&\
    apt-get -y install git &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Put conda in path so we can use conda activate
WORKDIR /home
RUN pip install -r requirements.txt
#EXPOSE 8503
#CMD ["python3", "main.py"]