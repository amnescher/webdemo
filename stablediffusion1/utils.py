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

def load_model():
        config = OmegaConf.load("configs/stable-diffusion/v1-inference.yaml")
        model = load_model_from_config(config, "storage/model_weights/diff1/model_v1.ckpt")
        return model, config

def diff_model(
    des,
    mode,
    model = None,
    config = None,
    image=None,
    strength=0.8,
    dim=(512, 512),
    seed_num=42,
    n_samples=3,
    n_iter=2,
):

    if mode == "txt2img":
        path, grid_path = txt2img_infer(
            input_prompt=des,
            model = model,
            config = config,
            input_plms=True,
            dim=dim,
            seed_num=seed_num,
            n_samples=n_samples,
            n_iter=n_iter,
        )

        images = glob.glob(grid_path + "/*.png")
        shutil.make_archive(path, "zip", path)
        return images[-1], path, grid_path

    elif mode == "img2img":
        uploaded_image = Image.open(image)

        letters = string.ascii_lowercase
        result_str = "".join(random.choice(letters) for i in range(15))
        image_path = "stableDiffusion/test_image/" + result_str + "_" + image.name
        uploaded_image.save(image_path)
        path, grid_path = img2img_infer(
            input_image=image_path,
            input_prompt=des,
            input_strength=strength,
            seed_num=seed_num,
            n_samples=n_samples,
            n_iter=n_iter,
        )
        shutil.make_archive(path, "zip", path)
        images = glob.glob(grid_path + "/*.png")

        return images[-1], path, grid_path

