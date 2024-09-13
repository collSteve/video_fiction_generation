from ai_script_video.motivation_vid.async_automation_modules import generate_image_from_prompt
from ai_script_video.motivation_vid.automation import Automation, FileTypes

import asyncio

class AsyncAutomation(Automation):
    def generate_sd_prompt_images(self, sd_prompts):
        def on_image_generated(sec_num, image_path):
            self.file_db.insert({"type": FileTypes.SD_Prompt_Images, "section_number": sec_num, "path": image_path})

        tasks = generate_image_from_prompt(sd_prompts, self.project_name, self.sd_image_gen_folder_path, self.ideogram_model, on_image_generated)

        async def run_task():
            await asyncio.gather(*tasks)
        asyncio.run(run_task())

    def run(self, system_prompt, prompt):
        raw_script = self.generate_script(system_prompt, prompt)
        sd_prompts = self.generate_sd_prompts(raw_script)
        self.generate_sd_prompt_images(sd_prompts)

        self.generate_voice_over(sd_prompts)
        voice_over_path_maps = self.get_voice_over_path_maps_from_db()
        sd_prompt_image_path_maps = self.get_sd_prompt_image_path_maps_from_db()
        self.generate_raw_concate_video(sd_prompt_image_path_maps, voice_over_path_maps)