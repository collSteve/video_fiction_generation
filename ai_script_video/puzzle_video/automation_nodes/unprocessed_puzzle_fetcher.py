from ai_script_video.puzzle_video.puzzle_persistence import QueryObj, query_puzzle_item
from automation.automation_node import AutomationNode, TaskStatus, TaskVariable


class UnprocessedPuzzleFetcher(AutomationNode):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self._inputs["puzzle_db_path"] = TaskVariable(type="str", value=None, name="puzzle_db_path", link=None)

        # add outputs
        self._outputs["unprocessed_puzzles"] = TaskVariable(type="List[RawPuzzle]", value=None, name="unprocessed_puzzles", link=None)
    
    def _run(self):
        super()._run()

        queryObj = QueryObj(attribute="process_status", is_valid=lambda x: x is ProcessStatus.Not_Started)
        puzzle_items = query_puzzle_item(self._inputs["puzzle_db_path"], [queryObj])

        self._outputs["unprocessed_puzzles"] = puzzle_items
        self._status = TaskStatus.Completed
