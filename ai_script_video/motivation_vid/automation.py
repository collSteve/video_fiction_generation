
# raw_script_to_sd_prompt_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\raw_script_to_sd_prompt"

# sd_image_gen_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\image_gen_dir"
# voice_over_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\voice_over_dir"

# raw_concate_video_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\raw_concate_dir"

# ideogram_model = "V_2_TURBO"

import enum
import os
from ai_script_video.motivation_vid.sync_automation_module import ScriptItem, generate_image_from_prompt, generate_image_from_prompt_int, generate_raw_script, generate_sd_prompts, generate_voice_over_int
from tinydb import TinyDB, Query

class FileTypes(enum, str):
    Script = "Script"
    Script_Disected = "Script_Disected"
    SD_Prompts = "SD_Prompts"
    SD_Prompt_Images = "SD_Prompt_Images"
    Voice_Over = "Voice_Over"
    Raw_Concate_Video = "Raw_Concate_Video"


class Automation:
    def __init__(self, 
                 raw_script_to_sd_prompt_path, 
                 sd_image_gen_folder_path, 
                 voice_over_folder_path, 
                 raw_concate_video_folder_path, 
                 script_folder_path,
                 ideogram_model):
        self.raw_script_to_sd_prompt_path = raw_script_to_sd_prompt_path
        self.sd_image_gen_folder_path = sd_image_gen_folder_path
        self.voice_over_folder_path = voice_over_folder_path
        self.raw_concate_video_folder_path = raw_concate_video_folder_path
        self.script_folder_path = script_folder_path

        self.ideogram_model = ideogram_model

        # init necessary dbs
        self.file_db = TinyDB("file_db.json")

        self.project_name = project_name




    def generate_script(self, system_prompt, prompt):
        script = generate_raw_script(system_prompt, prompt)

        output_path = os.path.join(self.script_folder_path, "script.txt")
        with open(output_path, "w+") as f:
            f.write(script)
        
        self.file_db.insert({"type": FileTypes.Script, "path": output_path})

        return script
    
    def generate_sd_prompts(self, raw_script):
        sd_prompts = generate_sd_prompts(raw_script, self.raw_script_to_sd_prompt_path)

        output_path = os.path.join(self.script_folder_path, "sd_prompts.json")
        with open(output_path, "w+") as f:
            f.write(sd_prompts.json())
        
        self.file_db.insert({"type": FileTypes.SD_Prompts, "path": output_path})

        return sd_prompts
    
    def generate_sd_prompt_images(self, sd_prompts):
        def on_image_generated(sec_num, image_path):
            self.file_db.insert({"type": FileTypes.SD_Prompt_Images, "section_number": sec_num, "path": image_path})


        generate_image_from_prompt_int(sd_prompts, self.project_name, self.sd_image_gen_folder_path, 
                                        self.ideogram_model,
                                        on_image_generated=on_image_generated)
        return 
    
    def generate_voice_over(self, script_items: list[ScriptItem]):
        def on_voice_over_generated(sec_num, voice_over_path):
            self.file_db.insert({"type": FileTypes.Voice_Over, "section_number": sec_num, "path": voice_over_path})

        generate_voice_over_int(script_items, self.project_name, 
                                self.voice_over_folder_path, 
                                on_voice_over_generated=on_voice_over_generated)
        return
    
        
