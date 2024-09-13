import asyncio

from ai_script_video.motivation_vid.async_automation_modules import generate_image_from_prompt
from ai_script_video.motivation_vid.sync_automation_module import SDPrompt


async def f(t):
    await asyncio.sleep(1)
    print(t)

def generate_sd_prompt_images(sd_prompts):
    def on_image_generated(sec_num, image_path):
        print(f"Image generated for section {sec_num} at {image_path}")

    tasks = generate_image_from_prompt(sd_prompts, "test_async", "D:\\Projects\\video_fiction_generation\\test\\test_img", on_image_generated=on_image_generated)

    async def run_task():
        await asyncio.gather(*tasks)
    asyncio.run(run_task())


def main():
    # await asyncio.gather(*(f(t) for t in "abcdefghigklmn"))      
    # print("done")

    prompts = [
        "a white cate riding a bike, pixar style",
        "an astronaut in space licking an icecream cone, realistic style",
        "four cute puppies playing basketball, anime style",
        "a walking tree monster in a forest, design style",
    ]

    tasks = []

    sd_prompts = []
    for i in range(len(prompts)):
        sd_prompts.append(SDPrompt(section_number=i, section_script="", image_prompt=prompts[i]))

    generate_sd_prompt_images(sd_prompts=sd_prompts)
        