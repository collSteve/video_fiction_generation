from enum import Enum
from typing import Any, Callable, List, Self
from pydantic import BaseModel

import warnings
import copy

from automation.automation_graph import AutomationGraph


class TaskStatus(str, Enum):
    Not_Started = "Not Started"
    In_Progress = "In Progress"
    Completed = "Completed"
    Failed = "Failed"

class VariableStatus(str, Enum):
    Not_Set = "Not Set"
    Set = "Set"

class TaskLink(BaseModel):
    origin_task_id: str
    target_task_id: str
    origin_node_output_name: str
    target_node_input_name: str
    variable_type: str

class TaskVariable(BaseModel):
    type: str
    value: Any = None
    name: str
    link: TaskLink | None = None # if none it is not set up yet
    validator: Callable[[Any],bool] | None = None
    status: VariableStatus = VariableStatus.Not_Set

class TaskOutput(BaseModel):
    type: str
    value: Any = None
    name: str
    links: List[TaskLink] = [] # if none it is not set up yet
    validator: Callable[[Any],bool] | None = None
    status: VariableStatus = VariableStatus.Not_Set

# items in road map
class AutomationNode():
    # next_tasks: List[Self] = []
    # previous_tasks: List[Self] = []
    _status: TaskStatus

    _inputs: dict[str, TaskVariable] = []
    _outputs: dict[str, TaskOutput] = []

    _global_graph: AutomationGraph

    def __init__(self, global_graph, id):
        self._status = TaskStatus.Not_Started
        self._global_graph = global_graph

        self._id = id

    def can_start(self):
        if len(self.previous_nodes) == 0:
            return True
        return self.validate_inputs()
    
    def validate_inputs(self):
        for input_item in self._inputs.values():
            if input_item.status == VariableStatus.Not_Set:
                return False
            if input_item.validator is not None:
                if not input_item.validator(input_item.value):
                    return False
        return True
    
    def set_input_value(self, input_name:str, value:Any):
        if input_name not in self._inputs:
            raise ValueError(f"Input key {input_name} not found in graph inputs")
        
        if self._inputs[input_name].validator is not None:
            if not self._inputs[input_name].validator(value):
                raise ValueError(f"Input value {value} is not valid for input {input_name}")
        
        self._inputs[input_name].value = value
        self._inputs[input_name].status = VariableStatus.Set

    def get_output_value(self, output_name:str):
        if output_name not in self._outputs:
            raise ValueError(f"Output key {output_name} not found in graph outputs")
        
        return self._outputs[output_name].value
    
    def add_input(self, input_name:str, input_type:str, validator:Callable[[Any],bool]=None):
        if input_name in self._inputs:
            raise ValueError(f"Input {input_name} already exists")
        
        self._inputs[input_name] = TaskVariable(name=input_name, value=None, type=input_type, validator=validator)

    def add_output(self, output_name:str, output_type:str, validator:Callable[[Any],bool]=None):
        if output_name in self._outputs:
            raise ValueError(f"Output {output_name} already exists")
        
        self._outputs[output_name] = TaskVariable(name=output_name, value=None, type=output_type, validator=validator)
    
    def remove_input(self, input_name:str):
        if input_name not in self._inputs:
            raise ValueError(f"Input {input_name} does not exist")
        
        del self._inputs[input_name]
    
    def remove_output(self, output_name:str):
        if output_name not in self._outputs:
            raise ValueError(f"Output {output_name} does not exist")
        
        del self._outputs[output_name]

    # to be implemented by child classes
    def _run(self):
        pass

    def execute(self):
        if not self.can_start():
            raise Exception("Cannot start task")
        
        if self._status == TaskStatus.In_Progress:
            warnings.warn("Task already in progress (for some reason it's being run again)")
            return
        
        if self._status == TaskStatus.Completed:
            warnings.warn("Task already completed (for some reason it's being run again)")
            return
        
        self._status = TaskStatus.In_Progress

        try:
            self._run()
        except Exception as e:
            self._status = TaskStatus.Failed
        
        self._status = TaskStatus.Completed


    @property
    def previous_nodes(self)->List[Self]:
        if self._global_graph is None:
            return []
        
        nodes = []
        for input_item in self._inputs.values():
            nodes.append(self._global_graph.get_node_by_id(input_item.link.origin_task_id))
        
        return nodes
    
    @property
    def next_nodes(self)->List[Self]:
        if self._global_graph is None:
            return []
        
        nodes = []
        for output_item in self._outputs.values():
            for link in output_item.links:
                nodes.append(self._global_graph.get_node_by_id(link.target_task_id))
        
        return nodes
    
    @property
    def status(self):
        return self._status
    
    @property
    def id(self):
        return self._id
    
    @property
    def inputs(self):
        return copy.deepcopy(self._inputs)
    
    @property
    def outputs(self):
        return copy.deepcopy(self._outputs)