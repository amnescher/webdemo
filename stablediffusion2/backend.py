import uvicorn
from fastapi import File, Form
from fastapi import UploadFile, Depends
import config
from typing import List, Union, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
import PIL.Image as Image
import uuid
import traceback
from omegaconf import OmegaConf
import requests
import json
import torch
from utils import diff_model, load_files_from_minIO_bucket,load_shared_bucket
from omegaconf import OmegaConf
import requests
import numpy as np
import os
import time

# download model weights from minio bucket and load model weights into GPU mem, load model config, download port config file from minio and return config file

(
    model_v2,
    config_v2,
    model_v2_up,
    model_v2_paint,
) = load_files_from_minIO_bucket()

minIO_clinet = load_shared_bucket()

# initialise database to store requrests information
# try:
#     requests.post(f"http://{port_config.model_ports.db[-1]}:8509/initdb")
# except:
#     print("database initialization failed")


# Initiate fast api
app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


# ------------------------------------------- Processing Text to Image requests ----------------------------------------

# define Basemodel class to recive txt2img request
class txt2img_req(BaseModel):
    prompt: str
    w: int
    h: int
    samples: int
    n_iter: int
    seed: int


@app.post("/txt2img")
def read_items(API_req: txt2img_req):
    # generating images by the stable diffusion and return paths to generated images
    start = time.time()
    image_path, path, grid_path = diff_model(
        prompt=API_req.prompt,
        mode="txt2img",
        model=model_v2,
        config=config_v2,
        strength=0.8,
        dim=(API_req.h, API_req.w),
        seed_num=API_req.seed,
        num_samples=API_req.samples,
        n_iter=API_req.n_iter,
        shared_dir = minIO_clinet
    )
    end = time.time()

    # save request information in the database
    request_info = {
        "req_type": "Stable Diffusion version2 - txt2img",
        "prompt": API_req.prompt,
        "runtime": (end - start),
    }
    # sending insert request to database microservice
    # requests.post(
    #     f"http://{port_config.model_ports.db[-1]}:8509/insert",
    #     data=json.dumps(request_info),
    # )

    return {"response": {"image": image_path, "path": path, "grid_path": grid_path}}


# -------------------------------------- Processing Image to Image requests ---------------------------------------------------
# define Basemodel class to recive Super resolution requests


class img2img_req(BaseModel):
    prompt: str
    samples: Optional[int] = None
    n_iter: Optional[int] = None
    seed: Optional[int] = None
    strength: Optional[float] = None


@app.post("/img2img")
def submit(req: img2img_req = Depends(), files: UploadFile = File(...)):
    request = req.dict()
    uploaded_image = Image.open(files.file)
    image_path = f"/prediction/{str(uuid.uuid4())}.jpg"
    uploaded_image.convert("RGB").save(image_path)
    start = time.time()
    image_path, path, grid_path = diff_model(
        prompt=request["prompt"],
        mode="img2img",
        model=model_v2,
        config=config_v2,
        image_path=image_path,
        strength=request["strength"],
        seed_num=request["seed"],
        num_samples=request["samples"],
        n_iter=request["n_iter"],
        shared_dir = minIO_clinet
    )
    end = time.time()
    # save request information in the database
    request_info = {
        "req_type": "Stable Diffusion version2 - img2img",
        "prompt": request["prompt"],
        "runtime": (end - start),
    }
    # sending insert request to database microservice
    # requests.post(
    #     f"http://{port_config.model_ports.db[-1]}:8509/insert",
    #     data=json.dumps(request_info),
    # )
    
    return {"response": {"image": image_path, "path": path, "grid_path": grid_path}}


# -------------------------------------- Processing Image to Image requests ---------------------------------------------------
# define Basemodel class to recive Super resolution requests


class superresolution_req(BaseModel):
    prompt: str
    samples: Optional[int] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    scale: Optional[float] = None
    eta: Optional[float] = None


@app.post("/upscale")
def submit(req: superresolution_req = Depends(), files: UploadFile = File(...)):
    request = req.dict()
    uploaded_image = Image.open(files.file)
    input_image_path = f"prediction/{str(uuid.uuid4())}.jpg"
    uploaded_image.convert("RGB").save(input_image_path)
    start = time.time()
    image_path = diff_model(
        prompt=request["prompt"],
        mode="upscaling",
        model=model_v2_up,
        config=None,
        image_path=input_image_path,
        seed_num=request["seed"],
        num_samples=request["samples"],
        steps=request["steps"],
        eta=request["eta"],
        scale=request["scale"],
        shared_dir = minIO_clinet
    )
    end = time.time()
    # save request information in the database
    request_info = {
        "req_type": "Stable Diffusion version2 - upscaling",
        "prompt": request["prompt"],
        "runtime": (end - start),
    }
    # sending insert request to database microservice
    # requests.post(
    #     f"http://{port_config.model_ports.db[-1]}:8509/insert",
    #     data=json.dumps(request_info),
    # )
    
    os.remove(input_image_path)
    return {"response": {"image": image_path}}


# -------------------------------------- Processing Inpainting requests ---------------------------------------------------
# define Basemodel class to recive img2img request


@app.post("/Inpainting")
def submit(req: superresolution_req = Depends(), files: List[UploadFile] = File(...)):
    request = req.dict()
    uploaded_image = Image.open(files[0].file)
    mask = Image.open(files[1].file)

    input_image_path = os.path.join(
        "prediction", "samples" + "_" + str(uuid.uuid4()) + "_image.jpg"
    )
    uploaded_image.save(input_image_path)
    start = time.time()
    image_path = diff_model(
        prompt=request["prompt"],
        mode="Inpainting",
        model=model_v2_paint,
        mask=mask,
        config=None,
        image_path=input_image_path,
        seed_num=request["seed"],
        num_samples=request["samples"],
        steps=request["steps"],
        eta=request["eta"],
        scale=request["scale"],
        shared_dir = minIO_clinet
    )
    end = time.time()
    os.remove(input_image_path)

    # save request information in the database
    request_info = {
        "req_type": "Stable Diffusion version2 - inpainting",
        "prompt": request["prompt"],
        "runtime": (end - start),
    }
    # sending insert request to database microservice
    # requests.post(
    #     f"http://{port_config.model_ports.db[-1]}:8509/insert",
    #     data=json.dumps(request_info),
    # )

    return {"response": {"image": image_path}}


if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8505)
