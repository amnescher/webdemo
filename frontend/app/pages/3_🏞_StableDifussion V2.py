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
import time 
import traceback
import sys
from streamlit_drawable_canvas import st_canvas

from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from omegaconf import OmegaConf

#add_bg_from_local("/home/storage/frontend/logo.jpeg")
#Read port config file

def delete_minIO_Folder(minioClient,bucketname, folderName):
    # Delete using "remove_object"
    objects_to_delete = minioClient.list_objects(bucketname, prefix=folderName, recursive=True)
    for obj in objects_to_delete:
        minioClient.remove_object(bucketname, obj.object_name)


load_dotenv()
port_config = os.getenv("STABLE_V2_IP")


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
    ["Info", "Image Generation", "Image Modification", "Upscaling","Inpainting"],
)
if app_mode == "Info":
    st.markdown("# Stable Diffusion Version 2")
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

#-------------------------------------- text to image----------------------
if app_mode == "Image Generation":
    st.markdown("# Stable Diffusion Version 2 - Image Generation")
    #Read input prompt and user configs 
    Prompt = st.text_input(
        "Prompt",
        value=" portrait photo of a old man crying, Tattles, sitting on bed, guages in ears, looking away, serious eyes, 50mm portrait photography, hard rim lighting photography–beta –ar 2:3 –beta –upbeta",
        key="Description_key",
    )
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1], gap="small")
    with c1:
        w = st.number_input("Width", value=768, step=64, key="Width_key")
    with c2:
        h = st.number_input("Height", value=768, step=64, key="Height_key")
    with c3:
        s = st.number_input("Seed", value=42, step=1, key="Seed_key")
    with c4:
        samples = st.number_input("samples", value=3, step=1, key="samples_key")

    with c5:
        n_iter = st.number_input("iterations", value=3, step=1, key="iterations_key")

    run = st.button("Generate")
    if run and Prompt:
        # make request body and send it
        payload = {
            "prompt": Prompt,
            "w": w,
            "h": h,
            "samples": samples,
            "n_iter": n_iter,
            "seed": s,
        }
        with st.spinner("Generating ..."):
            
            # try:
                res = requests.post(
                    f"http://{port_config}:8505/txt2img",
                    data=json.dumps(payload),
                )
                
            
                response = res.json()
                zip_path = response["response"]["path"]
                grid_path = response["response"]["grid_path"]

                image_from_bucket = response["response"]["image"]
                zip_file_bucket = response["response"]["path"] + ".zip"

                

                client.fget_object(
                        "diffusion2results", image_from_bucket, "grid_image"
                    )
                client.fget_object(
                        "diffusion2results", zip_file_bucket, "zip_file"
                    )
                
                st.image(Image.open("grid_image"))
                st.success('Successful!')

                # enable user to download generated images
                with open("zip_file", "rb") as file:
                    btn = st.download_button(
                        label="Download Samples",
                        data=file,
                        file_name=zip_path + ".zip",
                    )
                # --- delete results from minIO storage --------
                delete_minIO_Folder(client,"diffusion2results",grid_path)
                client.remove_object("diffusion2results",zip_file_bucket)

            # except Exception:
            #     st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")
            

            
# -------------------------------------------   image to image --------------

