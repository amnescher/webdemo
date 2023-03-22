import os
import sys
import uuid
import torch
import numpy as np
import streamlit as st
from PIL import Image
from omegaconf import OmegaConf
from einops import repeat, rearrange
from pytorch_lightning import seed_everything
from imwatermark import WatermarkEncoder

from scripts.txt2img import put_watermark
from ldm.models.diffusion.ddim import DDIMSampler
from ldm.models.diffusion.ddpm import LatentUpscaleDiffusion, LatentUpscaleFinetuneDiffusion
from ldm.util import exists, instantiate_from_config
from omegaconf import OmegaConf
import time 
import traceback
import requests
import json 
import shutil

torch.set_grad_enabled(False)


@st.cache(allow_output_mutation=True)
def initialize_model(config, ckpt):
    config = OmegaConf.load(config)
    model = instantiate_from_config(config.model)
    model.load_state_dict(torch.load(ckpt)["state_dict"], strict=False)
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model = model.to(device)
    sampler = DDIMSampler(model)
    return sampler


def make_batch_sd(
        image,
        txt,
        device,
        num_samples=1,
):
    image = np.array(image.convert("RGB"))
    image = torch.from_numpy(image).to(dtype=torch.float32) / 127.5 - 1.0
    batch = {
        "lr": rearrange(image, 'h w c -> 1 c h w'),
        "txt": num_samples * [txt],
    }
    batch["lr"] = repeat(batch["lr"].to(device=device), "1 ... -> n ...", n=num_samples)
    return batch


def make_noise_augmentation(model, batch, noise_level=None):
    x_low = batch[model.low_scale_key]
    x_low = x_low.to(memory_format=torch.contiguous_format).float()
    x_aug, noise_level = model.low_scale_model(x_low, noise_level)
    return x_aug, noise_level


def paint(sampler, image, prompt, seed, scale, h, w, steps, num_samples=1, callback=None, eta=0., noise_level=None):
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model = sampler.model
    seed_everything(seed)
    prng = np.random.RandomState(seed)
    start_code = prng.randn(num_samples, model.channels, h , w)
    start_code = torch.from_numpy(start_code).to(device=device, dtype=torch.float32)

    print("Creating invisible watermark encoder (see https://github.com/ShieldMnt/invisible-watermark)...")
    wm = "SDV2"
    wm_encoder = WatermarkEncoder()
    wm_encoder.set_watermark('bytes', wm.encode('utf-8'))
    with torch.no_grad(),\
            torch.autocast("cuda"):
        batch = make_batch_sd(image, txt=prompt, device=device, num_samples=num_samples)
        c = model.cond_stage_model.encode(batch["txt"])
        c_cat = list()
        if isinstance(model, LatentUpscaleFinetuneDiffusion):
            for ck in model.concat_keys:
                cc = batch[ck]
                if exists(model.reshuffle_patch_size):
                    assert isinstance(model.reshuffle_patch_size, int)
                    cc = rearrange(cc, 'b c (p1 h) (p2 w) -> b (p1 p2 c) h w',
                                   p1=model.reshuffle_patch_size, p2=model.reshuffle_patch_size)
                c_cat.append(cc)
            c_cat = torch.cat(c_cat, dim=1)
            # cond
            cond = {"c_concat": [c_cat], "c_crossattn": [c]}
            # uncond cond
            uc_cross = model.get_unconditional_conditioning(num_samples, "")
            uc_full = {"c_concat": [c_cat], "c_crossattn": [uc_cross]}
        elif isinstance(model, LatentUpscaleDiffusion):
            x_augment, noise_level = make_noise_augmentation(model, batch, noise_level)
            cond = {"c_concat": [x_augment], "c_crossattn": [c], "c_adm": noise_level}
            # uncond cond
            uc_cross = model.get_unconditional_conditioning(num_samples, "")
            uc_full = {"c_concat": [x_augment], "c_crossattn": [uc_cross], "c_adm": noise_level}
        else:
            raise NotImplementedError()

        shape = [model.channels, h, w]
        samples, intermediates = sampler.sample(
            steps,
            num_samples,
            shape,
            cond,
            verbose=False,
            eta=eta,
            unconditional_guidance_scale=scale,
            unconditional_conditioning=uc_full,
            x_T=start_code,
            callback=callback
        )
    with torch.no_grad():
        x_samples_ddim = model.decode_first_stage(samples)
    result = torch.clamp((x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0)
    result = result.cpu().numpy().transpose(0, 2, 3, 1) * 255
    st.text(f"upscaled image shape: {result.shape}")
    return [put_watermark(Image.fromarray(img.astype(np.uint8)), wm_encoder) for img in result]


def inference(image, prompt,seed,scale,steps,eta,num_samples,sampler=None,shared_dir = None):
    st.title("Stable Diffusion Upscaling")
    # run via streamlit run scripts/demo/depth2img.py <path-tp-config> <path-to-ckpt>
    if sampler == None:
        sampler = initialize_model("configs/stable-diffusion/x4-upscaling.yaml", "storage/model_weights/diff2/x4-upscaler-ema.ckpt")
    else:
        sampler = sampler
    image = Image.open(image)
    w, h = image.size
    width, height = map(lambda x: x - x % 64, (w, h))  # resize to integer multiple of 64
    image = image.resize((width, height))
    
    noise_level = None
    if isinstance(sampler.model, LatentUpscaleDiffusion):
        # TODO: make this work for all models
        noise_level = st.sidebar.number_input("Noise Augmentation", min_value=0, max_value=350, value=20)
        noise_level = torch.Tensor(num_samples * [noise_level]).to(sampler.model.device).long()

    t_progress = st.progress(0)
    def t_callback(t):
        t_progress.progress(min((t + 1) / steps, 1.))

    sampler.make_schedule(steps, ddim_eta=eta, verbose=True)
 
    result = paint(
            sampler=sampler,
            image=image,
            prompt=prompt,
            seed=seed,
            scale=scale,
            h=height, w=width, steps=steps,
            num_samples=num_samples,
            callback=t_callback,
            noise_level=noise_level,
            eta=eta
        )

    outpath = "prediction"
    sample_path = os.path.join(outpath, "samples"+"_"+str(uuid.uuid4())+"_"+str(seed))
    os.makedirs(sample_path, exist_ok=True)
    for base_count,image in enumerate(result):
        save_path = os.path.join(sample_path, f"{base_count:05}.png")
        image.save(save_path)
        shared_dir.fput_object(
        "diffusion2results", save_path, save_path,
    ) 

    # --------- Writing results to minIO bucket ----------
    
    return sample_path
        



    
