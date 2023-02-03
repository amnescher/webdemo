import uvicorn
from fastapi import File,Form
from fastapi import UploadFile,Depends
import config
from typing import List, Union,Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from utils import diff_model
from utils import load_model


model_v1, config_v1 = load_model()


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
    image_path, path, grid_path = diff_model(API_req.name,"txt2img", model = model_v1, config = config_v1,strength=0.8,
    dim=(API_req.h, API_req.w),
    seed_num=API_req.seed,
    n_samples=API_req.samples,
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
    image_path, path, grid_path = diff_model(request["name"],"txt2img", model = model_v1, config = config_v1,image = files.file,strength=request["strength"],
    seed_num=request["seed"],
    n_samples=request["samples"],
    n_iter=request["n_iter"])

    return {"response":{"image":image_path,"path":path,"grid_path":grid_path}}
    


    
    
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8504)