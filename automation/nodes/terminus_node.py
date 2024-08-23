from typing import Any, Callable
from automation.automation_node import AutomationNode

# Special nodes that are used to start and end the automation graph
class TerminusNode(AutomationNode):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)
    
    def add_input(self, input_name: str, input_type: str, validator: Callable[[Any], bool] = None):
        super().add_input(input_name, input_type, validator)
        try:
            self.add_output(input_name, input_type, validator)  # Terminus node has the same input and output
        except ValueError:  # escape mutual recursion
            pass

    def add_output(self, output_name: str, output_type: str, validator: Callable[[Any], bool] = None):
        super().add_output(output_name, output_type, validator)
        try:
            self.add_input(output_name, output_type, validator) # Terminus node has the same input and output
        except ValueError:  # escape mutual recursion
            pass

    def _run(self):
        # copy input values to output values
        for input_name in self._inputs:
            self._outputs[input_name].value = self._inputs[input_name].value
    
