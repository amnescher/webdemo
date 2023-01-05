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


def Donut():
    doc_pars = st.checkbox("Document Parsing")
    doc_vqa = st.checkbox("Document Visual Question Answering")
    fine_tune = st.checkbox("Fine-tune Donut on custom dataset")

    if doc_pars:
        uploaded_file = st.file_uploader("Upload a image", type=["jpg", "jpeg", "png"])
        run = st.button("Parsing")
        if uploaded_file:
            st.image(Image.open(uploaded_file))
        if uploaded_file and run:
            files = {"file": uploaded_file.getvalue()}
            res = requests.post(f"http://donut:8503/donut_pars", files=files)
            response = res.json()
            st.text_area(label="Output Data:", value=response, height=300)

    if doc_vqa: 
        uploaded_file = st.file_uploader("Upload a image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(Image.open(uploaded_file))
            user_input = st.text_input("QUESTION")
            run = st.button("Parsing")
        if uploaded_file and run:
            files = {"file": uploaded_file.getvalue()}
            data={"question":user_input}
            res = requests.post(f"http://donut:8503/donut_vqa", data = data, files=files)
            response = res.json()
            st.text_area(label="Output Data:", value=response, height=300)


def stable_diffusion_frontend(app_mode):
    upscl = None
    img2img = st.checkbox("Image Modification")
    txt2img = st.checkbox("Image Generation") 
    if app_mode == "Image Generation - Stable Diffusion 2":
        upscl = st.checkbox("Upscaling") 

    if txt2img:
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

            if app_mode == "Image Generation - Stable Diffusion 2":
                res = requests.post(f"http://0.0.0.0:8505/txt2img", data=json.dumps(payload))

            elif app_mode == "Image Generation - Stable Diffusion 1":
                res = requests.post(f"http://backend_stable1:8504/txt2img", data=json.dumps(payload))

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
    if img2img and not txt2img:
        uploaded_file = st.file_uploader(
            "Upload a image: image should be larger than 256x256",
            type=["jpg", "jpeg", "png"],
        )
        if uploaded_file:
            st.image(uploaded_file)
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
        if uploaded_file and desc and run:
            files = {'files': uploaded_file.getvalue()}
            payload =payload = {"name": desc,"samples":samples,"n_iter":n_iter,"seed":s,"strength":strng}
            if app_mode == "Image Generation - Stable Diffusion 2":
                res = requests.post(f"http://0.0.0.0:8505/img2img", params=payload, files=files)

            elif app_mode == "Image Generation - Stable Diffusion 1":
                res = requests.post(f"http://backend_stable1:8504/img2img", params=payload, files=files)
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
    if upscl and not txt2img and not img2img:
            uploaded_file = st.file_uploader(
            "Upload a image",
            type=["jpg", "jpeg", "png"],
        )
            if uploaded_file:
                image = Image.open(uploaded_file)
                w, h = image.size
                st.text(f"loaded input image of size ({w}, {h})")
                width, height = map(lambda x: x - x % 64, (w, h))  # resize to integer multiple of 64
                st.image(image)

                st.write(f"\n Tip: Add a description of the object that should be upscaled, e.g.: 'a professional photograph of a cat'")
                prompt = st.text_input("Prompt", "a high quality professional photograph")
                seed = st.number_input("Seed", min_value=0, max_value=1000000, value=0)
                num_samples = st.number_input("Number of Samples", min_value=1, max_value=64, value=1)
                scale = st.slider("Scale", min_value=0.1, max_value=30.0, value=9.0, step=0.1)
                steps = st.slider("DDIM Steps", min_value=2, max_value=250, value=50, step=1)
                eta = st.sidebar("eta (DDIM)", value=0., min_value=0., max_value=1., step=0.01)
                run = st.button("Generate")

                if uploaded_file and run :
                    files = {'files': uploaded_file.getvalue()}
                    payload = {"prompt": prompt,"samples":num_samples,"steps":steps,"seed":seed,"scale":scale,"eta":eta}
                    res = requests.post(f"http://0.0.0.0:8505/upscale", params=payload, files=files)
                    response = res.json()
                    zip_path = response["response"]["image"]
                    filename_list = glob(os.path.join(zip_path, "*.png"))
                    for filename in filename_list: 
                        im=Image.open(filename)
                        st.image(image)

                    with open(zip_path + ".zip", "rb") as file:
                        btn = st.download_button(
                            label="Download Samples",
                            data=file,
                            file_name=zip_path + ".zip",
                        )
                    shutil.rmtree(zip_path)
                    os.remove(zip_path + ".zip")

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


add_bg_from_local("storage/frontend/logo.jpeg")

st.sidebar.title("What to do")
st.sidebar.title("What to do")
st.title("EscherCloud AI Computer Vision Demo")
app_mode = st.sidebar.selectbox(
    "Select an application",
    ["Donut","Image Generation - Stable Diffusion 1","Image Generation - Stable Diffusion 2"],
)  # , "Face Recognition","Face Recognition-server", "About"])

if app_mode == "Donut":
    Donut()
elif app_mode == "Image Generation - Stable Diffusion 2":
    stable_diffusion_frontend(app_mode)
elif app_mode == "Image Generation - Stable Diffusion 1":
    stable_diffusion_frontend(app_mode)
