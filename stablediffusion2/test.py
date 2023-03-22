import uvicorn
from fastapi import File,Form
from fastapi import UploadFile,Depends
import config
from typing import List, Union,Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from stablediffusion1.utils import diff_model
import PIL.Image as Image
import uuid
import traceback
from omegaconf import OmegaConf
import requests
import json
import time
import torch 

from stablediffusion1.utils import load_model, diff_model


model_v2, config_v2, model_v2_up,model_v2_paint = load_model()
mask = Image.open("/home/storage/painting/mask.png")    
image_path = '/home/storage/painting/image.png'
    #f"/prediction/{str(uuid.uuid4())}.jpg"
    #uploaded_image.save(image_path)
image_path = diff_model(
    "red eyes",
    "Inpainting",
    model=model_v2_paint,
    config = None,
    image_path="/home/storage/painting/image.png",
    mask = mask,
    strength=0.8,
    dim=(512, 512),
    seed_num=42,
    num_samples=3,
    n_iter=2,
    eta = 0,
    scale =9,
    steps = 50,
) 


