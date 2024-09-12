import os
from pydantic import BaseModel
from ai_script_video.puzzle_video.puzzle_script_generation import generate_script
from api_handlers.chatgpt_api_handler import call_chatGPT, openai_client
from api_handlers.coqui_tts_handler import voice_over
from api_handlers.ideogram_api_handler import download_image, generate_image

from moviepy.editor import *

raw_script_to_sd_prompt_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\raw_script_to_sd_prompt"

sd_image_gen_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\image_gen_dir"
voice_over_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\voice_over_dir"

raw_concate_video_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\raw_concate_dir"

ideogram_model = "V_2_TURBO"

class ScriptItem(BaseModel):
    section_number: int
    section_script: str

class SDPrompt(ScriptItem):
    section_number: int
    section_script: str
    image_prompt: str

class SDPromptList(BaseModel):
    sections: list[SDPrompt]

def generate_raw_script(system_prompt, prompt):
    res = call_chatGPT(system_prompt, prompt, model="gpt-4o-mini")

    if res is None:
        raise Exception("No response from chatGPT")
    
    first_valid_message = res.first_valid_message

    if first_valid_message is None:
        raise Exception("No valid message found in response")
    
    if first_valid_message.role != "assistant":
        raise Exception("First valid message is not from assistant")
    
    return first_valid_message.content

def generate_sd_prompts(raw_script)->list[SDPrompt]:
    with open(raw_script_to_sd_prompt_path, "r") as f:
        sys_prompt = f.read()

    try:
        res = call_chatGPT(sys_prompt, raw_script, model="gpt-4o-mini", response_format=SDPromptList, chatGPT_completion_func=openai_client.beta.chat.completions.parse)

        if res is None:
            raise Exception("No response from chatGPT")
        
        first_valid_message = res.first_valid_message

        if first_valid_message is None:
            raise Exception("No valid message found in response")
        
        if first_valid_message.parsed is None:
            raise Exception("No valid parsed message found in response")
        
        if "sections" not in first_valid_message.parsed.dict().keys():
            raise Exception("No valid parsed message found in response: expect 'sections' key")
        
        return first_valid_message.parsed.sections
    except Exception as e:
        raise Exception(f"Error when generating sd prompts: {e}")


class FilePathMap(BaseModel):
    section_number: int
    path: str

def generate_image_from_prompt(sd_prompts: list[SDPrompt], folder_name):
    download_image_folder_path = os.path.join(sd_image_gen_folder_path, folder_name)

    # if folder name does not exist
    if (not os.path.exists(download_image_folder_path)):
        os.mkdir(download_image_folder_path)

    image_path_maps = []
    for sd_promt_item in sd_prompts:
        try:
            image_download_path = os.path.join(download_image_folder_path, f"{sd_promt_item.section_number}.png")

            generate_download_image(sd_promt_item.image_prompt, image_download_path)

            # need change to more stable persistence method. i.e. database
            image_path_maps.append(FilePathMap(section_number=sd_promt_item.section_number, path=image_download_path))
        
        except Exception as e:
            raise Exception(f"Error when generating image from prompt: {e}")
        
    return image_path_maps

# helper function for generating image
def generate_download_image(prompt, image_download_path):
    res = generate_image(prompt, model=ideogram_model)

    if res is None:
        raise Exception("No response from ideogram")
    
    if res["data"] is None or len(res["data"]) == 0:
        raise Exception("No data found in response")
    
    image_url = res["data"][0]["url"]

    if image_url is None:
        raise Exception("No image url found in response")

    download_image(image_url, image_download_path)


def generate_voice_over(script_items: list[ScriptItem], folder_name):
    voice_over_path = os.path.join(voice_over_folder_path, folder_name)

    # if folder name does not exist
    if (not os.path.exists(voice_over_path)):
        os.mkdir(voice_over_path)

    voice_over_path_maps: list[FilePathMap] = []

    for script_item in script_items:
        output_path = os.path.join(voice_over_path, f"{script_item.section_number}.mp3")
        voice_over(script_item.section_script, output_path)

        voice_over_path_maps.append(FilePathMap(section_number=script_item.section_number, path=output_path))
    
    return voice_over_path_maps

# helper
def get_map_by_number(maps: list[dict], section_number):
    for m in maps:
        if m.section_number == section_number:
            return m


# mergin in seconds (waits between scripts sections)
def merge_voice_over_image(unsorted_voice_over_path_maps:list[FilePathMap], unsorted_image_path_maps:list[FilePathMap], margin=0.5):
    voice_over_path_map = sorted(unsorted_voice_over_path_maps, key=lambda k: k.section_number)

    video_clips = []
    for vm in voice_over_path_map:
        img_item = get_map_by_number(unsorted_image_path_maps, vm.section_number)

        img = ImageClip(img_item.path)
        audio = AudioFileClip(vm.path)

        img = img.set_duration(audio.duration + margin)     # margin/2 + audio + margin/2

        img = img.set_audio(CompositeAudioClip([audio.set_start(margin/2)]))

        video_clips.append(img)
    

    concated_video = concatenate(video_clips, padding=0, method="compose")

    return concated_video


def save_video(video, output_path):
    video.write_videofile(output_path, codec="libx264", fps=24)






sample_script = """Poetry is the chosen language of childhood and youth. The baby
repeats words again and again for the mere joy of their sound:
the melody of nursery rhymes gives a delight which is quite
independent of the meaning of the words. Not until youth approaches
maturity is there an equal pleasure in the rounded periods of
elegant prose. It is in childhood therefore that the young mind
should be stored with poems whose rhythm will be a present delight
and whose beautiful thoughts will not lose their charm in later
years.

The selections for the lowest grades are addressed primarily to
the feeling for verbal beauty, the recognition of which in the
mind of the child is fundamental to the plan of this work. The
editors have felt that the inclusion of critical notes in these
little books intended for elementary school children would be not
only superfluous, but, in the degree in which critical comment
drew the child's attention from the text, subversive of the desired
result. Nor are there any notes on methods. The best way to teach
children to love a poem is to read it inspiringly to them.
The French say: "The ear is the pathway to the heart." A poem
should be so read that it will sing itself in the hearts of the
listening children.

In the brief biographies appended to the later books the human
element has been brought out. An effort has been made to call
attention to the education of the poet and his equipment for his
life work rather than to the literary qualities of his style.
"""

"""
Use case

script = generate_raw_script("You are a childern story writer. Expert in writing stories and award winning", "write a childern bedtime story for kids 8 to 12 years old. Be fun and fairy tale. should tell a moral. and should be in duration between 5 to 8 minutes") 


sd_prompts = generate_sd_prompts(script)  

img_path_maps = generate_image_from_prompt(sd_prompts, "kids_story1")

voice_over_path_maps = generate_voice_over(sd_prompts, "kids_story1")

raw_video = merge_voice_over_image(voice_over_path_maps, img_path_maps)

output_path = os.path.join(raw_concate_video_folder_path, "kids_story1.mp4")

save_video(raw_video, output_path)




with open('img_path_maps.pickle', 'wb+') as handle:
    pickle.dump(img_path_maps, handle, protocol=pickle.HIGHEST_PROTOCOL)


with open('voice_over_path_maps.pickle', 'rb') as handle:
    voice_over_path_maps2 = pickle.load(handle)
"""



"""
Debug

with open('voice_over_path_maps.pickle', 'rb') as handle:
    voice_over_path_maps = pickle.load(handle)

with open('img_path_maps.pickle', 'rb') as handle:
    img_path_maps = pickle.load(handle)


raw_video = merge_voice_over_image(voice_over_path_maps, img_path_maps)

"""