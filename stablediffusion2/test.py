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
import time
import torch 

from utils import load_model


model_v2, config_v2 = load_model(model="txt2img")
#model_v2, _ = load_model(model="upscaling")
# start = time.time()
# image_path, path, grid_path = diff_model("Animal","txt2img",model=model_v2,config=config_v2,strength=0.8,num_samples=1,n_iter=1)
# image_path, path, grid_path = diff_model("Animal","txt2img",model=model_v2,config=config_v2,strength=0.8,num_samples=1,n_iter=1)
# image_path, path, grid_path = diff_model("Animal","txt2img",model=model_v2,config=config_v2,strength=0.8,num_samples=1,n_iter=1)
# end = time.time()
# print("-----------Time----------->",end-start)
