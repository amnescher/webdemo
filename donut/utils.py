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

