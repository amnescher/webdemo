import uvicorn
from fastapi import File, Form
from fastapi import UploadFile, Depends
import config
from typing import List, Union, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from omegaconf import OmegaConf
import requests
import time
import json
import numpy as np 
import cv2 
from utils import process, load_model, load_shared_bucket
import PIL.Image as Image
import os 
import uuid
import shutil
from dotenv import load_dotenv
from minio import Minio

class canny2image(BaseModel):
    prompt: str
    num_samples: int
    image_resolution: int
    strength: float
    guess_mode: bool
    low_threshold: int
    high_threshold: int
    ddim_steps: int
    scale: float
    seed: int
    eta: float
    a_prompt: str
    n_prompt:str

app = FastAPI()
apply_canny,model, ddim_sampler= load_model()
@app.post("/canny2image")
def submit(req: canny2image = Depends(), files: UploadFile = File(...)):
    outpath = "prediction"
    file_bytes = np.asarray(bytearray(files.file.read()), dtype=np.uint8)
    input_image = cv2.imdecode(file_bytes, 1)
    outputs = process(input_image, req.prompt, req.a_prompt, req.n_prompt, req.num_samples, req.image_resolution, req.ddim_steps, req.guess_mode, req.strength, req.scale, req.seed, req.eta, req.low_threshold, req.high_threshold,apply_canny,model,ddim_sampler)
    local_path = os.path.join(outpath, "samples"+"_"+str(uuid.uuid4())+"_"+str(req.strength) +"_"+str(req.seed))
    os.makedirs(local_path, exist_ok=True)
    output_path =[]

    load_dotenv()
    access_key = os.getenv("access_key")
    secret_key = os.getenv("secret_key")

    minio_server_ip = os.environ.get('MINIO_SERVER_IP')
    
    client = Minio(
        f"{minio_server_ip}:9000",
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )
    for idx, image in enumerate(outputs):
        sample_path = os.path.join(local_path, f'grid-{idx:04}.png')
        Image.fromarray(image.astype(np.uint8)).save(sample_path)
        output_path.append(sample_path)
        print(sample_path)
        client.fput_object(
        "controlnetresults", sample_path, sample_path,
    )  
    shutil.make_archive(local_path, "zip", local_path)
    zip_path = local_path + ".zip"
    client.fput_object(
        "controlnetresults", sample_path, sample_path,
    )
    client.fput_object(
        "controlnetresults", zip_path, zip_path,
    )
    os.remove(zip_path)
    response_dict = {"output": output_path,"zip_path":zip_path}
    return response_dict
          


if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8507)