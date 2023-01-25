FROM python:3.8-slim-buster
WORKDIR /home
COPY . .
RUN pip install --upgrade pip &&\
    pip install -r requirements.txt
# EXPOSE 8509
# CMD ["python3", "backend.py"]