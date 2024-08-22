from typing import Set

from automation.automation_node import AutomationNode, IFTaskLink, TaskLink, TaskVariable


class AutomationGraph:
    nodes: Set[AutomationNode] = set()
    links: Set[TaskLink|IFTaskLink] = set()

    inputs: dict[str, TaskVariable] = {}
    outputs: dict[str, TaskVariable] = {}

    def __init__(self):
        self.nodes = set()
        self.links = set()

    



    