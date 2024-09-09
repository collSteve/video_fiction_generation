from ai_script_video.puzzle_video.puzzle_persistence import ProcessStatus, PuzzleItemStatus, QueryObj, query_puzzle_item
from automation.automation_node import AutomationNode, TaskStatus, TaskInput


class UnprocessedPuzzleFetcher(AutomationNode):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self.add_input("puzzle_db_path", "path")

        # add outputs
        self.add_output("unprocessed_puzzles", "List[RawPuzzle]")
    
    def _run(self):
        process_status_not_started = lambda x: x is ProcessStatus.Not_Started or x == ProcessStatus.Not_Started
        process_status_failed = lambda x: x is ProcessStatus.Failed or x == ProcessStatus.Failed

        queryObj_item_status = QueryObj(attribute="status", 
                            is_valid=lambda x: x is PuzzleItemStatus.Unused or x == PuzzleItemStatus.Unused)
        queryObj_process_status = QueryObj(attribute="process_status", 
                            is_valid=lambda x: process_status_not_started(x) or process_status_failed(x))
        
        puzzle_items = query_puzzle_item(self._inputs["puzzle_db_path"].value, [queryObj_item_status, queryObj_process_status])

        self._outputs["unprocessed_puzzles"].value = puzzle_items
