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


def diff_model(
    des,
    mode,
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