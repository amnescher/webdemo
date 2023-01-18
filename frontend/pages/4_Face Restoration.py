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


port_config = OmegaConf.load("/home/storage/config.yaml")

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


        
# image to image
if app_mode == "Face Restoration":
    st.markdown("# Face Restoration")
    st.markdown("# Face Restoration")
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
                res = requests.post(
                    f"http://{port_config.model_ports.gfpgan[-1]}:8506/Restoration",
                    params=payload,
                    files=files,
                )
            try:
                #get the respons includes paths to generated images
                response = res.json()
                cmp_path = response["response"]["cmp_path"]
                image_path = response["response"]["image"]
                result_path = response["response"]["path"]
                st.success('Successful!')
                st.image(Image.open(image_path))
                cmp_list = glob(os.path.join(cmp_path, "*.png"))
                st.info("Left: Before face restoration.    Right: After face restoration.", icon="ℹ️")
                for filename in cmp_list:
                     im = Image.open(filename)
                     st.image(im)

                with open(result_path + ".zip", "rb") as file:
                    btn = st.download_button(
                        label="Download Results",
                        data=file,
                        file_name=result_path + ".zip",
                    )
                    # delete generated images and directories
                shutil.rmtree(result_path)
                os.remove(result_path + ".zip")
            #     # enable user to download generated images 
            except NameError:
                st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")
            except json.decoder.JSONDecodeError: 
                st.error('Unsuccessful. Encountered an error. Please try again!', icon="🚨")
        
            