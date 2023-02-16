import PIL.Image as Image
import os
import glob
from scripts.img2img import img2img_infer
from scripts.txt2img import txt2img_infer
from scripts.streamlit.superresolution import inference
from scripts.streamlit.inpainting import inpainting
import shutil
from omegaconf import OmegaConf
import torch 
from ldm.util import instantiate_from_config
from scripts.streamlit.superresolution import initialize_model
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv


def diff_model(
    prompt,
    mode,
    model=None,
    config = None,
    image_path=None,
    mask = None,
    strength=0.8,
    dim=(512, 512),
    seed_num=42,
    num_samples=3,
    n_iter=2,
    eta = 0,
    scale =9,
    steps = 50,
):

    if mode == "txt2img":
        path, grid_path = txt2img_infer(
            input_prompt=prompt,
            model=model,
            config = config,
            input_plms=True,
            dim=dim,
            seed_num=seed_num,
            n_samples=num_samples,
            n_iter=n_iter,
        )

        images = glob.glob(grid_path + "/*.png")
        shutil.make_archive(path, "zip", path)
        return images[-1], path, grid_path

    elif mode == "img2img":
       
        path, grid_path = img2img_infer(
            input_image=image_path,
            input_prompt=prompt,
            model=model,
            config = config,
            input_strength=strength,
            seed_num=seed_num,
            n_samples=num_samples,
            n_iter=n_iter,
        )
        shutil.make_archive(path, "zip", path)
        images = glob.glob(grid_path + "/*.png")
        return images[-1], path, grid_path
        
    elif mode == "upscaling":
        path = inference(image_path,prompt,seed_num,scale,steps,eta,num_samples,sampler=model)
        shutil.make_archive(path, "zip", path)
        return  path
    elif mode == "Inpainting":
        path = inpainting(image_path,mask,prompt,seed_num,scale,steps,num_samples,eta,sampler=model)
        shutil.make_archive(path, "zip", path)
        return  path





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

    client = Minio(
        "minio:9000",
        access_key=access_key,
        secret_key=secret_key,secure=False
    )
    
    print("uploading model weights from MinIO bucket")
    # download model weights for txt2img/img2img, superresolution, and in-painting models from minio
    client.fget_object("modelweight", "storage/model_weights/diff2/model_v2_768.ckpt", "model_weight_gen")
    client.fget_object("modelweight", "storage/model_weights/diff2/x4-upscaler-ema.ckpt", "model_weight_scaling")
    client.fget_object("modelweight", "storage/model_weights/diff2/512-inpainting-ema.ckpt", "model_weight_inpainting")
    print("model successfully downloaded!")
    #load model config for txt2img/img2img
    config_gen = OmegaConf.load("configs/stable-diffusion/v2-inference-v.yaml")
    #load downloaded model into gpu
    model_gen = load_model_from_config(config_gen, "model_weight_gen")
    model_upScale = initialize_model("configs/stable-diffusion/x4-upscaling.yaml", "model_weight_scaling")
    model_inpainting = initialize_model("configs/stable-diffusion/v2-inpainting-inference.yaml", "model_weight_inpainting")

    client.fget_object("configdata", "storage/config.yaml", "config_file")
    port = OmegaConf.load("config_file")
    
    return model_gen, config_gen,model_upScale,model_inpainting, port
    
    
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


