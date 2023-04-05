from share import *
import config

import cv2
import einops
import numpy as np
import torch
import random
import PIL.Image as Image
from pytorch_lightning import seed_everything
from annotator.util import resize_image, HWC3
from annotator.canny import CannyDetector
from cldm.model import create_model, load_state_dict
from cldm.ddim_hacked import DDIMSampler
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os 

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
        secret_key=secret_key,
        secure=False
    )

    # Load model congiguration
    print("Downloading model from MinIO bucket")
    # Download model's weight from minio bucket and load model weight
    client.fget_object(
        "modelweight", "model_weights/ControlNet/models/control_sd15_canny.pth", "model_weight"
    )
    return "model_weight"

def load_shared_bucket():
    
    load_dotenv()
    access_key = os.getenv("access_key")
    secret_key = os.getenv("secret_key")

    minio_server_ip = os.environ.get('MINIO_SERVER_IP')
    
    client = Minio(
        f"{minio_server_ip}:9000",
        access_key=access_key,
        secret_key=secret_key,
        secure=False
    )

    found = client.bucket_exists("controlnetresults")

    if not found:
        client.make_bucket("controlnetresults")

    return client
def load_model():
    apply_canny = CannyDetector()
    model = create_model('./models/cldm_v15.yaml').cpu()
    model_weight= load_files_from_minIO_bucket()
    model.load_state_dict(load_state_dict(model_weight, location='cuda'))
    model = model.cuda()
    ddim_sampler = DDIMSampler(model)
    print("******** Model Loaded **********")
    return apply_canny,model, ddim_sampler

def process(input_image, prompt, a_prompt, n_prompt, num_samples, image_resolution, ddim_steps, guess_mode, strength, scale, seed, eta, low_threshold, high_threshold,apply_canny,model,ddim_sampler):
    with torch.no_grad():
        img = resize_image(HWC3(input_image), image_resolution)
        H, W, C = img.shape

        detected_map = apply_canny(img, low_threshold, high_threshold)
        detected_map = HWC3(detected_map)

        control = torch.from_numpy(detected_map.copy()).float().cuda() / 255.0
        control = torch.stack([control for _ in range(num_samples)], dim=0)
        control = einops.rearrange(control, 'b h w c -> b c h w').clone()

        if seed == -1:
            seed = random.randint(0, 65535)
        seed_everything(seed)

        if config.save_memory:
            model.low_vram_shift(is_diffusing=False)

        cond = {"c_concat": [control], "c_crossattn": [model.get_learned_conditioning([prompt + ', ' + a_prompt] * num_samples)]}
        un_cond = {"c_concat": None if guess_mode else [control], "c_crossattn": [model.get_learned_conditioning([n_prompt] * num_samples)]}
        shape = (4, H // 8, W // 8)

        if config.save_memory:
            model.low_vram_shift(is_diffusing=True)

        model.control_scales = [strength * (0.825 ** float(12 - i)) for i in range(13)] if guess_mode else ([strength] * 13)  # Magic number. IDK why. Perhaps because 0.825**12<0.01 but 0.826**12>0.01
        samples, intermediates = ddim_sampler.sample(ddim_steps, num_samples,
                                                     shape, cond, verbose=False, eta=eta,
                                                     unconditional_guidance_scale=scale,
                                                     unconditional_conditioning=un_cond)

        if config.save_memory:
            model.low_vram_shift(is_diffusing=False)

        x_samples = model.decode_first_stage(samples)
        x_samples = (einops.rearrange(x_samples, 'b c h w -> b h w c') * 127.5 + 127.5).cpu().numpy().clip(0, 255).astype(np.uint8)

        results = [x_samples[i] for i in range(num_samples)]
    return [255 - detected_map] + results
