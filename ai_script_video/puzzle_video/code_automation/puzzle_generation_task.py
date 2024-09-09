from typing import List
from ai_script_video.puzzle_video.code_automation.base_task import PuzzleBaseTask
from ai_script_video.puzzle_video.puzzle_generation import generate_puzzles
from ai_script_video.puzzle_video.puzzle_persistence import QueryObj, RawPuzzleItem


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ai_script_video.puzzle_video.simple_code_automation import PuzzleAutomationService


class PuzzleGenerationTask(PuzzleBaseTask):
    def __init__(self, puzzle_automation_service):
        super().__init__(puzzle_automation_service)

        self.puzzle_db_manager = puzzle_automation_service.puzzle_db_manager
        self.puzzle_creation_system_prompt_path = puzzle_automation_service.puzzle_creation_system_info.puzzle_creation_system_prompt_path
    
    def _run(self):
        past_puzzle_questions = self.get_past_puzzle_questions()

        generated_puzzles = generate_puzzles(past_puzzle_questions, sys_prompt_path=self.puzzle_creation_system_prompt_path)

        if generated_puzzles is None:
            raise Exception("Generated puzzles are None (probably gpt error)")
        
        db_items: List[RawPuzzleItem] = []
        for puzzle in generated_puzzles:
            puzzle_db_item = RawPuzzleItem(**puzzle.model_dump())
            db_items.append(puzzle_db_item)

        
        return db_items

    def get_past_puzzle_questions(self):
        queryObj = QueryObj(attribute="puzzle_question", is_valid=lambda x: x is not None)
        puzzle_items = self.puzzle_db_manager.query_puzzle_item([queryObj])

        return [item.puzzle_question for item in puzzle_items]