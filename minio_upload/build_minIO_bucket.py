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
        access_key = access_key,
        secret_key = secret_key,
        secure=False
    )


    # # Make 'asiatrip' bucket if not exist.


    # found = client.bucket_exists("modelweight")
    
    # if not found:
    #         client.make_bucket("modelweight")
    #         print("Bucket Made")
    # # else:
    # #      print("Bucket Found")
    # data_path = "/home/ubuntu/dev/webapp/webdemo/storage/model_weights"
    # bucketname = "modelweight"
    # for root, dirs, files in os.walk(data_path):
    #     for file in files:
    #         filepath = os.path.join(root, file)
    #         # Upload the file to the bucket with the same structure as the original folder
    #         client.fput_object(bucketname, os.path.join(bucketname, os.path.relpath(filepath, data_path)), filepath)

    client.fput_object(
        "modelweight", "model_weights/ControlNet/models/control_sd15_canny.pth", "/storage/model_weights/ControlNet/models/control_sd15_canny.pth",
    )

    


if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)