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


model_v1, config_v1 = load_model()


image_path, path, grid_path = diff_model("Animal","txt2img",model=model_v1,config=config_v1,strength=0.8,n_samples=1,n_iter=1)
image_path, path, grid_path = diff_model("Animal","txt2img",model=model_v1,config=config_v1,strength=0.8,n_samples=1,n_iter=1)

image_path, path, grid_path = diff_model("Animal","txt2img",model=model_v1,config=config_v1,strength=0.8,n_samples=1,n_iter=1)

