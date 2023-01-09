
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


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )
add_bg_from_local("/home/storage/frontend/logo.jpeg")   

port_config = OmegaConf.load("/home/storage/config.yaml")




port_config = OmegaConf.load("/home/storage/config.yaml")
#st.set_page_config(page_title="Stable Difussion Version 1", page_icon="🖼")
st.sidebar.header("Select a service")
app_mode = st.sidebar.selectbox(
   "Options",
    [ "Info","Image Generation","Image Modification"],
)
if app_mode == "Info":
    st.markdown("# Stable Diffusion Version 1")
    st.write(
    """ StableDiffusion 1 """
)


if app_mode == "Image Generation":
    desc = st.text_input("Prompt", value=" portrait photo of a old man crying, Tattles, sitting on bed, guages in ears, looking away, serious eyes, 50mm portrait photography, hard rim lighting photography–beta –ar 2:3 –beta –upbeta", key = "Description_key")
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1], gap="small")
    with c1:
        w = st.number_input("Width", value=512, step=64, key = "Width_key")
    with c2:
        h = st.number_input("Height", value=512, step=64, key = "Height_key")
    with c3:
        s = st.number_input("Seed", value=42, step=1, key = "Seed_key")
    with c4:
        samples = st.number_input("samples", value=3, step=1, key = "samples_key")

    with c5:
        n_iter = st.number_input("iterations", value=3, step=1, key = "iterations_key")

    run = st.button("Generate")
    if run and desc:
        payload = {"name": desc, "w":w,"h":h,"samples":samples,"n_iter":n_iter,"seed":s}
        res = requests.post(f"http://{port_config.model_ports.stablediff1[-1]}:8504/txt2img", data=json.dumps(payload))
        response = res.json()
        st.image(Image.open(response["response"]["image"]))
        zip_path = response["response"]["path"]
        grid_path = response["response"]["grid_path"]
        with open(zip_path + ".zip", "rb") as file:
            btn = st.download_button(
                label="Download Samples",
                data=file,
                file_name=zip_path + ".zip",
            )
        shutil.rmtree(zip_path)
        shutil.rmtree(grid_path)
        os.remove(zip_path + ".zip")
# image to image 
elif app_mode == "Image Modification":
    uploaded_file = st.file_uploader(
        "Upload a image: image should be larger than 256x256",
        type=["jpg", "jpeg", "png"],
    )
    if uploaded_file:
        st.image(uploaded_file)
        image = Image.open(uploaded_file)
        w, h = image.size
        if w< 256 or h <256:
            uploaded_file = False
            st.text(f"loaded input image of size ({w}, {h}). Image should be larger than 256x256")
    if uploaded_file:
        desc = st.text_input(
            "Description",
            value=" A boat is sailing in a fictional ocean in front of mountains."
        ,key = "Description_key")
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="small")
        with c1:
            strng = st.number_input(
                "Strength (0,1):", value=0.8, step=0.01, format="%.2f"
            , key=str(uuid.uuid4()))
        with c2:
            s = st.number_input("Seed", value=42, step=1, key = "Seed_key")
        with c3:
            samples = st.number_input("samples", value=1, step=1, key = "samples_key")
        with c4:
            n_iter = st.number_input("iterations", value=3, step=1,key = "iterations_key")

        run = st.button("Generate")
        if  desc and run:
            files = {'files': uploaded_file.getvalue()}
            payload =payload = {"name": desc,"samples":samples,"n_iter":n_iter,"seed":s,"strength":strng}
            res = requests.post(f"http://{port_config.model_ports.stablediff1[-1]}:8504/img2img", params=payload, files=files)
            response = res.json()
            st.image(Image.open(response["response"]["image"]))
            zip_path = response["response"]["path"]
            grid_path = response["response"]["grid_path"]
            with open(zip_path + ".zip", "rb") as file:
                btn = st.download_button(
                    label="Download Samples",
                    data=file,
                    file_name=zip_path + ".zip",
                )
            shutil.rmtree(zip_path)
            shutil.rmtree(grid_path)
            os.remove(zip_path + ".zip")
