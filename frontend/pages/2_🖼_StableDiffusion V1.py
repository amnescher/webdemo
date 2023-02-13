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
from itertools import cycle
import json
import time

from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from omegaconf import OmegaConf

def load_config_port():
    load_dotenv()
    access_key = os.getenv("access_key")
    secret_key = os.getenv("secret_key")
    client = Minio(
                    "minio:9000",
                    access_key=access_key,
                    secret_key=secret_key,secure=False
                    )
    # read configuration file includes port informations
    client.fget_object("configdata", "storage/config.yaml", "config_file")
    port = OmegaConf.load("config_file")
    return port


#add_bg_from_local("/home/storage/frontend/logo.jpeg")

port_config = load_config_port()



st.sidebar.header("Select a demo")
app_mode = st.sidebar.selectbox(
    "Options",
    ["Info", "Image Generation", "Image Modification","Exploring"],
)
if app_mode == "Info":
    st.markdown("# Stable Diffusion Version 1")
    st.write(
        """ ### What is Stable Diffusion Image Generator?

Stable Diffusion Image Generator (SDIG) is an AI-powered technology used to generate visuals from text. This technology uses Computer Vision algorithms and NLP technology to analyze the text input and generate visuals from it. SDIG is a revolutionary technology that has made it easier for artists to create original artwork with minimal effort. The visuals generated by SDIG are unique and one-of-a-kind, making it perfect for creating original artwork. SDIG is also able to generate visuals from different types of text, including poetry, lyrics, and stories.

### How Stable Diffusion Image Generator is Transforming Various Industries?

Stable Diffusion Image Generator is transforming various industries with its revolutionary technology.
Here are some of the ways that SDIG is transforming various industries:

**Advertising and Marketing:** AI-generated images from text can be used to create unique visuals for advertising and **marketing campaigns.** These visuals can be used to promote products and services in a more engaging way.

**Web Design:** AI-generated images from text can be used to create unique visuals for websites. These visuals can help make websites more visually appealing and engaging.

**Graphic Design:** AI-generated images from text can be used to create unique visuals for graphic design projects. These visuals can help make designs more dynamic and engaging.
"""
    )

port_config = OmegaConf.load("/home/storage/config.yaml")

if app_mode == "Image Generation":
    st.markdown("# Stable Diffusion Version 1 - Image Generation")
    # Get configuration from user
    desc = st.text_input(
        "Prompt",
        value=" portrait photo of a old man crying, Tattles, sitting on bed, guages in ears, looking away, serious eyes, 50mm portrait photography, hard rim lighting photography–beta –ar 2:3 –beta –upbeta",
        key="Description_key",
    )
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1], gap="small")
    with c1:
        w = st.number_input("Width", value=512, step=64, key="Width_key")
    with c2:
        h = st.number_input("Height", value=512, step=64, key="Height_key")
    with c3:
        s = st.number_input("Seed", value=42, step=1, key="Seed_key")
    with c4:
        samples = st.number_input("samples", value=3, step=1, key="samples_key")

    with c5:
        n_iter = st.number_input("iterations", value=3, step=1, key="iterations_key")

    run = st.button("Generate")
    if run and desc:
        # make request body
        payload = {
            "name": desc,
            "w": w,
            "h": h,
            "samples": samples,
            "n_iter": n_iter,
            "seed": s,
        }
        #Send reuest 
        with st.spinner("Generating ..."):
            start = time.time()
            res = requests.post(
                f"http://{port_config.model_ports.stablediff1[-1]}:8504/txt2img",
                data=json.dumps(payload)
            )
            end = time.time()
        try:
            response = res.json()
            zip_path = response["response"]["path"]
            grid_path = response["response"]["grid_path"]
            st.success('Successful!')
            payload = {
                    "req_type": "Stable Diffusion version1 - txt2img",
                    "prompt": desc,
                    "runtime": (end - start)
                    }

            db_req = requests.post(
                f"http://{port_config.model_ports.db[-1]}:8509/insert",
                data=json.dumps(payload),
            )

            st.image(Image.open(response["response"]["image"]))
            
            # enable user to download the generated image in a zip file
            with open(zip_path + ".zip", "rb") as file:
                btn = st.download_button(
                    label="Download Samples",
                    data=file,
                    file_name=zip_path + ".zip",
                )
            shutil.rmtree(zip_path)
            shutil.rmtree(grid_path)
            os.remove(zip_path + ".zip")

        except NameError:
            st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")
        except json.decoder.JSONDecodeError: 
            st.error('Unsuccessful. Encountered an error. Please try again!', icon="🚨")
        
