import uvicorn
from fastapi import File, Form
from fastapi import UploadFile, Depends
import config
from typing import List, Union, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from utils import diff_model
from utils import load_files_from_minIO_bucket, load_shared_bucket
from omegaconf import OmegaConf
import requests
import time
import json


# download model weights from minio bucket and load model weights into GPU mem, load model config, download port config file from minio and return config file
model_v1, config_v1 = load_files_from_minIO_bucket()

# initialise minIO buckets for sending results to frontend
minIO_clinet = load_shared_bucket()
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
        model=model_v1,
        config=config_v1,
        strength=0.8,
        dim=(API_req.h, API_req.w),
        seed_num=API_req.seed,
        n_samples=API_req.samples,
        n_iter=API_req.n_iter,
        shared_dir = minIO_clinet
    )
    end = time.time()
    print(" Runtime--------->",(end - start))
    return {"response": {"image": image_path, "path": path, "grid_path": grid_path}}


# -------------------------------------- Processing Image to Image requests ---------------------------------------------------
# define Basemodel class to recive img2img request
class img2img_req(BaseModel):
    prompt: str
    samples: Optional[int] = None
    n_iter: Optional[int] = None
    seed: Optional[int] = None
    strength: Optional[float] = None


@app.post("/img2img")
def submit(req: img2img_req = Depends(), files: UploadFile = File(...)):
    request = req.dict()
    start = time.time()
    # generating images by the stable diffusion and return paths to generated images
    image_path, path, grid_path = diff_model(
        prompt=request["prompt"],
        mode="txt2img",
        model=model_v1,
        config=config_v1,
        image=files.file,
        strength=request["strength"],
        seed_num=request["seed"],
        n_samples=request["samples"],
        n_iter=request["n_iter"],
        shared_dir = minIO_clinet
    )
    end = time.time()
    print(" Runtime--------->",(end - start))
    # sending insert request to database microservice

    return {"response": {"image": image_path, "path": path, "grid_path": grid_path}}


if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8504)
