from ai_script_video.puzzle_video.puzzle_generation import generate_puzzles
from ai_script_video.puzzle_video.puzzle_persistence import PuzzleDBItem, PuzzleItemStatus, QueryObj, query_puzzle_item
from automation.automation_node import AutomationNode, TaskStatus, TaskInput


class PuzzleGenerationTask(AutomationNode):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self.add_input("puzzle_db_path", "path")
        self.add_input("puzzle_creation_system_prompt_path", "path")

        # add outputs
        self.add_output("generated_puzzles", "List[PuzzleDBItem]")
    
    def _run(self):
        past_puzzle_questions = self.get_past_puzzle_questions()

        generated_puzzles = generate_puzzles(past_puzzle_questions, sys_prompt_path=self._inputs["puzzle_creation_system_prompt_path"].value)

        if generated_puzzles is None:
            raise Exception("Generated puzzles are None (probably gpt error)")
        
        db_items = []
        for puzzle in generated_puzzles:
            puzzle_db_item = PuzzleDBItem(**puzzle.model_dump(), status=PuzzleItemStatus.Unused)
            db_items.append(puzzle_db_item)

        
        self._outputs["generated_puzzles"].value = db_items

    def get_past_puzzle_questions(self):
        queryObj = QueryObj(attribute="puzzle_question", is_valid=lambda x: x is not None)
        puzzle_items = query_puzzle_item(self._inputs["puzzle_db_path"].value, [queryObj])

        return [item.puzzle_question for item in puzzle_items]