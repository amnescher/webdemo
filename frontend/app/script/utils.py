from omegaconf import OmegaConf
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os


def load_config_port():
    load_dotenv("storage/env.env")
    #Connect to MINio bucket to download config file
    access_key = os.environ.get('access_key')
    secret_key = os.environ.get('secret_key')
    client = Minio(
                    "localhost:9000",
                    access_key=access_key,
                    secret_key=secret_key,secure=False
                    )
    # read configuration file includes port informations
    client.fget_object("configdata", "storage/config.yaml", "config_file")
    port = OmegaConf.load("config_file")
    return port