# image to image
elif app_mode == "Image Modification":
    st.markdown("# Stable Diffusion Version 1 - Image Modification")
    # upload input image
    uploaded_file = st.file_uploader(
        "Upload a image: image should be larger than 256x256",
        type=["jpg", "jpeg", "png"],
    )
    if uploaded_file:
        #check if image size is not smaller than 256*256
        st.image(uploaded_file)
        image = Image.open(uploaded_file)
        w, h = image.size
        if w < 256 or h < 256:
            uploaded_file = False
            st.text(
                f"loaded input image of size ({w}, {h}). Image should be larger than 256x256"
            )
    if uploaded_file:
        # get input prompt and configuration from user
        Prompt = st.text_input(
            "Prompt",
            value=" A boat is sailing in a fictional ocean in front of mountains.",
            key="Description_key",
        )
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="small")
        with c1:
            strng = st.number_input(
                "Strength (0,1):",
                value=0.8,
                step=0.01,
                format="%.2f",
                key="Strength_key",
            )
        with c2:
            s = st.number_input("Seed", value=42, step=1, key="Seed_key")
        with c3:
            samples = st.number_input("samples", value=1, step=1, key="samples_key")
        with c4:
            n_iter = st.number_input(
                "iterations", value=3, step=1, key="iterations_key"
            )

        run = st.button("Generate")
        # make request boday and sending request
        if Prompt and run:
            files = {"files": uploaded_file.getvalue()}
            payload = payload = {
                "name": Prompt,
                "samples": samples,
                "n_iter": n_iter,
                "seed": s,
                "strength": strng,
            }
            with st.spinner("Generating ..."):
                start = time.time()
                res = requests.post(
                    f"http://{port_config.model_ports.stablediff1[-1]}:8504/img2img",
                    params=payload,
                    files=files,
                )
                end = time.time()
            #get the response back that includes pathes to generated images
            try:
                response = res.json()
                zip_path = response["response"]["path"]
                grid_path = response["response"]["grid_path"]
                st.success('Successful!')

                payload = {
                    "req_type": "Stable Diffusion version1 - img2img",
                    "prompt": Prompt,
                    "runtime": (end - start)
                    }

                db_req = requests.post(
                f"http://{port_config.model_ports.db[-1]}:8509/insert",
                data=json.dumps(payload),
            )
                st.image(Image.open(response["response"]["image"]))
                #enable user to download generated image
                with open(zip_path + ".zip", "rb") as file:
                    btn = st.download_button(
                        label="Download Samples",
                        data=file,
                        file_name=zip_path + ".zip",
                    )
                #delete generated images/directory to save space
                shutil.rmtree(zip_path)
                shutil.rmtree(grid_path)
                os.remove(zip_path + ".zip")
            
            except NameError:
                st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")
            except json.decoder.JSONDecodeError: 
                st.error('Unsuccessful. Encountered an error. Please try again!', icon="🚨")
elif app_mode == "Exploring":
    f = open('storage/frontend/exploring_stable_v1/prompt.json')
    images = json.load(f)

    cols = cycle(st.columns(2)) # st.columns here since it is out of beta at the time I'm writing this
    for key,val in images.items() :
        next(cols).image(Image.open("storage/frontend/exploring_stable_v1/"+key), width=256, caption=val)

