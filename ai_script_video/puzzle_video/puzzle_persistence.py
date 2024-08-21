import json
import os

from enum import Enum
from typing import Any, Callable, List
from pydantic import BaseModel

from ai_script_video.puzzle_video.puzzle_generation import RawPuzzle
from ai_script_video.puzzle_video.puzzle_script_generation import PuzzleScriptObj

class ScriptGenerationStatus(str, Enum):
    Not_Generated = "Not Generated"
    Generating = "Generating"
    Generated = "Generated"
    Generation_Failed = "Generation Failed"

class VideoGenerationStatus(str, Enum):
    Not_Generated = "Not Generated"
    Generating = "Generating"
    Generated = "Generated"
    Generation_Failed = "Generation Failed"

class VideoContentGenerationStatus(str, Enum):
    Not_Generated = "Not Generated"
    Generating = "Generating"
    Generated = "Generated"
    Generation_Failed = "Generation Failed"

class ProcessStatus(str, Enum):
    Not_Started = "Not Started"
    In_Progress = "In Progress"
    Completed = "Completed"
    Failed = "Failed"

class VideoContent(BaseModel):
    video_header: str
    engaging_text: str
    video_title: str
    video_description: str
    self_comment: str

class PuzzleDBItem(BaseModel):
    puzzle_type: str
    puzzle_title: str
    puzzle_question: str
    puzzle_answer: str
    script: PuzzleScriptObj = None
    video_content: List[VideoContent] = None
    video_content_generation_status: VideoContentGenerationStatus = VideoContentGenerationStatus.Not_Generated
    script_generation_status: ScriptGenerationStatus = ScriptGenerationStatus.Not_Generated
    video_generation_status: VideoGenerationStatus = VideoGenerationStatus.Not_Generated

    process_status: ProcessStatus = ProcessStatus.Not_Started


def save_puzzles(puzzles: List[RawPuzzle], filename):
    with open(filename, "w+") as f:
        # add to json obj stored in file
        f.seek(0)

        data: List[PuzzleDBItem] = []
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        
        for puzzle in puzzles:
            puzzleItem = PuzzleDBItem(**puzzle)
            data.append(puzzleItem)

        f.seek(0)
        json.dump(data, f, indent=4)
        
class QueryObj(BaseModel):
    attribute: str
    is_valid: Callable[[Any], bool]

def query_puzzle_item(filename, query: List[QueryObj]) -> List[PuzzleDBItem]:
    # check validity of query objects
    for queryObj in query:
        if queryObj.attribute not in PuzzleDBItem.model_fields.keys():
            raise Exception(f"Invalid query object: attribut {queryObj.attribute} is not valid")

    # load all db
    with open(filename, "r") as f:
        data: List[PuzzleDBItem] = json.load(f)
    
    valid_items: List[PuzzleDBItem] = []
    for puzzle_item in data:
        puzzle_item_dict = puzzle_item.model_dump()

        item_is_valid = True
        for queryObj in query:
            if not queryObj.is_valid(puzzle_item_dict[queryObj.attribute]):
                item_is_valid = False
                break
        
        if item_is_valid:
            valid_items.append(puzzle_item)
    
    return valid_items
    
def get_past_puzzle_questions(filename):
    # load all db
    with open(filename, "r") as f:
        data: List[PuzzleDBItem] = json.load(f)

    return [puzzle_item.puzzle_question for puzzle_item in data]


def get_puzzle(filename, puzzle_id):
        queryObj = QueryObj(attribute="puzzle_id", is_valid=lambda x: x == puzzle_id)
        puzzle_item = query_puzzle_item(filename, [queryObj])[0]

        if puzzle_item is None:
            raise Exception("Puzzle not found with id: " + puzzle_id)

        return puzzle_item