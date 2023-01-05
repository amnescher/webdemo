"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
import argparse

import gradio as gr
import torch
from PIL import Image

from donut import DonutModel


def demo_process_vqa(input_img, question, pretrained_path = "naver-clova-ix/donut-base-finetuned-docvqa"):
    pretrained_model = DonutModel.from_pretrained(pretrained_path)
    if torch.cuda.is_available():
        pretrained_model.half()
        device = torch.device("cuda")
        pretrained_model.to(device)
    else:
        pretrained_model.encoder.to(torch.bfloat16)
    pretrained_model.eval()

    task_prompt = "<s_docvqa><s_question>{user_input}</s_question><s_answer>"
    input_img = Image.open(input_img)
    user_prompt = task_prompt.replace("{user_input}", question)
    output = pretrained_model.inference(input_img, prompt=user_prompt)["predictions"][0]
    return output


def demo_process(input_img, task_name = "cord-v2", pretrained_path = "naver-clova-ix/donut-base-finetuned-cord-v2"):
    pretrained_model = DonutModel.from_pretrained(pretrained_path)
    if torch.cuda.is_available():
        pretrained_model.half()
        device = torch.device("cuda")
        pretrained_model.to(device)
    else:
        pretrained_model.encoder.to(torch.bfloat16)
    pretrained_model.eval()
    task_prompt = f"<s_{task_name}>"
    input_img = Image.open(input_img)
    output = pretrained_model.inference(image=input_img, prompt=task_prompt)["predictions"][0]
    return output
