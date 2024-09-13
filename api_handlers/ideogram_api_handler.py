from typing import Any, List
import aiohttp
from dotenv import load_dotenv
import os
import asyncio

import requests

# load_dotenv("../.env")
load_dotenv()

headers = {
    "Api-Key": os.getenv("IDEOGRAM_API_KEY"),
    "Content-Type": "application/json"
}

url = "https://api.ideogram.ai/generate"

models = ["V_1", "V_1_TURBO", "V_2", "V_2_TURBO"]
aspect_ratios = [
    "ASPECT_10_16",
    "ASPECT_16_10",
    "ASPECT_9_16",
    "ASPECT_16_9",
    "ASPECT_3_2",
    "ASPECT_2_3",
    "ASPECT_4_3",
    "ASPECT_3_4",
    "ASPECT_1_1",
    "ASPECT_1_3",
    "ASPECT_3_1"
]

style_types = ["GENERAL", "REALISTIC", "DESIGN", "RENDER_3D", "ANIME"]

def generate_image(prompt, model="V_2_TURBO", aspect_ratio="ASPECT_16_9", style_type="GENERAL"):
    base_req =  {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "model": model,
        "magic_prompt_option": "AUTO"
    }

    if (model == "V_2" or model == "V_2_TURBO") and style_type is not None:
        base_req["style_type"] = style_type

    payload = { "image_request": base_req }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()

async def async_generate_image(prompt, model="V_2_TURBO", aspect_ratio="ASPECT_16_9", style_type="GENERAL"):
    base_req =  {
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "model": model,
        "magic_prompt_option": "AUTO"
    }

    if (model == "V_2" or model == "V_2_TURBO") and style_type is not None:
        base_req["style_type"] = style_type

    payload = { "image_request": base_req }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await response.json()
        


def download_image(image_url, image_path):
    response = requests.get(image_url, headers=headers)

    with open(image_path, "wb+") as f:
        f.write(response.content)

    return image_path

async def async_download_image(image_url, image_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url, headers=headers) as response:
            image_data = await response.read()

            with open(image_path, "wb+") as f:
                f.write(image_data)

            return image_path