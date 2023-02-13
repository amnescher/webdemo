
import os
import glob
import sys
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error
from omegaconf import OmegaConf


def load_config_port():
    #Connect to MINio bucket to download config file
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
