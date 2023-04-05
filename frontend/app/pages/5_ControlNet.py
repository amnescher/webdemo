import streamlit as st
import numpy as np
import random
import PIL.Image as Image
import requests
import json
import os
from minio import Minio


port_config = os.getenv("ControlNet_IP")

access_key = os.getenv("access_key")
secret_key = os.getenv("secret_key")
minio_server_ip = os.environ.get('MINIO_SERVER_IP')

client = Minio(
    f"{minio_server_ip}:9000",
    access_key=access_key,
    secret_key=secret_key,secure=False
)

def delete_minIO_Folder(minioClient,bucketname, folderName):
    # Delete using "remove_object"
    objects_to_delete = minioClient.list_objects(bucketname, prefix=folderName, recursive=True)
    for obj in objects_to_delete:
        minioClient.remove_object(bucketname, obj.object_name)

# Set page title
st.set_page_config(page_title="Control Stable Diffusion with Canny Edge Maps")

# Add heading
st.markdown("## Control Stable Diffusion with Canny Edge Maps")

# Create two columns
col1, col2 = st.columns(2)

# Add input image
input_image = col1.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

# Add prompt textbox and run button
prompt = col1.text_input("Prompt")
run_button = col1.button("Run")

# Add advanced options accordion
with col2.container():
    with st.expander("Advanced options", expanded=False):
        # Add sliders and checkboxes
        num_samples = st.slider("Images", min_value=1, max_value=12, value=1, step=1)
        image_resolution = st.slider("Image Resolution", min_value=256, max_value=768, value=512, step=64)
        strength = st.slider("Control Strength", min_value=0.0, max_value=2.0, value=1.0, step=0.01)
        guess_mode = st.checkbox("Guess Mode")
        low_threshold = st.slider("Canny low threshold", min_value=1, max_value=255, value=100, step=1)
        high_threshold = st.slider("Canny high threshold", min_value=1, max_value=255, value=200, step=1)
        ddim_steps = st.slider("Steps", min_value=1, max_value=100, value=20, step=1)
        scale = st.slider("Guidance Scale", min_value=0.1, max_value=30.0, value=9.0, step=0.1)
        seed = st.slider("Seed", min_value=-1, max_value=2147, step=1, value=-1)
        eta = st.number_input("eta (DDIM)", value=0.0)
        a_prompt = st.text_input("Added Prompt", value='best quality, extremely detailed')
        n_prompt = st.text_input("Negative Prompt", value='longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality')
if  input_image:
    st.image(input_image)
if input_image and run_button and prompt:
    request_features = {
            "prompt": prompt,
            "num_samples": num_samples,
            "image_resolution": image_resolution,
            "strength": strength,
            "guess_mode": guess_mode,
            "low_threshold": low_threshold,
            "high_threshold":high_threshold,
            "ddim_steps":ddim_steps,
            "scale":scale,
            "seed":seed,
            "eta":eta,
            "a_prompt":a_prompt,
            "n_prompt":n_prompt

        }
    files = {"files": input_image.getvalue()}
    with st.spinner("Generating ..."):
        response = requests.post(f"http://{port_config}:8507/canny2image",
                        params=request_features,
                        files=files,
                )
        
        res = response.json()
        for obj in res["output"]:
                        client.fget_object(
                            "controlnetresults", obj, "grid_image"
                        )
                        st.image(Image.open("grid_image"))
                        client.remove_object("controlnetresults", obj)
        client.fget_object(
                            "controlnetresults", res["zip_path"], "zip_file"
                        )
        with open("zip_file", "rb") as file:
                        btn = st.download_button(
                            label="Download Samples",
                            data=file,
                            file_name=res["zip_path"],
                        )
        client.remove_object("controlnetresults",res["zip_path"])