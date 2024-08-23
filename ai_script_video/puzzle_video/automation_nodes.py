from enum import Enum
import json
from typing import Any, Callable, List, Self
from openai import BaseModel
from ai_script_video.puzzle_video.automation_nodes.script_generation import ScriptGenerationTask
from ai_script_video.puzzle_video.puzzle_generation import generate_puzzles
from ai_script_video.puzzle_video.puzzle_persistence import ProcessStatus, QueryObj, get_puzzle, query_puzzle_item, ScriptGenerationStatus, save_puzzles
from ai_script_video.puzzle_video.puzzle_script_generation import generate_script
from automation.automation_node import AutomationNode, TaskStatus, TaskInput


puzzle_db_path = "puzzle.db.json"

script_system_prompt_path = "script_creation_prompt"








class VideoContentGenerationTask(AutomationNode):
    pass

class VoiceOverGenerationTask(AutomationNode):
    pass

class VideoVisualGenerationTask(AutomationNode):
    pass

class VideoSegmentGenerationTask(AutomationNode):
    pass

class VideoSegmentMergeTask(AutomationNode):
    pass

class PostProcessingTask(AutomationNode):
    pass

AutomationRoadMap = {
    "tasks":{
        "script_generation": {
            "next_tasks": ["video_content_generation"],
            "task_class": ScriptGenerationTask
        },
        "video_content_generation": {
            "next_tasks": ["voice_over_generation", "video_visual_generation"],
        },
        "voice_over_generation": {
            "next_tasks": ["video_segment_generation"],
        },
        "video_visual_generation": {
            "next_tasks": ["video_segment_generation"],
        },
        "video_segment_generation": {
            "next_tasks": ["video_segment_merge"],
        },
        "video_segment_merge": {
            "next_tasks": ["post_processing"],
        },
        "post_processing": {
            "next_tasks": [],
        }
    },
    "start_task": "script_generation",
    "end_task": "post_processing"
}

    

class AutomationJob(BaseModel):
    tasks: List[AutomationNode]
    current_tasks: List[AutomationNode]

    def __init__(self):
        self.tasks = []
        self.current_tasks = []
        self.status = TaskStatus.Not_Started

    def add_task(self, task: AutomationNode):
        self.tasks.append(task)

    def start(self):
        self.status = TaskStatus.In_Progress
        self.current_task = self.tasks[0]

    def next_task(self):
        if self.current_task is None:
            raise Exception("No task started")
        if self.current_task._status == TaskStatus.Completed:
            if self.tasks.index(self.current_task) + 1 < len(self.tasks):
                self.current_task = self.tasks[self.tasks.index(self.current_task) + 1]
            else:
                self.status = TaskStatus.Completed
        else:
            raise Exception("Current task is not completed")

    def get_current_task(self):
        return self.current_task

    def get_status(self):
        return self.status

    def set_status(self, status: TaskStatus):
        self.status = status

    def set_current_task_status(self, status: TaskStatus):
        self.current_task._status = status

    def get_all_tasks(self):
        return self.tasks


def get_all_puzzles_script_not_generated():
    queryObj = QueryObj(attribute="script_generation_status", is_valid=lambda x: x is ScriptGenerationStatus.Not_Generated)
    return query_puzzle_item(puzzle_db_path, [queryObj])
