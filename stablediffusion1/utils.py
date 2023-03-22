import PIL.Image as Image
import base64
import os
import glob
import sys
from scripts.img2img import img2img_infer
from scripts.txt2img import txt2img_infer
import shutil
import random
import string
import uuid
import torch
from ldm.util import instantiate_from_config
from omegaconf import OmegaConf
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv


def load_model_from_config(config, ckpt, verbose=False):
    print(f"Loading model from {ckpt}")
    pl_sd = torch.load(ckpt, map_location="cpu")
    if "global_step" in pl_sd:
        print(f"Global Step: {pl_sd['global_step']}")
    sd = pl_sd["state_dict"]
    model = instantiate_from_config(config.model)
    m, u = model.load_state_dict(sd, strict=False)
    if len(m) > 0 and verbose:
        print("missing keys:")
        print(m)
    if len(u) > 0 and verbose:
        print("unexpected keys:")
        print(u)
    model.cuda()
    model.eval()

    return model


def load_files_from_minIO_bucket():

    # connect to minio bucket and download and return model weight and config file needed by stable diffusion
    # returns loaded model, model configuration file and port configuration file

    # Load access key and secret key to connect to minIO server
    #connect to minio bucket
    load_dotenv()
    access_key = os.getenv("access_key")
    secret_key = os.getenv("secret_key")

    minio_server_ip = os.environ.get('MINIO_SERVER_IP')
    
    client = Minio(
        f"{minio_server_ip}:9000",
        access_key=access_key,
        secret_key=secret_key,secure=False
    )
    # Load model congiguration
    config = OmegaConf.load("configs/stable-diffusion/v1-inference.yaml")
    print("Downloading model from MinIO bucket")
    # Download model's weight from minio bucket and load model weight
    client.fget_object(
        "modelweight", "model_weights/diff1/model_v1.ckpt", "model_weight"
    )
    model = load_model_from_config(config, "model_weight")
    # Download port conf file from minio bucker and load config fie
    # client.fget_object("configdata", "storage/config.yaml", "config_file")
    # port = OmegaConf.load("config_file")

    return model, config

def load_shared_bucket():
    load_dotenv()
    access_key = os.getenv("access_key")
    secret_key = os.getenv("secret_key")

    minio_server_ip = os.environ.get('MINIO_SERVER_IP')
    
    client = Minio(
        f"{minio_server_ip}:9000",
        access_key=access_key,
        secret_key=secret_key,secure=False
    )

    found = client.bucket_exists("diffusion1results")

    if not found:
        client.make_bucket("diffusion1results")

    return client





def diff_model(
    prompt,
    mode,
    model=None,
    config=None,
    image=None,
    strength=0.8,
    dim=(512, 512),
    seed_num=42,
    n_samples=3,
    n_iter=2,
    shared_dir = None
):
    """
    Returns path to generated images by stable diffudion
    grid_path: path to grid of generated images
    path: path to directory that stores generated images

    Args:
    prompt: user prompt to generate image based on it
    mode: stable diffusion mode, options: txt2img, txt2img
    model: stable difusion model
    config: model configuration file
    input_plms, seed_num,n_samples, are stable diffusion input args
    """

    if mode == "txt2img":
        path, grid_path = txt2img_infer(
            input_prompt=prompt,
            model=model,
            config=config,
            input_plms=True,
            dim=dim,
            seed_num=seed_num,
            n_samples=n_samples,
            n_iter=n_iter,
        )

        images = glob.glob(grid_path + "/*.png")
        shutil.make_archive(path, "zip", path)
        #-------- Writing files to minIO Buckets ------
        zip_path = path + ".zip"
        shared_dir.fput_object(
        "diffusion1results", images[-1], images[-1],
    )
        shared_dir.fput_object(
        "diffusion1results", zip_path, zip_path,
    )
        
        shutil.rmtree(grid_path)
        os.remove(zip_path)
        
        return images[-1], path, grid_path

    elif mode == "img2img":
        uploaded_image = Image.open(image)

        letters = string.ascii_lowercase
        result_str = "".join(random.choice(letters) for i in range(15))
        image_path = "stableDiffusion/test_image/" + result_str + "_" + image.name
        uploaded_image.convert("RGB").save(image_path)
        path, grid_path = img2img_infer(
            input_image=image_path,
            input_prompt=prompt,
            input_strength=strength,
            seed_num=seed_num,
            n_samples=n_samples,
            n_iter=n_iter
        )

        shutil.make_archive(path, "zip", path)
        images = glob.glob(grid_path + "/*.png")

        # --------- Writing results to minIO bucket ----------
        zip_path = path + ".zip"
        shared_dir.fput_object(
        "diffusion1results", images[-1], images[-1],
    )
        shared_dir.fput_object(
        "diffusion1results", zip_path, zip_path,
    )   
        
        shutil.rmtree(grid_path)
        os.remove(zip_path)
        return images[-1], path, grid_path
