FROM python:3.10.1-slim
WORKDIR /home
COPY requirements.txt .
RUN pip install --upgrade pip &&\
    pip install -r requirements.txt
ADD . .
