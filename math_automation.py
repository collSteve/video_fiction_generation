from automation.automation_graph import AutomationGraph
from automation.automation_node import AutomationNode, TaskInput, TaskOutput, TaskStatus, VariableStatus
from automation.nodes.terminus_node import TerminusNode


class Addition(AutomationNode):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)
        self._inputs = {
            "a": TaskInput(type="number", name="a"),
            "b": TaskInput(type="number", name="b"),
        }
        self._outputs = {
            "sum": TaskOutput(type="number", name="sum"),
        }

    def _run(self):
        self._outputs["sum"].value = self._inputs["a"].value + self._inputs["b"].value


math_graph = AutomationGraph()
addition_node_1 = Addition(math_graph, "addition1")
addition_node_2 = Addition(math_graph, "addition2")
start_node = TerminusNode(math_graph, "start")
end_node = TerminusNode(math_graph, "end")

start_node.add_input("a", "number")
start_node.add_input("b", "number")
start_node.add_input("c", "number")

end_node.add_output("sum", "number")

math_graph.add_node(addition_node_1)
math_graph.add_node(addition_node_2)
math_graph.add_node(start_node)
math_graph.add_node(end_node)

math_graph.set_start_node("start")
math_graph.set_end_node("end")

math_graph.add_link("start", "a", "addition1", "a")
math_graph.add_link("start", "b", "addition1", "b")
math_graph.add_link("start", "c", "addition2", "b")
math_graph.add_link("addition1", "sum", "addition2", "a")
math_graph.add_link("addition2", "sum", "end", "sum")

math_graph.set_input_value("a", 10)
math_graph.set_input_value("b", 2)
math_graph.set_input_value("c", -1)

math_graph.execute()

print(math_graph.outputs)