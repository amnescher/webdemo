import uvicorn
from fastapi import File,Form
from fastapi import UploadFile,Depends
import config
from typing import List, Union,Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from inference_gfpgan import inference
import PIL.Image as Image
from stablediffusion1.utils import load_config_port
import uuid
import os 
import shutil 
import glob 
import requests


port_config = load_config_port()

try:
        requests.post(
                                f"http://{port_config.model_ports.db[-1]}:8509/initdb"
                            )
except:
        print("database initialization failed")


class RestorationFace(BaseModel):
    upscale: Optional[int] = None
    # bg_upsampler: str
    # bg_tile:Optional[int] = None

app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}



@app.post("/Restoration")
def submit(req: RestorationFace = Depends(), files: UploadFile = File(...)):
    request = req.dict()
    uploaded_image = Image.open(files.file)
    image_path = name = f"/prediction/{str(uuid.uuid4())}.jpg"
    uploaded_image.save(image_path)
    result_path, image_path = inference(image_path, upscale=request["upscale"])
    shutil.make_archive(result_path, "zip", result_path)
    cmp_path = os.path.join(result_path, 'cmp')
    return {"response":{"path":result_path,"image":image_path,"cmp_path":cmp_path}}
        

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8506)