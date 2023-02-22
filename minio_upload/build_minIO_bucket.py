from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os

"""
The implementation is a single node single drive ----> production level requires a loadbalncer
"""
def main():
    # Create a client with the MinIO server playground, its access key
    # and secret key.

    load_dotenv()
    access_key = os.getenv("access_key")
    secret_key = os.getenv("secret_key")
    minio_server_ip = os.environ.get('MINIO_SERVER_IP')
    
    client = Minio(
        f"{minio_server_ip}:9000",
        access_key=access_key,
        secret_key=secret_key,secure=False
    )


    # # Make 'asiatrip' bucket if not exist.
    found = client.bucket_exists("modelweight")

    if found:
        print ("Bucket 'modelweight' already exists")
    else:
        client.make_bucket("modelweight")
        client.fput_object(
        "modelweight", "storage/model_weights/diff2/model_v2_768.ckpt", "/storage/model_weights/diff2/model_v2_768.ckpt",
    )
        client.fput_object(
        "modelweight", "storage/model_weights/diff2/512-inpainting-ema.ckpt", "/storage/model_weights/diff2/512-inpainting-ema.ckpt",
    )
        client.fput_object(
        "modelweight", "storage/model_weights/diff2/x4-upscaler-ema.ckpt", "/storage/model_weights/diff2/x4-upscaler-ema.ckpt",
    )
        client.fput_object(
        "modelweight", "storage/model_weights/GFPGAN/GFPGANv1.3.pth", "/storage/model_weights/GFPGAN/GFPGANv1.3.pth",
    )

    found = client.bucket_exists("configdata")
    if found:
        print("Bucket 'config_data' already exists")
    else:
        client.make_bucket("configdata")
        client.fput_object(
        "configdata", "storage/config.yaml", "/storage/config.yaml",
    )
        

    


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)