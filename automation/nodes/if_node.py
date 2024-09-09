from typing import Any, Callable
from pydantic import BaseModel

from automation.automation_node import AutomationNode, TaskInput, TaskLink, TaskOutput


class AutomationIFNode(AutomationNode):
    

    def __init__(self, global_graph, id, execute_logic: Callable[[Any],bool]):
        super().__init__(global_graph, id)

        self._yes_link: TaskLink | None = None
        self._no_link: TaskLink | None = None

        self._execute_logic = execute_logic

        self._logic_return: bool | None = None


    def configure_input_output(self, input_name: str, output_name: str, variable_type: str, validator: Callable[[Any], bool] = None):
        if len(self._inputs) > 0 or len(self._outputs) > 0:
            raise ValueError("IF Node can only have one input and one output")
        super().add_input(input_name, variable_type, validator)
        super().add_output(output_name, variable_type, validator) # if_node will output same value as input


    def add_input(self, input_name: str, input_type: str, validator: Callable[[Any], bool] = None):
        raise ValueError("Not allowed to add input to IF Node, use configure_input_output instead")


    def add_output(self, output_name: str, output_type: str, validator: Callable[[Any], bool] = None):
        raise ValueError("Not allowed to add input to IF Node, use configure_input_output instead")


    def set_yes_link(self, target_node_id: str, target_node_input_name: str, variable_type: str):
        assert len(self._outputs) == 1, f"IF Node can only have one output, but found {len(self._outputs)}"
        
        self._yes_link = TaskLink(source_node_id=self.id, 
                                  source_node_output_name=self.output_name, 
                                  target_node_id=target_node_id, 
                                  target_node_input_name=target_node_input_name,
                                  variable_type=variable_type)

    def set_no_link(self, target_node_id: str, target_node_input_name: str, variable_type: str):
        assert len(self._outputs) == 1, f"IF Node can only have one output, but found {len(self._outputs)}"

        self._no_link = TaskLink(source_node_id=self.id, 
                                  source_node_output_name=self.output_name, 
                                  target_node_id=target_node_id, 
                                  target_node_input_name=target_node_input_name,
                                  variable_type=variable_type)

    def _run(self):

        assert len(self._inputs) == 1, f"IF Node can only have one input, but found {len(self._inputs)}"
        assert len(self._outputs) == 1, f"IF Node can only have one output, but found {len(self._outputs)}"


        self._outputs[self.output_name].value = self._inputs[self.input_name].value

        self._logic_return = self._execute_logic(self._inputs[self.input_name].value)
        if self._logic_return:
            print(f"run yes branch, input value: {self._inputs[self.input_name].value}") 
            self._outputs[self.output_name].links = [self._yes_link]
        else:
            print(f"run no branch, input value: {self._inputs[self.input_name].value}")
            self._outputs[self.output_name].links = [self._no_link]

    @property
    def logic_return(self):
        return self._logic_return
    
    @property
    def yes_link(self):
        return self._yes_link
    
    @property
    def no_link(self):
        return self._no_link
    
    @property
    def output_name(self):
        assert len(self._outputs) == 1, f"IF Node can only have one output, but found {len(self._outputs)}"
        
        return list(self._outputs.keys())[0]
    
    @property
    def input_name(self):
        assert len(self._inputs) == 1, f"IF Node can only have one input, but found {len(self._inputs)}"
        
        return list(self._inputs.keys())[0]
    