import uuid
import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np
from PIL import Image
from typing import List
import config
import requests
from utils import donut_app

# port_config = load_config_port()

# try:
#         requests.post(
#                                 f"http://{port_config.model_ports.db[-1]}:8509/initdb"
#                             )
# except:
#         print("database initialization failed")


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


@app.post("/donut_pars")
def get_image(file: UploadFile = File(...)):
    image  = file.file
    output = donut_app(image, "parsing", question="")
    return {"name": output}

@app.post("/donut_vqa")
def get_imag_questione(question: List[str] = [""], file: UploadFile = File(...)):
    image  = file.file
    question = question[0]
    output = donut_app(image, "vqa", question=question)
    return {"name": output}
    
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8503)

