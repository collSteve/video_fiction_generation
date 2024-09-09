from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ai_script_video.puzzle_video.simple_code_automation import PuzzleAutomationService

# create exception for puzzle task failure
class PuzzleTaskFailure(Exception):
    pass

class PuzzleBaseTask:
    def __init__(self, puzzle_automation_service):
        self.puzzle_automation_service : PuzzleAutomationService = puzzle_automation_service

    # To be implemented by the subclass
    def _run(self):
        raise NotImplementedError()
    
    def execute(self):
        try:
            return self._run()
        except Exception as e:
            raise PuzzleTaskFailure(f"Error in puzzle task <{self.__class__.__name__}>: {str(e)}")