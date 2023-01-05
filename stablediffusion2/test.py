import uvicorn
from fastapi import File,Form
from fastapi import UploadFile,Depends
# import config
# from typing import List, Union,Optional
#from pydantic import BaseModel
from fastapi import FastAPI, Query
#from utils import diff_model
#import PIL.Image as Image
# import uuid


# class txt2img_req(BaseModel):
#     name: str
#     w: int
#     h: int
#     samples: int
#     n_iter: int
#     seed:int
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome from the API"}


if __name__ == "__main__":
    uvicorn.run("test:app", host="0.0.0.0", port=8505)   
print("*****************TEST******************")