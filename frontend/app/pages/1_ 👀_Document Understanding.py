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

from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from omegaconf import OmegaConf

load_dotenv()
port_config = os.getenv("DOUNAT_IP")


access_key = os.getenv("access_key")
secret_key = os.getenv("secret_key")
minio_server_ip = os.environ.get('MINIO_SERVER_IP')

client = Minio(
    f"{minio_server_ip}:9000",
    access_key=access_key,
    secret_key=secret_key,secure=False
)

#add_bg_from_local("/home/storage/frontend/logo.jpeg")
#image_id = Image.open("/home/images/frontend/ocr.jpeg")

st.sidebar.header("Select a demo")
# load port configuration

app_mode = st.sidebar.selectbox(
    "Options",
    ["Info", "Document Parsing", "Document Visual Question Answering"],
)
if app_mode == "Info":
    st.markdown("# Document Understanding")
    #st.image(image_id)
    # add description
    st.write(
        """## What is Document Understanding?

Document understanding also known as Optical Character Recognition (OCR) is a technology that enables the recognition of characters from images and scanned documents. It is used to extract text from images and make it available in a digital format that can be read and understood by humans and machines. OCR technology is used to automate document processing, improve compliance, and enable automation. OCR has the potential to streamline processes and help organizations save time and money. 


## Common OCR Applications and Use Cases

OCR technology is used in a variety of applications and use cases. The most common OCR applications and use cases include document management, document processing, known your customer (KYC), know your business (KYB) and data entry.
In document management, OCR technology is used to quickly and accurately process documents and extract information. This can help organizations save time and money by automating document processing and improving accuracy and compliance. In document processing, OCR technology is used to quickly and accurately process customer information. This can help organizations improve customer experience by providing customers with accurate and up-to-date information.
When it comes to KYC and KYB checks, businesses process many identity documents manually or by using solutions with limited automation. This entails inaccuracies in customer identity data and slower user flows. OCR can extract data from any type of identity document, including passports, ID cards, driving licenses, residence permits and others. OCR allows businesses to scan and recognize identity documents Namely, it can recognize complex ID documents regardless of differences in their formats and structures. In data entry, OCR technology is used to quickly and accurately process data and extract information. This can help organizations improve accuracy and reduce errors by automating data entry.


## The Benefits of OCR

The most obvious benefit of OCR is its ability to automate document processing. By using OCR, organizations can quickly and accurately process documents without having to manually enter data. This can help reduce document processing time and costs. In addition, OCR can help improve accuracy and compliance. By using OCR, organizations can quickly and accurately process documents and ensure that the information is accurate and up-to-date. This helps to reduce errors and ensure compliance with regulations. The use of OCR technology can also help to improve the customer experience. By using OCR, organizations can quickly and accurately process customer information and provide customers with a better experience. This can help to improve customer satisfaction and loyalty. Finally, OCR technology can help organizations reduce costs. By using OCR, organizations can quickly and accurately process documents without having to manually enter data. This can help to reduce document processing time and costs, which can lead to cost savings for organizations.
         """
    )

if app_mode == "Document Parsing":
    st.markdown("# Document Information Extraction")
    st.write(
        "Document information extraction tasks a document image and the AI model returns structured form of information existed in the image. The AI model not only reads the characters well, but also understand the layouts and semantics to infer the groups and nested hierarchies among the texts."
    )
    #Load input image
    uploaded_file = st.file_uploader("Upload a image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(Image.open(uploaded_file))
        run = st.button("Parsing")
    if uploaded_file and run:
        files = {"file": uploaded_file.getvalue()}
        with st.spinner("Processing ..."):
        #send request to backend donut model
            start = time.time()
            res = requests.post(
                f"http://{port_config}:8503/donut_pars", files=files
            )
            end = time.time()
        #get the response back from backend
        try:
                response = res.json()
                 # show the response 
                st.text_area(label="Output Data:", value=response, height=300)
                payload = {
                    "req_type": "Donut - parsing",
                    "runtime": (end - start)
                    }

            #     db_req = requests.post(
            #     f"http://{port_config}:8509/insert",
            #     data=json.dumps(payload),
            # )
        except NameError:
                st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")
        except json.decoder.JSONDecodeError: 
                st.error('Unsuccessful. Encountered an error. Please try again!', icon="🚨")
       
       

elif app_mode == "Document Visual Question Answering":

    st.markdown("# Document Visual Question Answering")

    st.write(
        " In Document Visual Question Answering a document image and question pair is given and the AI model predicts the answer for the question by capturing both visual and textual information within the image."
    )
    #Load input image
    uploaded_file = st.file_uploader("Upload a image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(Image.open(uploaded_file))
        #get the input question
        user_input = st.text_input("QUESTION")
        run = st.button("Parsing")
    if uploaded_file and run:
        files = {"file": uploaded_file.getvalue()}
        data = {"question": user_input}
        with st.spinner("Processing ..."):
        #send request to backend
            start = time.time()
            res = requests.post(
                f"http://{port_config}:8503/donut_vqa",
                data=data,
                files=files,
            )
            end = time.time()
        # get the response back and show the results
        try:
                response = res.json()
                 # show the response 
                st.text_area(label="Output Data:", value=response, height=300)
                payload = {
                    "req_type": "Donut - vqa",
                    "prompt":user_input,
                    "runtime": (end - start)
                    }
                db_req = requests.post(
                f"http://{port_config}:8509/insert",
                data=json.dumps(payload),
            )
        except NameError:
                st.error('Unsuccessful. Encountered an error. Try again!', icon="🚨")
        except json.decoder.JSONDecodeError: 
                st.error('Unsuccessful. Encountered an error. Please try again!', icon="🚨")