elif app_mode == "Image Modification":
    st.markdown("# Stable Diffusion Version 2 - Image Modification")
    # upload input image
    uploaded_file = st.file_uploader(
        "Upload a image: image should be larger than 256x256",
        type=["jpg", "jpeg", "png"],
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        w, h = image.size
        st.info(f"Loaded input image of size ({w}, {h})", icon="ℹ️")
        st.image(uploaded_file)
        #check if image size is not smaller than 256*256
        image = Image.open(uploaded_file)
        w, h = image.size
        if w < 256 or h < 256:
            uploaded_file = False
            st.text(
                f"loaded input image of size ({w}, {h}). Image should be larger than 256x256"
            )
    if uploaded_file:
        # get the prompt and configuration from user
        prompt = st.text_input(
            "Prompt",
            value=" painting, Van Gogh style, high quality, close shot, blue flowers, summer time.",
            key="Description_key",
        )
        c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="small")
        with c1:
            strng = st.number_input(
                "Strength (0,1):",
                min_value=0.0, max_value=1.0, value=0.8, step=0.01,
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
        if prompt and run:
            #make request body and send it
            files = {"files": uploaded_file.getvalue()}
            payload = {
                "prompt": prompt,
                "samples": samples,
                "n_iter": n_iter,
                "seed": s,
                "strength": strng,
            }
            with st.spinner("Generating ..."):
                
                try:
                    res = requests.post(
                        f"http://{port_config}:8505/img2img",
                        params=payload,
                        files=files,
                    )
                    
                
                    # get the respons includes paths to generated images
                    response = res.json()
                    zip_path = response["response"]["path"]
                    grid_path = response["response"]["grid_path"]
                    image_from_bucket = response["response"]["image"]
                    zip_file_bucket = response["response"]["path"] + ".zip"

                    

                    client.fget_object(
                            "diffusion2results", image_from_bucket, "grid_image"
                        )
                    client.fget_object(
                            "diffusion2results", zip_file_bucket, "zip_file"
                        )
                    
                    st.image(Image.open("grid_image"))
                    st.success('Successful!')

                    # enable user to download generated images
                    with open("zip_file", "rb") as file:
                        btn = st.download_button(
                            label="Download Samples",
                            data=file,
                            file_name=zip_path + ".zip",
                        )
                    # --- delete results from minIO storage --------
                    delete_minIO_Folder(client,"diffusion2results",grid_path)
                    client.remove_object("diffusion2results",zip_file_bucket)
                except Exception:
                    st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")
                

                   
# -------------------------------------------   Super resolution --------------
elif app_mode == "Upscaling":
    st.markdown("# Stable Diffusion Version 2 - Image Up Scaling")
    uploaded_file = st.file_uploader(
        "Upload a image",
        type=["jpg", "jpeg", "png"],
    )
    if uploaded_file:
        # upload inmage
        image = Image.open(uploaded_file)
        w, h = image.size
        st.info(f"Loaded input image of size ({w}, {h})", icon="ℹ️")
        st.image(image)
        # get prompt from user
        st.write(
            f"\n Tip: Add a description of the object that should be upscaled, e.g.: 'a professional photograph of a cat'"
        )
        prompt = st.text_input("Prompt", "a high quality professional photograph")
        c1, c2 = st.columns([1, 1], gap="small")
        with c1:
            seed = st.number_input("Seed", min_value=1, max_value=1000000, value=42)
        with c2:
            num_samples = st.number_input(
            "Number of Samples", min_value=1, max_value=64, value=1
        )
        c1, c2,c3 = st.columns([1, 1,1], gap="small")
        with c1:
            scale = st.slider("Scale", min_value=0.1, max_value=30.0, value=9.0, step=0.1)
        with c2:
            steps = st.slider("DDIM Steps", min_value=2, max_value=250, value=50, step=1)
        with c3:
            eta = st.slider(
            "eta (DDIM)", min_value=0.0, max_value=1.0, value=0.0, step=0.01
        )
        run = st.button("Generate")
        if uploaded_file and run:
            # make request body and send request
            files = {"files": uploaded_file.getvalue()}
            payload = {
                "prompt": prompt,
                "samples": num_samples,
                "steps": steps,
                "seed": seed,
                "scale": scale,
                "eta": eta,
            }
            with st.spinner("Generating ..."):
                
                try:
                    res = requests.post(
                        f"http://{port_config}:8505/upscale",
                        params=payload,
                        files=files,
                    )

                    response = res.json()
                # get the response back that includes path to generated image
                    response_path = response["response"]["image"]
                    directory_path = response_path + "/"
                    zip_file_bucket = response_path + ".zip"
                    objects_in_dir = client.list_objects("diffusion2results", prefix=directory_path, recursive=True)
                    for obj in objects_in_dir:
                        client.fget_object(
                            "diffusion2results", obj.object_name, "grid_image"
                        )
                        st.image(Image.open("grid_image"))
                    st.success('Successful!')
                    client.fget_object(
                            "diffusion2results", zip_file_bucket, "zip_file"
                        )
                    # enable users to download generated images
                    with open("zip_file", "rb") as file:
                        btn = st.download_button(
                            label="Download Samples",
                            data=file,
                            file_name=zip_file_bucket,
                        )
                    delete_minIO_Folder(client,"diffusion2results",response_path)
                    client.remove_object("diffusion2results",zip_file_bucket)
                    
                except Exception:
                    st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")





# -------------------------------------------   INpainting --------------





elif app_mode == "Inpainting":

    st.title("Stable Diffusion Inpainting")

    image_uploaded = st.file_uploader("Image", ["jpg", "jpeg", "png"])
    if image_uploaded:
        image = Image.open(image_uploaded)
        w, h = image.size
        if w <256 or h< 256:
            st.info(f"Loaded input image resized into ({w}, {h})", icon="ℹ️")
            st.info(f"image too small, should be larger than 256x256", icon="ℹ️")
        else:
            width, height = map(lambda x: x - x % 64, (w, h))  # resize to integer multiple of 32
            image = image.resize((width, height))
            st.info(f"Loaded input image resized into ({width}, {height})", icon="ℹ️")
            prompt = st.text_input("Prompt")

            seed = st.number_input("Seed", min_value=0, max_value=1000000, value=0)
            num_samples = st.number_input("Number of Samples", min_value=1, max_value=64, value=1)
            scale = st.slider("Scale", min_value=0.1, max_value=30.0, value=10., step=0.1)
            ddim_steps = st.slider("DDIM Steps", min_value=0, max_value=50, value=50, step=1)
            eta = st.number_input("eta (DDIM)", value=0., min_value=0., max_value=1.)
            stroke_width = st.slider("Stroke width: ", 1, 25, 3)
            
            fill_color = "rgba(255, 255, 255, 0.0)"
            stroke_color = "rgba(255, 255, 255, 1.0)"
            bg_color = "rgba(0, 0, 0, 1.0)"
            drawing_mode = "freedraw"

            st.write("Canvas")
            st.caption(
                "Draw a mask to inpaint, then click the 'Send to Streamlit' button (bottom left, with an arrow on it).")
            canvas_result = st_canvas(
                fill_color=fill_color,
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color=bg_color,
                background_image=image,
                update_streamlit=False,
                height=height,
                width=width,
                drawing_mode=drawing_mode,
                key="canvas",
            )
            if canvas_result.image_data is not None:
                mask = canvas_result.image_data
                mask = mask[:, :, -1] > 0
                if mask.sum() > 0:
                    mask = Image.fromarray(mask)
                    mask_name =  "samples"+"_"+str(uuid.uuid4())+"_"+str(seed) + "_mask.png"
                    image_name =  "samples"+"_"+str(uuid.uuid4())+"_"+str(seed) + "_image.png"
                    mask.save(mask_name, "PNG")
                    image.convert("RGB").save(image_name, "PNG")
                    files = [
            ('files',('image1', open(image_name,'rb'), 'image/png') ),
            ('files', ('image2', open(mask_name,'rb'), 'image/png'))
            ]
                    
                    payload = {
                    "prompt": prompt,
                    "samples": num_samples,
                    "steps": ddim_steps,
                    "seed": seed,
                    "scale": scale,
                    "eta": eta,
                }
                    run = st.button("Generate")
                    if run:
                        with st.spinner("Generating ..."):
                                res = requests.post(
            
                                    f"http://{port_config}:8505/Inpainting",
                                    params=payload,
                                    files=files,
                                )
                                response = res.json()
            
                            # get the response back that includes path to generated image
                                response_path = response["response"]["image"]
                                directory_path = response_path + "/"
                                zip_file_bucket = response_path + ".zip"
                                objects_in_dir = client.list_objects("diffusion2results", prefix=directory_path, recursive=True)
                                for obj in objects_in_dir:
                                    client.fget_object(
                                        "diffusion2results", obj.object_name, "grid_image"
                                    )
                                    st.image(Image.open("grid_image"))
                                st.success('Successful!')
                                client.fget_object(
                                        "diffusion2results", zip_file_bucket, "zip_file"
                                    )
                                # enable users to download generated images
                                with open("zip_file", "rb") as file:
                                    btn = st.download_button(
                                        label="Download Samples",
                                        data=file,
                                        file_name=zip_file_bucket,
                                    )
                                delete_minIO_Folder(client,"diffusion2results",response_path)
                                client.remove_object("diffusion2results",zip_file_bucket)
                                os.remove(image_name)
                                os.remove(mask_name)
                            # except Exception:
                            #     st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")