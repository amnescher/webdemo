from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os


def main():
    # Create a client with the MinIO server playground, its access key
    # and secret key.

    load_dotenv("storage/env.env")
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

    # Upload '/home/user/Photos/asiaphotos.zip' as object name
    # 'asiaphotos-2015.zip' to bucket 'asiatrip'.
    #Write weights of stable diffusion version 1 
    client.fput_object(
        "modelweight", "storage/model_weights/diff1/model_v1.ckpt", "storage/model_weights/diff1/model_v1.ckpt",
    )
    print(
        "'storage/model_weights/diff1/model_v1.ckpt' is successfully uploaded as "
        "object 'model_v1.ckpt' to bucket 'modelweight'."
    )
    # Write weights of stable diffusion version 1 
    client.fput_object(
        "modelweight", "storage/model_weights/diff2/model_v2_768.ckpt", "storage/model_weights/diff2/model_v2_768.ckpt",
    )
    print(
        "'storage/model_weights/diff2/model_v2_768.ckpt' is successfully uploaded as "
        "object 'model_v2_768.ckpt' to bucket 'asiatrip'."
    )

    client.fput_object(
        "modelweight", "storage/model_weights/diff2/x4-upscaler-ema.ckpt", "storage/model_weights/diff2/x4-upscaler-ema.ckpt",
    )
    print(
        "'storage/model_weights/diff2/x4-upscaler-ema.ckpt' is successfully uploaded as "
        "object 'model_v2_768.ckpt' to bucket 'asiatrip'."
    )

    client.fput_object(
        "config_data", "storage/config.yaml", "storage/config.yaml",
    )

    


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)