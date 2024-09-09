from ai_script_video.puzzle_video.code_automation.base_task import PuzzleBaseTask

from TTS.api import TTS
import torch


class VoiceOverTask(PuzzleBaseTask):
    def __init__(self, puzzle_automation_service):
        super().__init__(puzzle_automation_service)

        device = "cuda" if torch.cuda.is_available() else "cpu"

        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    def voice_over_dict(self, script_dict: dict[str, str], output_folder: str, speaker="Royston Min"):
        output_path_dict = {}
        for key, value in script_dict.items():
            output_path = f"{output_folder}/{key}.mp3"
            self.create_voice_over(value, output_path, speaker=speaker)
            output_path_dict[key] = output_path
        
        return output_path_dict

    def create_voice_over(self, text, output_path, speaker="Royston Min"):
        self.tts.tts_to_file(text=text, speaker=speaker, language="en", file_path=output_path)
        