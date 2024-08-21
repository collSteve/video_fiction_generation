from enum import Enum
import json
from typing import Any, Callable, List, Self
from openai import BaseModel
from ai_script_video.puzzle_video.puzzle_generation import generate_puzzles
from ai_script_video.puzzle_video.puzzle_persistence import ProcessStatus, PuzzleDBItem, QueryObj, get_puzzle, query_puzzle_item, ScriptGenerationStatus, save_puzzles
from ai_script_video.puzzle_video.puzzle_script_generation import PuzzleScriptObj, generate_script


puzzle_db_path = "puzzle.db.json"

script_system_prompt_path = "script_creation_prompt"

# automation set up, set up a flowchart for the automation task
class TaskStatus(str, Enum):
    Not_Started = "Not Started"
    In_Progress = "In Progress"
    Completed = "Completed"
    Failed = "Failed"

class TaskLink(BaseModel):
    origin_task_id: str
    target_task_id: str
    variable_name: str
    variable_type: str

class IFTaskLink(BaseModel):
    origin_task_id: str
    yes_target_task_id: str
    no_target_task_id: str
    variable_name: str
    variable_type: str

class TaskVariable(BaseModel):
    type: str
    value: Any = None
    name: str
    link: TaskLink | IFTaskLink | None = None # if none it is not set up yet

# items in road map
class AutomationTask():
    # next_tasks: List[Self] = []
    # previous_tasks: List[Self] = []
    status: TaskStatus

    inputs: dict[str, TaskVariable] = []
    outputs: dict[str, TaskVariable] = []

    global_graph = None

    def __init__(self, global_graph, id):
        self.status = TaskStatus.Not_Started
        self.global_graph = global_graph

        self._id = id

    def can_start(self):
        if len(self.previous_nodes) == 0:
            return True
        for node in self.previous_nodes:
            if node.status != TaskStatus.Completed:
                return False
        return True
    
    def validate_inputs(self):
        # 
        return True # TODO
    
    def run(self):
        if not self.can_start():
            raise Exception("Cannot start task")
        
        if not self.validate_inputs():
            raise Exception("Invalid inputs")
        
        self.status = TaskStatus.In_Progress

    def execute(self):
        try:
            self.run()
        except Exception as e:
            self.status = TaskStatus.Failed
        
        self.status = TaskStatus.Completed


    @property
    def previous_nodes(self)->List[Self]:
        if self.global_graph is None:
            return []
        
        nodes = []
        for input_item in self.inputs.values():
            nodes.append(self.global_graph.get_node_by_id(input_item.link.origin_task_id))
        
        return nodes
    
    @property
    def next_nodes(self)->List[Self]:
        if self.global_graph is None:
            return []
        
        nodes = []
        for output_item in self.outputs.values():
            nodes.append(self.global_graph.get_node_by_id(output_item.link.target_task_id))
        
        return nodes

class IFNodeOutputInfo(BaseModel):
    yes_target_task_id: str
    no_target_task_id: str
    variable_name: str
    variable_type: str

class IFNodeInputInfo(BaseModel):
    origin_task_id: str
    variable_name: str
    variable_type: str

class AutomationIFNode(AutomationTask):
    validation: bool | None = None
    def __init__(self, global_graph, id, input_info: IFNodeInputInfo, output_info: IFNodeOutputInfo, validate: Callable[[Any],bool]):
        super().__init__(global_graph, id)

        assert(input_info.variable_type == output_info.variable_type)

        self.inputs[input_info.variable_name] = TaskVariable(name=input_info.variable_name, value=None, type=input_info.variable_type, 
                                                             link=TaskLink(
                                                                 origin_task_id=input_info.origin_task_id, 
                                                                 target_task_id= self._id,
                                                                 variable_name=input_info.variable_name,
                                                                 variable_type=input_info.variable_type))
        
        self.outputs[output_info.variable_name] = TaskVariable(name=output_info.variable_name, value=None, type=output_info.variable_type, 
                                                             link=IFTaskLink(
                                                                 origin_task_id=self._id, 
                                                                 yes_target_task_id=output_info.yes_target_task_id,
                                                                 no_target_task_id=output_info.no_target_task_id,
                                                                 variable_name=output_info.variable_name,
                                                                 variable_type=output_info.variable_type))
        
        self._validate = validate

        self._input_info = input_info
        self._output_info = output_info
        

    def run(self):
        super().run()

        self.outputs[self._output_info.variable_name].value = self.inputs[self._input_info.variable_name].value

        self.validation = self._validate(self.inputs[self._input_info.variable_name].value)


     


# class PuzzleAutomationTask(AutomationTask):
#     puzzle_id: str
#     puzzle_item: PuzzleDBItem

#     def __init__(self, puzzle_id):
#         super().__init__()
#         self.puzzle_id = puzzle_id
#         self.puzzle_item = get_puzzle(puzzle_db_path, puzzle_id)

