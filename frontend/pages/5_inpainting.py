import sys
import cv2
import numpy as np
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas


st.title("Stable Diffusion Inpainting")

image = st.file_uploader("Image", ["jpg", "png"])
if image:
    image = Image.open(image)
    w, h = image.size
    print(f"loaded input image of size ({w}, {h})")
    width, height = map(lambda x: x - x % 64, (w, h))  # resize to integer multiple of 32
    image = image.resize((width, height))

    prompt = st.text_input("Prompt")

    seed = st.number_input("Seed", min_value=0, max_value=1000000, value=0)
    num_samples = st.number_input("Number of Samples", min_value=1, max_value=64, value=1)
    scale = st.slider("Scale", min_value=0.1, max_value=30.0, value=10., step=0.1)
    ddim_steps = st.slider("DDIM Steps", min_value=0, max_value=50, value=50, step=1)
    eta = st.sidebar.number_input("eta (DDIM)", value=0., min_value=0., max_value=1.)

    fill_color = "rgba(255, 255, 255, 0.0)"
    stroke_width = st.number_input("Brush Size",
                                    value=64,
                                    min_value=1,
                                    max_value=100)
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
    if canvas_result:
        mask = canvas_result.image_data
        mask = mask[:, :, -1] > 0
        if mask.sum() > 0:
            mask = Image.fromarray(mask)
            st.write("Inpainted")
