
# raw_script_to_sd_prompt_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\raw_script_to_sd_prompt"

# sd_image_gen_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\image_gen_dir"
# voice_over_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\voice_over_dir"

# raw_concate_video_folder_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\raw_concate_dir"

# ideogram_model = "V_2_TURBO"

from enum import Enum
import os
import pickle
from ai_script_video.motivation_vid.sync_automation_module import FilePathMap, ScriptItem, generate_image_from_prompt, generate_image_from_prompt_int, generate_raw_script, generate_sd_prompts, generate_voice_over_int, merge_voice_over_image, save_video
from tinydb import TinyDB, Query
import json

class FileTypes(str, Enum):
    Script = "Script"
    Script_Disected = "Script_Disected"
    SD_Prompts = "SD_Prompts"
    SD_Prompt_Images = "SD_Prompt_Images"
    Voice_Over = "Voice_Over"
    Raw_Concate_Video = "Raw_Concate_Video"


SD_PROMPTS_DISECT_FILENAME = "sd_prompts"
SCRIPT_FILENAME = "script"
FILE_DB_FILENAME = "file_db"


class Automation():
    def __init__(self, 
                 project_name,
                 raw_script_to_sd_prompt_path, 
                 sd_image_gen_folder_path, 
                 voice_over_folder_path, 
                 raw_concate_video_folder_path, 
                 script_folder_path,
                 ideogram_model,
                 file_db_path=f"{FILE_DB_FILENAME}.json"):
        self.raw_script_to_sd_prompt_path = raw_script_to_sd_prompt_path
        self.sd_image_gen_folder_path = sd_image_gen_folder_path
        self.voice_over_folder_path = voice_over_folder_path
        self.raw_concate_video_folder_path = raw_concate_video_folder_path
        self.script_folder_path = script_folder_path

        self.ideogram_model = ideogram_model

        # init necessary dbs
        self.file_db = TinyDB(file_db_path)

        self.project_name = project_name




    def generate_script(self, system_prompt, prompt):
        script = generate_raw_script(system_prompt, prompt)

        output_path = os.path.join(self.script_folder_path, f"{SCRIPT_FILENAME}.txt")
        with open(output_path, "w+") as f:
            f.write(script)
        
        self.file_db.insert({"type": FileTypes.Script, "path": output_path})

        return script
    
    def generate_sd_prompts(self, raw_script):
        sd_prompts = generate_sd_prompts(raw_script, self.raw_script_to_sd_prompt_path)

        # output_path = os.path.join(self.script_folder_path, f"{SD_PROMPTS_DISECT_FILENAME}.json")
        output_path = os.path.join(self.script_folder_path, f"{SD_PROMPTS_DISECT_FILENAME}.pickle")
        # with open(output_path, "w+") as f:
        #     json.dump(sd_prompts, f)

        with open(output_path, 'wb+') as handle:
            pickle.dump(sd_prompts, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
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

    def get_voice_over_path_maps_from_db(self):
        query_item = Query()
        db_items = self.file_db.search(query_item.type == FileTypes.Voice_Over)

        voice_over_path_maps = []
        for item in db_items:
            voice_over_path_maps.append(FilePathMap(section_number=item["section_number"], path=item["path"]))

        return voice_over_path_maps
    
    def get_sd_prompt_image_path_maps_from_db(self):
        query_item = Query()
        db_items = self.file_db.search(query_item.type == FileTypes.SD_Prompt_Images)

        sd_prompt_image_path_maps = []
        for item in db_items:
            sd_prompt_image_path_maps.append(FilePathMap(section_number=item["section_number"], path=item["path"]))

        return sd_prompt_image_path_maps

    def generate_raw_concate_video(self, sd_prompt_image_path_maps, voice_over_path_maps):
        output_path = os.path.join(self.raw_concate_video_folder_path, f"{self.project_name}.mp4")
        raw_video = merge_voice_over_image(unsorted_voice_over_path_maps=voice_over_path_maps, 
                                           unsorted_image_path_maps=sd_prompt_image_path_maps)
        
        save_video(raw_video, output_path)
        self.file_db.insert({"type": FileTypes.Raw_Concate_Video, "path": output_path})

    def run(self, system_prompt, prompt):
        raw_script = self.generate_script(system_prompt, prompt)
        sd_prompts = self.generate_sd_prompts(raw_script)
        self.generate_sd_prompt_images(sd_prompts)

        self.generate_voice_over(sd_prompts)
        voice_over_path_maps = self.get_voice_over_path_maps_from_db()
        sd_prompt_image_path_maps = self.get_sd_prompt_image_path_maps_from_db()
        self.generate_raw_concate_video(sd_prompt_image_path_maps, voice_over_path_maps)


class SyncAutomationFactory:
    @staticmethod
    def create_automation(project_name, video_root_dir_path, raw_script_to_sd_prompt_path, ideogram_model="V_2_TURBO", Automation_Class: type[Automation]=Automation):
        project_root_dir_path = os.path.join(video_root_dir_path, project_name)
        if (not os.path.exists(project_root_dir_path)):
            os.mkdir(project_root_dir_path)
        
        ingredients_dir_path = os.path.join(project_root_dir_path, "ingredients")
        if (not os.path.exists(ingredients_dir_path)):
            os.mkdir(ingredients_dir_path)

        file_db_path = os.path.join(project_root_dir_path, f"{FILE_DB_FILENAME}.json")


        return Automation_Class(project_name, 
                          raw_script_to_sd_prompt_path=raw_script_to_sd_prompt_path, 
                          sd_image_gen_folder_path=ingredients_dir_path, 
                          voice_over_folder_path=ingredients_dir_path, 
                          raw_concate_video_folder_path=project_root_dir_path, 
                          script_folder_path=project_root_dir_path, 
                          ideogram_model=ideogram_model,
                          file_db_path=file_db_path)
    
        
test_raw_script_to_sd_prompt_path = "D:\\Projects\\video_fiction_generation\\ai_script_video\\motivation_vid\\raw_script_to_sd_prompt"
test_video_root_dir_path = "D:\\Projects\\video_fiction_generation\\test"

script_sys_prompt = "You are a childern story writer. Expert in writing stories and award winning childern story writor. Write a childern bedtime story for kids 8 to 12 years old. Be fun and fairy tale. should tell a moral. and should be in duration between 5 to 8 minutes"

"""
au = SyncAutomationFactory.create_automation("test_story2", test_video_root_dir_path, test_raw_script_to_sd_prompt_path) 

raw_script = au.generate_script(script_sys_prompt, "")
sd_prompts = au.generate_sd_prompts(raw_script)
au.generate_sd_prompt_images(sd_prompts)

au.generate_voice_over(sd_prompts)
voice_over_path_maps = au.get_voice_over_path_maps_from_db()
sd_prompt_image_path_maps = au.get_sd_prompt_image_path_maps_from_db()
au.generate_raw_concate_video(sd_prompt_image_path_maps, voice_over_path_maps)

"""