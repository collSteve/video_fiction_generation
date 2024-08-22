from enum import Enum
from typing import Any, Callable, List, Self
from pydantic import BaseModel


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
class AutomationNode():
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

class AutomationIFNode(AutomationNode):
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
