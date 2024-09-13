

import os
from typing import Callable, Coroutine
from ai_script_video.motivation_vid.sync_automation_module import SDPrompt
from api_handlers.ideogram_api_handler import async_download_image, async_generate_image

# helper function for generating image
async def generate_download_image(prompt, image_download_path, ideogram_model="V_2_TURBO"):
    res = await async_generate_image(prompt, model=ideogram_model)

    if res is None:
        raise Exception("No response from ideogram")
    
    if res["data"] is None or len(res["data"]) == 0:
        raise Exception("No data found in response")
    
    image_url = res["data"][0]["url"]

    if image_url is None:
        raise Exception("No image url found in response")

    await async_download_image(image_url, image_download_path)

def generate_image_from_prompt(sd_prompts: list[SDPrompt], folder_name, sd_image_gen_folder_path, 
                                   ideogram_model="V_2_TURBO", 
                                   on_image_generated:Callable[[int, str], None]=lambda x, y: None)->list[Coroutine]:

    download_image_folder_path = os.path.join(sd_image_gen_folder_path, folder_name)

    # if folder name does not exist
    if (not os.path.exists(download_image_folder_path)):
        os.mkdir(download_image_folder_path)

    tasks = []
    for sd_promt_item in sd_prompts:
        tasks.append(generate_download_image_safe(download_image_folder_path, sd_promt_item, ideogram_model, on_image_generated))

    return tasks
        

# helper function
async def generate_download_image_safe(download_image_folder_path, sd_promt_item: SDPrompt, ideogram_model, on_image_generated):
    try:
        image_download_path = os.path.join(download_image_folder_path, f"{sd_promt_item.section_number}.png")

        await generate_download_image(sd_promt_item.image_prompt, image_download_path, ideogram_model=ideogram_model)

        on_image_generated(sd_promt_item.section_number, image_download_path)

    except Exception as e:
        raise Exception(f"Error when generating image from prompt: {e}")