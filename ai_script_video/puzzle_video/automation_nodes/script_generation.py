from ai_script_video.puzzle_video.puzzle_script_generation import generate_script
from automation.automation_node import AutomationNode, TaskStatus, TaskInput


class ScriptGenerationTask(AutomationNode):

    def __init__(self):
        super().__init__()

        # add inputs
        self._inputs["puzzle_item"] = TaskInput(type="PuzzleDBItem", value=None, name="puzzle_item", link=None)
        self._inputs["script_system_prompt_path"] = TaskInput(type="str", value=None, name="script_system_prompt_path", link=None)

        # add outputs
        self._outputs["generated_script"] = TaskInput(type="PuzzleScriptObj", value=None, name="generated_script", link=None)
    
    def _run(self):
        super()._run()

        generated_script = generate_script(self._inputs["puzzle_item"], system_prompt_path=self._inputs["script_system_prompt_path"])


        if generated_script is None:
            raise Exception("Generated script is None (probably gpt error)")
        
        self._outputs["generated_script"] = generated_script
        self._status = TaskStatus.Completed