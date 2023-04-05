
FROM python:3.7-slim-buster
ENV TZ Europe/London
# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libglib2.0-0 ffmpeg libsm6 libxrender1 libxext6 wget git && \
    rm -rf /var/lib/apt/lists/*
# Put conda in path so we can use conda activate
WORKDIR /home
COPY requirements.txt .
RUN pip install -r requirements.txt
ADD .  .
#EXPOSE 8503
#CMD ["python3", "main.py"]