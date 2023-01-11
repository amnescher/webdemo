import PIL.Image as Image
import base64
import os
import glob
import sys
from scripts.img2img import img2img_infer
from scripts.txt2img import txt2img_infer
from scripts.streamlit.superresolution import inference
import shutil
import random
import string
import uuid


def diff_model(
    prompt,
    mode,
    image_path=None,
    strength=0.8,
    dim=(512, 512),
    seed_num=42,
    num_samples=3,
    n_iter=2,
    eta = 0,
    scale =9,
    steps = 50
):

    if mode == "txt2img":
        path, grid_path = txt2img_infer(
            input_prompt=prompt,
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
            input_strength=strength,
            seed_num=seed_num,
            n_samples=num_samples,
            n_iter=n_iter,
        )
        shutil.make_archive(path, "zip", path)
        images = glob.glob(grid_path + "/*.png")
        return images[-1], path, grid_path
        
    elif mode == "upscaling":
        path = inference(image_path,prompt,seed_num,scale,steps,eta,num_samples)
        shutil.make_archive(path, "zip", path)
        return  path
diff_model(
    "test",
    "txt2img",
    image_path=None,
    strength=0.8,
    dim=(256, 256),
    seed_num=42,
    num_samples=3,
    n_iter=2,
    eta = 0,
    scale =9,
    steps = 50
)