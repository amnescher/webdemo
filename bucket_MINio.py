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

    load_dotenv("./env_client.env")
    access_key = os.environ.get('access_key')
    secret_key = os.environ.get('secret_key')


    client = Minio(
        "localhost:9000",
        access_key=access_key,
        secret_key=secret_key,secure=False
    )


    # # Make 'asiatrip' bucket if not exist.
    found = client.bucket_exists("modelweight")
    if not found:
        client.make_bucket("modelweight")
    else:
        print("Bucket 'modelweight' already exists")

    # found = client.bucket_exists("configdata")
    # if not found:
    #     client.make_bucket("configdata")
    # else:
    #     print("Bucket 'config_data' already exists")
    # client.fput_object(
    #     "configdata", "storage/config.yaml", "storage/config.yaml",
    # )
    # # Upload '/home/user/Photos/asiaphotos.zip' as object name
    # # 'asiaphotos-2015.zip' to bucket 'asiatrip'.
    # #Write weights of stable diffusion version 1 
    # # client.fput_object(
    # #     "modelweight", "storage/model_weights/diff1/model_v1.ckpt", "storage/model_weights/diff1/model_v1.ckpt",
    # # )
    # # print(
    # #     "'storage/model_weights/diff1/model_v1.ckpt' is successfully uploaded as "
    # #     "object 'model_v1.ckpt' to bucket 'modelweight'."
    # # )
    # # # Write weights of stable diffusion version 1 
    # # client.fput_object(
    # #     "modelweight", "storage/model_weights/diff2/model_v2_768.ckpt", "storage/model_weights/diff2/model_v2_768.ckpt",
    # # )
    # # print(
    # #     "'storage/model_weights/diff2/model_v2_768.ckpt' is successfully uploaded as "
    # #     "object 'model_v2_768.ckpt' to bucket 'asiatrip'."
    # # )

    # client.fput_object(
    #     "modelweight", "storage/model_weights/diff2/512-inpainting-ema.ckpt", "storage/model_weights/diff2/512-inpainting-ema.ckpt",
    # )
    # print(
    #     "'storage/model_weights/diff2/512-inpainting-ema.ckpt' is successfully uploaded as "
    #     "object 'model_v2_768.ckpt' to bucket 'asiatrip'."
    # )


    # # client.fput_object(
    # #     "modelweight", "storage/model_weights/diff2/x4-upscaler-ema.ckpt", "storage/model_weights/diff2/x4-upscaler-ema.ckpt",
    # # )
    # # print(
    # #     "'storage/model_weights/diff2/x4-upscaler-ema.ckpt' is successfully uploaded as "
    # #     "object 'model_v2_768.ckpt' to bucket 'asiatrip'."
    # # )

    # # client.fput_object(
    # #     "config_data", "storage/config.yaml", "storage/config.yaml",
    # # )

    client.fput_object(
        "modelweight", "storage/model_weights/GFPGAN/GFPGANv1.3.pth", "/home/ubuntu/dev/webapp/webdemo/storage/model_weights/GFPGAN/GFPGANv1.3.pth",
    )


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)