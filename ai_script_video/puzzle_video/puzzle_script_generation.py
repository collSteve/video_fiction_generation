from pydantic import BaseModel
from api_handlers.chatgpt_api_handler import call_chatGPT, ChatGPTReturnObj, openai_client


class PuzzleScriptObj(BaseModel):
    introduction: str
    ask_puzzle: str
    inter_prompting: str
    answer_reveal: str
    engage_prompt: str
    engage_act: str
    follow_request: str


# puzzle_info format: {"puzzle_type": "", "puzzle_question": "puzzle_answer":""}
def generate_script(puzzle_info: dict[str, str], system_prompt_path = "script_creation_prompt") -> (PuzzleScriptObj|None):
    with open(system_prompt_path, "r") as f:
        sys_prompt = f.read()

    # contruct input
    script_gen_input = {
        "puzzle_type": puzzle_info["puzzle_type"],
        "puzzle_question": puzzle_info["puzzle_question"],
        "puzzle_answer": puzzle_info["puzzle_answer"],
    }

    prompt = str(script_gen_input)
    # call chatGPT
    try:
        res_obj = call_chatGPT(sys_prompt, prompt, model="gpt-4o-mini", response_format=PuzzleScriptObj, chatGPT_completion_func=openai_client.beta.chat.completions.parse)
        
        # validate format
        if res_obj.first_valid_message is None:
            raise Exception("No valid message found in response")
        
        if res_obj.first_valid_message.parsed is None:
            raise Exception("No valid parsed message found in response")
        

        # validate content
        necessary_keys = ["introduction", "ask_puzzle", "inter_prompting", "answer_reveal", "engage_prompt", "engage_act", "follow_request"]

        for key in necessary_keys:
            if key not in res_obj.first_valid_message.parsed.dict().keys():
                raise Exception(f"Key {key} not found in response")
        
        result: PuzzleScriptObj = res_obj.first_valid_message.parsed
        return  result
    
    except Exception as e:
        raise Exception(f"Error when generating script: {e}")


a = {
  "puzzle_type": "Word Riddle",
  "puzzle_question": "What has keys but can't open locks?",
  "puzzle_answer": "A piano"
}

    