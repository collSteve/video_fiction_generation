from enum import Enum
from typing import Any, Self, Set

from queue import Queue

from automation.automation_node import AutomationNode, TaskLink, TaskVariable
from automation.nodes.terminus_node import TerminusNode

class AutomationStatus(str, Enum):
    Not_Started = "Not Started"
    In_Progress = "In Progress"
    Completed = "Completed"
    Failed = "Failed"

class AutomationGraph:
    nodes: Set[AutomationNode] = set()
    links: Set[TaskLink] = set()

    start_node: TerminusNode = None
    end_node: TerminusNode = None

    status: AutomationStatus = AutomationStatus.Not_Started


    def __init__(self):
        self.nodes = set()
        self.links = set()

    def _run(self):
        node_queue: Queue[AutomationNode] = Queue()
        node_queue.put(self.start_node)

        while not node_queue.empty():
            current_node = node_queue.get()
            if current_node.status == AutomationStatus.Completed:
                continue

            if not current_node.can_start():
                node_queue.put(current_node)
                continue

            current_node.execute()
            for output_item in current_node.outputs.values():
                for link in output_item.links:
                    if link is not None:
                        # set input of target node
                        target_node = self.get_node_by_id(link.target_task_id)
                        target_node.set_input_value(link.target_node_input_name, output_item.value)

                        # add target node to queue
                        node_queue.put(target_node)

    def execute(self):
        if not self.is_valid():
            raise ValueError("Graph is not valid")
        
        if self.status == AutomationStatus.In_Progress:
            raise ValueError("Graph is already in progress")
        
        if self.status == AutomationStatus.Completed:
            raise ValueError("Graph is already completed")
        
        self.status = AutomationStatus.In_Progress
        try:
            self.run()
        except Exception as e:
            self.status = AutomationStatus.Failed
            raise e
        
        self.status = AutomationStatus.Completed

    def is_valid(self)->bool:
        return True # TODO: Implement
    
    def add_node(self, node:AutomationNode):
        self.nodes.add(node)

    def set_input_value(self, input_name:str, value:Any):
        if input_name not in self.start_node.inputs:
            raise ValueError(f"Input key {input_name} not found in graph inputs")
        
        if self.start_node.inputs[input_name].validator is not None:
            if not self.start_node.inputs[input_name].validator(value):
                raise ValueError(f"Input value {value} is not valid for input {input_name}")
        
        self.start_node.set_input_value(input_name, value)

    @staticmethod
    def build_from_json()->Self:
        pass

    def get_node_by_id(self, id:str)->AutomationNode:
        for node in self.nodes:
            if node.id == id:
                return node
        raise ValueError(f"Node with id {id} not found in graph")
    
    def set_start_node(self, id:str):
        self.start_node = self.get_node_by_id(id)

    def set_end_node(self, id:str):
        self.end_node = self.get_node_by_id(id)

    @property
    def inputs(self)->dict[str, TaskVariable]:
        return self.start_node.inputs
    




    