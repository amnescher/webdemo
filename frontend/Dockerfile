FROM python:3.10.1-slim
WORKDIR /home
COPY . .
RUN pip install --upgrade pip &&\
    pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "HOME.py"]