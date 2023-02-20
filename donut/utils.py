import PIL.Image as Image
import base64
from app import demo_process, demo_process_vqa
from train import train, save_config_file
import os
import glob
import sys
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from omegaconf import OmegaConf

def donut_app(image, mode, question=""):
    if mode == "parsing":
        return demo_process(image)
    if mode == "vqa":
        return demo_process_vqa(image, question)
    return None

def load_config_port():
    #Connect to MINio bucket to download config file
    load_dotenv()
    access_key = os.getenv("access_key")
    secret_key = os.getenv("secret_key")

    minio_server_ip = os.environ.get('MINIO_SERVER_IP')
    client = Minio(
        f"{minio_server_ip}:9000",
        access_key=access_key,
        secret_key=secret_key,secure=False
    )
    # read configuration file includes port informations
    client.fget_object("configdata", "storage/config.yaml", "config_file")
    port = OmegaConf.load("config_file")
    return port

