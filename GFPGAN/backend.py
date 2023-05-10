import uvicorn
from fastapi import File,Form
from fastapi import UploadFile,Depends
import config
from typing import List, Union,Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query
from inference_gfpgan import inference
import PIL.Image as Image
import uuid
import os 
import shutil 
import glob 
import requests
from dotenv import load_dotenv
from minio import Minio


load_dotenv()
access_key = os.getenv("access_key")
secret_key = os.getenv("secret_key")

minio_server_ip = os.environ.get('MINIO_SERVER_IP')

client = Minio(
        f"{minio_server_ip}:9000",
        access_key=access_key,
        secret_key=secret_key,secure=False
    )

found = client.bucket_exists("gfpganresults")

if not found:
        client.make_bucket("gfpganresults")
        print("controlnetresults bucket was made")


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
    image_path = name = f"prediction/{str(uuid.uuid4())}.jpg"
    uploaded_image.save(image_path)
    result_path, image_path = inference(image_path, upscale=request["upscale"])
    client.fput_object(
        "gfpganresults", image_path, image_path,
    ) 
    shutil.make_archive(result_path, "zip", result_path)
    zip_path = result_path + ".zip"
    client.fput_object(
        "gfpganresults", zip_path, zip_path,
    )
    cmp_path = os.path.join(result_path, 'cmp')
    # Upload each file in the directory to the bucket
    for dirpath, dirnames, filenames in os.walk(cmp_path):
        for filename in filenames:
            file_path = os.path.join(cmp_path, filename)
                # Upload the file to the bucket
            client.fput_object(
                    bucket_name="gfpganresults",
                    object_name=file_path,
                    file_path=file_path,
                )
    return {"response":{"zip_path":zip_path,"image":image_path,"cmp_path":cmp_path}}
        

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8506)