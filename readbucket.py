from minio import Minio
from minio.error import S3Error

def main():
    # Create a client with the MinIO server playground, its access key
    # and secret key.
    client = Minio(
        "localhost:9000",
        access_key="DHyEPTDfDA0tECSo",
        secret_key="W1evynrjtBK1yAKGoE5JdrHRpIP0rWKQ",secure=False
    )

    # # Make 'asiatrip' bucket if not exist.
    found = client.bucket_exists("modelweight")

if __name__ == "__main__":
    try:
        main()
    except S3Error as exc:
        print("error occurred.", exc)