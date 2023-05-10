import streamlit as st
import numpy as np
import PIL.Image as Image
import os
import shutil
import requests
import json
import uuid
import base64
from glob import glob
from omegaconf import OmegaConf
import datetime
import time
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from omegaconf import OmegaConf
import zipfile
import io

load_dotenv()
port_config = os.getenv("FACERES_IP")

access_key = os.getenv("access_key")
secret_key = os.getenv("secret_key")
minio_server_ip = os.environ.get('MINIO_SERVER_IP')

client = Minio(
    f"{minio_server_ip}:9000",
    access_key=access_key,
    secret_key=secret_key,secure=False
)


st.sidebar.header("Select a demo")

app_mode = st.sidebar.selectbox(
    "Options",
    ["Info", "Face Restoration"],
)

if app_mode == "Info":
    st.markdown("# Face Restoration")
    st.write(
        """ ### 
"""
    )
    st.write(
        """ ### Why Face Restoration?

Face images are always one of the most popular types of images in our daily life, which record 
long-lasting precious memories and provide crucial information for identity analysis. Unfortunately, due to the limited conditions in the acquisition, storage and transmission devices, the degradations of face images are still ubiquitous in most real-world applications. The degraded face images not only impede human visual perception but also degrade face-related applications such as video surveillance and face recognition. This challenge motivates the restoration of high-quality (HQ) face images from the low-quality (LQ) face inputs which contain unknown degradations 
(e.g., blur, noise, compression), known as blind face restoration (BFR).
"""
    )
if app_mode == "Face Restoration":
    # upload input image
    uploaded_file = st.file_uploader(
        "Upload a image",
        type=["jpg", "jpeg", "png"],
    )

   
    if uploaded_file:
        st.image(uploaded_file)
        #check if image size is not smaller than 256*256
        image = Image.open(uploaded_file)
        # get the prompt and configuration from user
        upscale = st.number_input("upscale", value=2, step=1, key="Seed_key")
        run = st.button("Generate")
        if run:
            #make request body and send it
            files = {"files": uploaded_file.getvalue()}
            payload = {
                "upscale": upscale
            }
            with st.spinner("Generating ..."):
                start = time.time()
                res = requests.post(
                    f"http://{port_config}:8506/Restoration",
                    params=payload,
                    files=files,
                )
                end = time.time()
            try:
                #get the respons includes paths to generated images
                response = res.json()
                image_path = response["response"]["image"]
                client.fget_object(
                            "gfpganresults", image_path, "grid_image"
                        )
                # cmp_path = response["response"]["cmp_path"]
                # image_path = response["response"]["image"]
                zip_path = response["response"]["zip_path"]
                cmp_dir = response["response"]["cmp_path"]
                # st.success('Successful!')
                    
                st.image(Image.open("grid_image"))
                # cmp_list = glob(os.path.join(cmp_path, "*.png"))
                # st.info("Left: Before face restoration.    Right: After face restoration.", icon="ℹ️")
                # for filename in cmp_list:
                #      im = Image.open(filename)
                #      st.image(im)
                objects = client.list_objects(bucket_name="gfpganresults", prefix=cmp_dir, recursive=True)

                # Read each file in the directory
                for obj in objects:
                        # Download the file contents

                        file_data = client.get_object("gfpganresults", obj.object_name).read()
                        im = Image.open(io.BytesIO(file_data))
                        st.image(im)
                        

                client.fget_object(
                            "gfpganresults", zip_path, "zip_file"
                        )

                with open("zip_file", "rb") as file:
                                btn = st.download_button(
                                    label="Download Samples",
                                    data=file,
                                    file_name=zip_path,
                                )
                # with open(result_path + ".zip", "rb") as file:
                #     btn = st.download_button(
                #         label="Download Results",
                #         data=file,
                #         file_name=result_path + ".zip",
                #     )
                #     # delete generated images and directories
                # shutil.rmtree(result_path)
                # os.remove(result_path + ".zip")
              # enable user to download generated images 
            except NameError:
                st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")
            except json.decoder.JSONDecodeError: 
                st.error('Unsuccessful. Encountered an error. Please try again!', icon="🚨")