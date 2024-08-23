from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import Any, List, Self, Set

from utils.queue import Queue
import warnings

from automation.automation_node import AutomationNode, TaskLink, TaskInput, TaskOutput, TaskStatus, VariableStatus
from automation.nodes.terminus_node import TerminusNode


class AutomationStatus(str, Enum):
    Not_Started = "Not Started"
    In_Progress = "In Progress"
    Completed = "Completed"
    Failed = "Failed"

class AutomationGraph:

    def __init__(self):
        self.nodes: List[AutomationNode] = []
        self.links: List[TaskLink] = []

        self._start_node: TerminusNode = None
        self._end_node: TerminusNode = None

        self.status: AutomationStatus = AutomationStatus.Not_Started

    def _run(self):
        node_queue: Queue[AutomationNode] = Queue()
        node_queue.put(self._start_node)

        while not node_queue.empty() and not self.are_outputs_computed():

            current_node = node_queue.get()

            print(f"Executing node {current_node.id}")

            if current_node.status == TaskStatus.Completed:
                raise Exception(f"[weird behaviour]: Node {current_node.id} is already completed but not scheduled, and it is being executed")
                
            if current_node.status == TaskStatus.Not_Started:
                current_node.schedule()

            if current_node.status != TaskStatus.Scheduled:
                warnings.warn(f"[weird behaviour]: Node {current_node.id} is not scheduled with status {current_node.status}")

            if not current_node.can_start():
                node_queue.put(current_node)
                continue

            current_node.execute()
            for output_item in current_node.outputs.values():
                for link in output_item.links:
                    if link is not None:
                        # set input of target node
                        target_node = self.get_node_by_id(link.target_node_id)
                        target_node.set_input_value(link.target_node_input_name, output_item.value)

                        # if target node is not in queue, add it and schedule it
                        if all([x.id != target_node.id for x in node_queue.skim_content]):
                            node_queue.put(target_node)
                            target_node.schedule()

    def execute(self):
        if not self.is_valid():
            raise ValueError("Graph is not valid")
        
        if self.status == AutomationStatus.In_Progress:
            raise ValueError("Graph is already in progress")
        
        if self.status == AutomationStatus.Completed:
            raise ValueError("Graph is already completed")
        
        self.status = AutomationStatus.In_Progress
        try:
            self._run()
        except Exception as e:
            self.status = AutomationStatus.Failed
            raise e
        
        self.status = AutomationStatus.Completed

    def is_valid(self)->bool:
        return True # TODO: Implement

    def are_outputs_computed(self)->bool:
        for output in self._end_node.outputs.values():
            if output.status == VariableStatus.Not_Set:
                return False
        return True
    
    def add_node(self, node:AutomationNode):
        self.nodes.append(node)

    def set_input_value(self, input_name:str, value:Any):
        if input_name not in self._start_node.inputs:
            raise ValueError(f"Input key {input_name} not found in graph inputs")
        
        if self._start_node.inputs[input_name].validator is not None:
            if not self._start_node.inputs[input_name].validator(value):
                raise ValueError(f"Input value {value} is not valid for input {input_name}")
        
        self._start_node.set_input_value(input_name, value)

    @staticmethod
    def build_from_json()->Self:
        pass

    def get_node_by_id(self, id:str)->AutomationNode:
        for node in self.nodes:
            if node.id == id:
                return node
        raise ValueError(f"Node with id {id} not found in graph")
    
    def set_start_node(self, id:str):
        self._start_node = self.get_node_by_id(id)

    def set_end_node(self, id:str):
        self._end_node = self.get_node_by_id(id)

    def add_link(self, source_node_id:str, source_node_output_name:str, target_node_id:str, target_node_input_name:str):
        source_node = self.get_node_by_id(source_node_id)
        target_node = self.get_node_by_id(target_node_id)

        source_output = source_node.outputs[source_node_output_name]
        target_input = target_node.inputs[target_node_input_name]

        if source_output is None:
            raise ValueError(f"Output {source_node_output_name} not found in node {source_node_id}")

        if target_input is None:
            raise ValueError(f"Input {target_node_input_name} not found in node {target_node_id}")

        # make sure variable have the same type
        if source_output.type != target_input.type:
            raise ValueError(f"Output type {source_output.type} does not match input type {target_input.type}")

        link = TaskLink(source_node_id=source_node_id, 
                        source_node_output_name=source_node_output_name, 
                        target_node_id=target_node_id, 
                        target_node_input_name=target_node_input_name,
                        variable_type=source_output.type
                        )
        
        source_node.link_output(link)
        target_node.link_input(link)
        
        # source_node.outputs[source_node_output_name].links.append(link)
        # target_node.inputs[target_node_input_name].link = link

        self.links.append(link)

    @property
    def inputs(self)->dict[str, TaskInput]:
        return deepcopy(self._start_node.inputs)
    
    @property
    def outputs(self)->dict[str, TaskOutput]:
        return deepcopy(self._end_node.outputs)
    




    