from typing import Any, Callable
from pydantic import BaseModel

from automation.automation_node import AutomationNode, TaskVariable


class AutomationIFNode(AutomationNode):
    _logic_return: bool | None = None

    _yes_output: TaskVariable | None = None
    _no_output: TaskVariable | None = None

    _output_name: str

    def __init__(self, global_graph, id, execute_logic: Callable[[Any],bool], output_name: str):
        super().__init__(global_graph, id)

        self._execute_logic = execute_logic
        self._output_name = output_name
    
    def add_input(self, input_name: str, input_type: str, validator: Callable[[Any], bool] = None):
        if len(self._inputs) > 0:
            raise ValueError("IF Node can only have one input")
        super().add_input(input_name, input_type, validator)

    def add_output(self, output_name: str, output_type: str, validator: Callable[[Any], bool] = None):
        raise ValueError("You should not use add_oupout on an IF node. Use set_yes_output and set_no_output instead")
    
    def set_yes_output(self, output_name: str, output_type: str, validator: Callable[[Any], bool] = None):
        self._yes_output = TaskVariable(name=output_name, value=None, type=output_type, validator=validator)

    def set_no_output(self, output_name: str, output_type: str, validator: Callable[[Any], bool] = None):
        self._no_output = TaskVariable(name=output_name, value=None, type=output_type, validator=validator)

    def _run(self):
        super()._run()

        assert len(self._inputs) == 1, "IF Node can only have one input"

        self.outputs = {}

        self._logic_return = self._execute_logic(self._inputs[self._input_info.variable_name].value)
        if self._logic_return:
            self.outputs[self._output_name] = self._yes_output
        else:
            self.outputs[self._output_name] = self._no_output

        self.outputs[self._output_name].value = self._inputs.values()[0].value

    @property
    def logic_return(self):
        return self._logic_return