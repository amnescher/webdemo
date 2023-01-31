import uvicorn
from fastapi import File,Form
from fastapi import UploadFile,Depends
import config
from typing import List, Union,Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from utils import diff_model
import PIL.Image as Image
import uuid
import traceback
from omegaconf import OmegaConf
import requests
import json

class txt2img_req(BaseModel):
    name: str
    w: int
    h: int
    samples: int
    n_iter: int
    seed:int
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


@app.post("/txt2img")
def read_items(API_req: txt2img_req):
    image_path, path, grid_path = diff_model(API_req.name,"txt2img",strength=0.8,
    dim=(API_req.h, API_req.w),
    seed_num=API_req.seed,
    num_samples=API_req.samples,
    n_iter=API_req.n_iter)

    return {"response":{"image":image_path,"path":path,"grid_path":grid_path}}
  

class img2img_req(BaseModel):
    name: str
    samples: Optional[int] = None
    n_iter: Optional[int] = None
    seed:Optional[int] = None
    strength: Optional[float] = None

@app.post("/img2img")
def submit(req: img2img_req = Depends(), files: UploadFile = File(...)):
    request = req.dict()
    uploaded_image = Image.open(files.file)
    image_path = name = f"/home/storage/test_image/{str(uuid.uuid4())}.jpg"
    uploaded_image.save(image_path)
    image_path, path, grid_path = diff_model(request["name"],"img2img",image_path = image_path ,strength=request["strength"],
    seed_num=request["seed"],
    num_samples=request["samples"],
    n_iter=request["n_iter"])
    return {"response":{"image":image_path,"path":path,"grid_path":grid_path}}
    

class superresolution_req(BaseModel):
    prompt: str
    samples: Optional[int] = None
    steps: Optional[int] = None
    seed:Optional[int] = None
    scale: Optional[float] = None
    eta: Optional[float] = None

@app.post("/upscale")
def submit(req: superresolution_req = Depends(), files: UploadFile = File(...)):
    request = req.dict()
    uploaded_image = Image.open(files.file)
    image_path= name = f"/home/storage/test_image/{str(uuid.uuid4())}.jpg"
    uploaded_image.save(image_path)
    port_config = OmegaConf.load("/home/storage/config.yaml")
    
    image_path = diff_model(request["prompt"],"upscaling",image_path = image_path,
    seed_num=request["seed"],
    num_samples=request["samples"],
    steps=request["steps"],
    eta = request["eta"],
    scale =request["scale"] )
    
    


    return {"response":{"image":image_path}}

    
    
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8505)