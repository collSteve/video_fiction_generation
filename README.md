# Video Fiction Generation

An automation video factory for creating AI generated videos using various TTS, TTI and post-processing technology.

Sample Usage:

```python
from ai_script_video/motivation_vid/automation import *

au = SyncAutomationFactory.create_automation("test_story2", test_video_root_dir_path, test_raw_script_to_sd_prompt_path) 

raw_script = au.generate_script(script_sys_prompt, "")
sd_prompts = au.generate_sd_prompts(raw_script)
au.generate_sd_prompt_images(sd_prompts)

au.generate_voice_over(sd_prompts)
voice_over_path_maps = au.get_voice_over_path_maps_from_db()
sd_prompt_image_path_maps = au.get_sd_prompt_image_path_maps_from_db()
au.generate_raw_concate_video(sd_prompt_image_path_maps, voice_over_path_maps)
```

Sample output:
[![Watch the video](test_concat.mp4)]
