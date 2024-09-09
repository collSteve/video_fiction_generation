from __future__ import annotations

from ai_script_video.puzzle_video.code_automation.base_task import PuzzleBaseTask
from ai_script_video.puzzle_video.puzzle_persistence import ProcessStatus, PuzzleItemStatus, QueryObj

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ai_script_video.puzzle_video.simple_code_automation import PuzzleAutomationService


class Unprocessed_Puzzle_Fetcher(PuzzleBaseTask):
    def __init__(self, puzzle_automation_service):
        super().__init__(puzzle_automation_service)

        self.puzzle_db_manager = puzzle_automation_service.puzzle_db_manager

    def _run(self):
        process_status_not_started = lambda x: x is ProcessStatus.Not_Started or x == ProcessStatus.Not_Started
        process_status_failed = lambda x: x is ProcessStatus.Failed or x == ProcessStatus.Failed

        queryObj_item_status = QueryObj(attribute="status", 
                            is_valid=lambda x: x is PuzzleItemStatus.Unused or x == PuzzleItemStatus.Unused)
        queryObj_process_status = QueryObj(attribute="process_status", 
                            is_valid=lambda x: process_status_not_started(x) or process_status_failed(x))
        
        puzzle_items = self.puzzle_db_manager.query_puzzle_item([queryObj_item_status, queryObj_process_status])

        return puzzle_items
    
def fetch_unprocessed_puzzles(puzzle_automation_service: PuzzleAutomationService):
    puzzle_db_manager = puzzle_automation_service.puzzle_db_manager

    process_status_not_started = lambda x: x is ProcessStatus.Not_Started or x == ProcessStatus.Not_Started
    process_status_failed = lambda x: x is ProcessStatus.Failed or x == ProcessStatus.Failed

    queryObj_item_status = QueryObj(attribute="status", 
                        is_valid=lambda x: x is PuzzleItemStatus.Unused or x == PuzzleItemStatus.Unused)
    queryObj_process_status = QueryObj(attribute="process_status", 
                        is_valid=lambda x: process_status_not_started(x) or process_status_failed(x))
    
    puzzle_items = puzzle_db_manager.query_puzzle_item([queryObj_item_status, queryObj_process_status])

    return puzzle_items