class SaveJsonDBTask(AutomationTask):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self.inputs["json_obj_list"] = TaskVariable(type="json_list", value=None, name="json_obj_list", link=None)
        self.inputs["db_path"] = TaskVariable(type="path", value=None, name="db_path", link=None)

        # add outputs
        self.outputs["directing"] = TaskVariable(type="router", value=None, name="directing", link=None)

    def validate_inputs(self):
        return super().validate_inputs() and isinstance(self.inputs["json_obj_list"].value, list)
    
    def run(self):
        super().run()

        with open(self.inputs["db_path"].value, "w+") as f:
            # add to json obj stored in file
            f.seek(0)

            data = json.load(f)

            # validate data is List
            if not isinstance(data, list):
                self.status = TaskStatus.Failed
                return

            for json_obj in self.inputs["json_obj_list"].value:
                data.append(json_obj)
            
            f.seek(0)
            json.dump(data, f, indent=4)
        
        self.status = TaskStatus.Completed
     

class PuzzleGenerationTask(AutomationTask):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self.inputs["puzzle_db_path"] = TaskVariable(type="str", value=None, name="puzzle_db_path", link=None)
        self.inputs["puzzle_creation_system_prompt_path"] = TaskVariable(type="str", value=None, name="puzzle_creation_system_prompt_path", link=None)

        # add outputs
        self.outputs["generated_puzzles"] = TaskVariable(type="List[RawPuzzle]", value=None, name="generated_puzzles", link=None)
    
    def run(self):
        super().run()

        past_puzzle_questions = self.get_past_puzzle_questions()

        generated_puzzles = generate_puzzles(past_puzzle_questions, system_prompt_path=self.inputs["puzzle_creation_system_prompt_path"])

        if generated_puzzles is None:
            raise Exception("Generated puzzles are None (probably gpt error)")
        
        self.outputs["generated_puzzles"] = generated_puzzles
        self.status = TaskStatus.Completed

    def get_past_puzzle_questions(self):
        queryObj = QueryObj(attribute="puzzle_question", is_valid=lambda x: x is not None)
        puzzle_items = query_puzzle_item(self.inputs["puzzle_db_path"], [queryObj])

        return [item.puzzle_question for item in puzzle_items]

class UnprocessedPuzzleFetcher(AutomationTask):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self.inputs["puzzle_db_path"] = TaskVariable(type="str", value=None, name="puzzle_db_path", link=None)

        # add outputs
        self.outputs["unprocessed_puzzles"] = TaskVariable(type="List[RawPuzzle]", value=None, name="unprocessed_puzzles", link=None)
    
    def run(self):
        super().run()

        queryObj = QueryObj(attribute="process_status", is_valid=lambda x: x is ProcessStatus.Not_Started)
        puzzle_items = query_puzzle_item(self.inputs["puzzle_db_path"], [queryObj])

        self.outputs["unprocessed_puzzles"] = puzzle_items
        self.status = TaskStatus.Completed



class ScriptGenerationTask(AutomationTask):

    def __init__(self):
        super().__init__()

        # add inputs
        self.inputs["puzzle_item"] = TaskVariable(type="PuzzleDBItem", value=None, name="puzzle_item", link=None)
        self.inputs["script_system_prompt_path"] = TaskVariable(type="str", value=None, name="script_system_prompt_path", link=None)

        # add outputs
        self.outputs["generated_script"] = TaskVariable(type="PuzzleScriptObj", value=None, name="generated_script", link=None)
    
    def run(self):
        super().run()

        generated_script = generate_script(self.inputs["puzzle_item"], system_prompt_path=self.inputs["script_system_prompt_path"])


        if generated_script is None:
            raise Exception("Generated script is None (probably gpt error)")
        
        self.outputs["generated_script"] = generated_script
        self.status = TaskStatus.Completed

class VideoContentGenerationTask(AutomationTask):
    pass

class VoiceOverGenerationTask(AutomationTask):
    pass

class VideoVisualGenerationTask(AutomationTask):
    pass

class VideoSegmentGenerationTask(AutomationTask):
    pass

class VideoSegmentMergeTask(AutomationTask):
    pass

class PostProcessingTask(AutomationTask):
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
    tasks: List[AutomationTask]
    current_tasks: List[AutomationTask]


    def __init__(self):
        self.tasks = []
        self.current_tasks = []
        self.status = TaskStatus.Not_Started

    def add_task(self, task: AutomationTask):
        self.tasks.append(task)

    def start(self):
        self.status = TaskStatus.In_Progress
        self.current_task = self.tasks[0]

    def next_task(self):
        if self.current_task is None:
            raise Exception("No task started")
        if self.current_task.status == TaskStatus.Completed:
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
        self.current_task.status = status

    def get_all_tasks(self):
        return self.tasks




def get_all_puzzles_script_not_generated():
    queryObj = QueryObj(attribute="script_generation_status", is_valid=lambda x: x is ScriptGenerationStatus.Not_Generated)
    return query_puzzle_item(puzzle_db_path, [queryObj])
