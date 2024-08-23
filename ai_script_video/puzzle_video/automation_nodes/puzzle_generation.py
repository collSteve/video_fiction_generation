from ai_script_video.puzzle_video.puzzle_generation import generate_puzzles
from ai_script_video.puzzle_video.puzzle_persistence import QueryObj, query_puzzle_item
from automation.automation_node import AutomationNode, TaskStatus, TaskInput


class PuzzleGenerationTask(AutomationNode):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self._inputs["puzzle_db_path"] = TaskInput(type="str", value=None, name="puzzle_db_path", link=None)
        self._inputs["puzzle_creation_system_prompt_path"] = TaskInput(type="str", value=None, name="puzzle_creation_system_prompt_path", link=None)

        # add outputs
        self._outputs["generated_puzzles"] = TaskInput(type="List[RawPuzzle]", value=None, name="generated_puzzles", link=None)
    
    def _run(self):
        super()._run()

        past_puzzle_questions = self.get_past_puzzle_questions()

        generated_puzzles = generate_puzzles(past_puzzle_questions, system_prompt_path=self._inputs["puzzle_creation_system_prompt_path"])

        if generated_puzzles is None:
            raise Exception("Generated puzzles are None (probably gpt error)")
        
        self._outputs["generated_puzzles"] = generated_puzzles
        self._status = TaskStatus.Completed

    def get_past_puzzle_questions(self):
        queryObj = QueryObj(attribute="puzzle_question", is_valid=lambda x: x is not None)
        puzzle_items = query_puzzle_item(self._inputs["puzzle_db_path"], [queryObj])

        return [item.puzzle_question for item in puzzle_items]