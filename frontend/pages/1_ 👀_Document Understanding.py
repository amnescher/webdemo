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
st.set_page_config(page_title="Document Understanding", page_icon="👀")


st.sidebar.header("Select a service")
app_mode = st.sidebar.selectbox(
   "Options",
    [ "Info","Document Parsing","Document Visual Question Answering"],
)
if app_mode == "Info":
    st.markdown("# Document Understanding Demo")
    st.write(
    """Document images, such as commercial invoices, receipts, IDs, and business cards, are easy to find in modern working environments. To extract useful information from such document images, Eschercloud AI offers state-of-the-art Document Understanding  (DU) models for different industries with applications 
    including document classification, information extraction and visual question answering. """
)

if app_mode=="Document Parsing":

        st.markdown("Document Parsing")
        uploaded_file = st.file_uploader("Upload a image", type=["jpg", "jpeg", "png"])
        run = st.button("Parsing")
        if uploaded_file:
            st.image(Image.open(uploaded_file))
        if uploaded_file and run:
            files = {"file": uploaded_file.getvalue()}
            res = requests.post(f"http://{port_config.model_ports.donut[-1]}:8503/donut_pars", files=files)
            response = res.json()
            st.text_area(label="Output Data:", value=response, height=300)

elif app_mode=="Document Visual Question Answering": 

        st.markdown("Document Visual Question Answering")

        uploaded_file = st.file_uploader("Upload a image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(Image.open(uploaded_file))
            user_input = st.text_input("QUESTION")
            run = st.button("Parsing")
        if uploaded_file and run:
            files = {"file": uploaded_file.getvalue()}
            data={"question":user_input}
            res = requests.post(f"http://{config.model_ports.donut[-1]}:8503/donut_vqa", data = data, files=files)
            response = res.json()
            st.text_area(label="Output Data:", value=response, height=300)

