import os
from typing import List, ClassVar
from pydantic import BaseModel
import random
from moviepy.editor import *

from ai_script_video.puzzle_video.code_automation.puzzle_generation_task import PuzzleGenerationTask
from ai_script_video.puzzle_video.code_automation.script_gen_task import VoiceOverTask
from ai_script_video.puzzle_video.code_automation.unrpocessed_puzzle_fetcher import Unprocessed_Puzzle_Fetcher
from ai_script_video.puzzle_video.puzzle_persistence import PuzzleDBItem, PuzzleDBManager, PuzzleItemStatus
from ai_script_video.puzzle_video.puzzle_script_generation import generate_script


class PuzzleCreationSystemInfo(BaseModel):
    puzzle_db_path: str
    puzzle_creation_system_prompt_path: str
    script_system_prompt_path: str
    script_db_path: str
    video_fragment_folder: str
    voice_over_folder: str
    background_picture_folder: str

class PuzzleAutomationService:
    def __init__(self, puzzle_creation_system_info: PuzzleCreationSystemInfo, puzzle_db_manager: PuzzleDBManager):
        self._puzzle_creation_system_info = puzzle_creation_system_info
        self._puzzle_db_manager = puzzle_db_manager

    @property
    def puzzle_creation_system_info(self):
        return self._puzzle_creation_system_info
    
    @ property
    def puzzle_db_manager(self):
        return self._puzzle_db_manager

class CodeAutomationPuzzle:
    def __init__(self, puzzle_automation_service: PuzzleAutomationService):
        self.puzzle_automation_service = puzzle_automation_service

        self.voice_over_task = VoiceOverTask(puzzle_automation_service)
        

    def _run(self):
        unprocessed_puzzles_task = Unprocessed_Puzzle_Fetcher(self.puzzle_automation_service)

        unprocessed_puzzles: List[PuzzleDBItem] = unprocessed_puzzles_task.execute()

        puzzle_generation_task = PuzzleGenerationTask(self.puzzle_automation_service)

        while len(unprocessed_puzzles) <= 0:
            # generate new puzzles and save
            generated_puzzles: List[PuzzleDBItem] = puzzle_generation_task.execute()

            #save to db
            self.puzzle_automation_service.puzzle_db_manager.save_puzzles(generated_puzzles)

            # get unprocessed puzzles
            unprocessed_puzzles = unprocessed_puzzles_task.execute()
        
        # chose a puzzle
        puzzle = unprocessed_puzzles[0]
        if puzzle is None:
            raise Exception("No puzzle to process")
        
        print(f"Got puzzle: {puzzle}")
        # mark puzzle in db
        self.puzzle_automation_service.puzzle_db_manager.update_puzzle_status(puzzle, PuzzleItemStatus.InProcess)

        # generate scipts
        generated_script = generate_script(puzzle.model_dump(), system_prompt_path=self.puzzle_automation_service.puzzle_creation_system_info.script_system_prompt_path)

        print("Script gen finshed")

        # create voice over and video for segments of the script
        voice_over_path_dict = self.voice_over_task.voice_over_dict(generated_script.model_dump(), self.puzzle_automation_service.puzzle_creation_system_info.voice_over_folder)

        print("voice over gen finshed")

        # create video segments
        # choose a background picture
        files = os.listdir(self.puzzle_automation_service.puzzle_creation_system_info.background_picture_folder)
        
        # filter out non image files
        files = [file for file in files if file.endswith(".png") or file.endswith(".jpg")]

        if len(files) <= 0:
            raise Exception("No background picture found")
        
        # choose a background picture (randomly)
        background_picture_path = os.path.join(self.puzzle_automation_service.puzzle_creation_system_info.background_picture_folder, 
                                               random.choice(files))
        
        video_voiceover_path_dict = {}
        # create video fragments by combining voice over and background pictures
        for key, value in voice_over_path_dict.items():
            voice_over_clip = AudioFileClip(value)
            background_picture_clip = ImageClip(background_picture_path).set_duration(voice_over_clip.duration)
            background_picture_clip = background_picture_clip.set_audio(voice_over_clip)

            output_path = os.path.join(self.puzzle_automation_service.puzzle_creation_system_info.video_fragment_folder, f"{key}.mp4")
            background_picture_clip.write_videofile(output_path, codec="libx264", fps=24)
            video_voiceover_path_dict[key] = output_path
        
            

# test out
test_system_info: PuzzleCreationSystemInfo = PuzzleCreationSystemInfo(puzzle_db_path="D:\\Projects\\video_fiction_generation\\ai_script_video\\puzzle_video\\puzzle_db.json",
                                                                      puzzle_creation_system_prompt_path="D:\\Projects\\video_fiction_generation\\ai_script_video\\puzzle_video\\puzzle_generation_prompt",
                                                                      script_system_prompt_path="D:\\Projects\\video_fiction_generation\\ai_script_video\\puzzle_video\\script_generation_prompt",
                                                                      script_db_path="",
                                                                      video_fragment_folder="D:\\Projects\\video_fiction_generation\\ai_script_video\\puzzle_video\\video_frags",
                                                                      voice_over_folder="D:\\Projects\\video_fiction_generation\\ai_script_video\\puzzle_video\\voice_overs",
                                                                      background_picture_folder="D:\\Projects\\video_fiction_generation\\ai_script_video\\puzzle_video\\assets\\card_background")

test_puzzle_db_manager = PuzzleDBManager(test_system_info.puzzle_db_path)

test_puzzle_service = PuzzleAutomationService(puzzle_creation_system_info=test_system_info, puzzle_db_manager=test_puzzle_db_manager)

test_puzzle_service.puzzle_db_manager
print("Get owrk")

test_automation = CodeAutomationPuzzle(test_puzzle_service)

test_automation._run()






