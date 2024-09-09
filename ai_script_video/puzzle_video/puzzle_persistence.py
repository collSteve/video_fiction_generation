import json
import os.path
import uuid

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

class PuzzleItemStatus(str, Enum):
    Used = "Used"
    Unused = "Unused"
    InProcess = "In Process"

class VideoContent(BaseModel):
    video_header: str
    engaging_text: str
    video_title: str
    video_description: str
    self_comment: str

class PuzzleDBItem(BaseModel):
    id: str
    puzzle_type: str
    puzzle_title: str
    puzzle_question: str
    puzzle_answer: str
    status: PuzzleItemStatus = PuzzleItemStatus.Unused
    # script: PuzzleScriptObj = None
    # video_content: List[VideoContent] = None
    # video_content_generation_status: VideoContentGenerationStatus = VideoContentGenerationStatus.Not_Generated
    # script_generation_status: ScriptGenerationStatus = ScriptGenerationStatus.Not_Generated
    # video_generation_status: VideoGenerationStatus = VideoGenerationStatus.Not_Generated

    process_status: ProcessStatus = ProcessStatus.Not_Started

class RawPuzzleItem(BaseModel):
    puzzle_type: str
    puzzle_title: str
    puzzle_question: str
    puzzle_answer: str

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
            id = uuid.uuid4()
            puzzleItem = PuzzleDBItem(**puzzle, id=id)
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

    # check if file exists
    if not os.path.isfile(filename):
        json.dump([], open(filename, "w+"))
    
    # load all db
    with open(filename, "r") as f:
        try:
            dict_data: dict[str, Any] = json.load(f)

        except json.JSONDecodeError:
            raise Exception("Error when loading json file")
    
    
    valid_items: List[PuzzleDBItem] = []
    for dict_item in dict_data:

        item_is_valid = True
        for queryObj in query:
            if not queryObj.is_valid(dict_item[queryObj.attribute]):
                item_is_valid = False
                break
        
        if item_is_valid:
            valid_items.append(PuzzleDBItem(**dict_item))
    
    return valid_items
    
def get_past_puzzle_questions(filename):
    # load all db
    with open(filename, "r") as f:
        data: List[PuzzleDBItem] = json.load(f)

    return [puzzle_item.puzzle_question for puzzle_item in data]


def get_puzzle(filename, puzzle_id):
        queryObj = QueryObj(attribute="id", is_valid=lambda x: x == puzzle_id)
        puzzle_item = query_puzzle_item(filename, [queryObj])[0]

        if puzzle_item is None:
            raise Exception("Puzzle not found with id: " + puzzle_id)

        return puzzle_item


class PuzzleDBManager():
    def __init__(self, json_db_path):
        self.db_path = json_db_path

    def save_puzzles(self, puzzles: List[RawPuzzle]):
        return save_puzzles(puzzles, self.db_path)
        
    def query_puzzle_item(self, query: List[QueryObj]) -> List[PuzzleDBItem]:
        return query_puzzle_item(self.db_path, query)
    
    def get_puzzle(self, puzzle_id):
        return get_puzzle(self.db_path, puzzle_id)
    
    def remove_puzzle(self, puzzle_id):
        # check if file exists
        if not os.path.isfile(self.db_path):
            json.dump([], open(self.db_path, "w+"))
        
        # load all db
        with open(self.db_path, "r") as f:
            try:
                dict_data: dict[str, Any] = json.load(f)

            except json.JSONDecodeError:
                raise Exception("Error when loading json file")
            
        # remove puzzle
        dict_data = [item for item in dict_data if item["id"] != puzzle_id]

        # save to db
        with open(self.db_path, "w") as f:
            json.dump(dict_data, f, indent=4)
    
    def update_puzzle_status(self, puzzle_id:str, status: PuzzleItemStatus):
        # check if file exists
        if not os.path.isfile(self.db_path):
            json.dump([], open(self.db_path, "w+"))
        
        # load all db
        with open(self.db_path, "r") as f:
            try:
                dict_data: dict[str, Any] = json.load(f)

            except json.JSONDecodeError:
                raise Exception("Error when loading json file")
            
        # update puzzle status
        for item in dict_data:
            if item["id"] == puzzle_id:
                item["status"] = status
        
        # save to db
        with open(self.db_path, "w") as f:
            json.dump(dict_data, f, indent=4)
