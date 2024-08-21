from typing import List
from pydantic import BaseModel

from api_handlers.chatgpt_api_handler import call_chatGPT, ChatGPTReturnObj, openai_client


class RawPuzzle(BaseModel):
    puzzle_type: str
    puzzle_title: str
    puzzle_question: str
    puzzle_answer: str

class RawPuzzleList(BaseModel):
    generated_puzzles: List[RawPuzzle]

def generate_puzzles(past_puzzle_questions:List[str], sys_prompt_path = "puzzle_generation_prompt")->(List[RawPuzzle]|None):
    with open(sys_prompt_path, "r") as f:
        sys_prompt = f.read()

    # contruct input
    prompt = "past_questions: "+ str(past_puzzle_questions)

    # call chatGPT
    try:
        res_obj = call_chatGPT(sys_prompt, prompt, model="gpt-4o-mini", response_format=RawPuzzleList, chatGPT_completion_func=openai_client.beta.chat.completions.parse)
        
        # validate format
        if res_obj.first_valid_message is None:
            raise Exception("No valid message found in response")
        
        if res_obj.first_valid_message.parsed is None:
            raise Exception("No valid parsed message found in response")
        
        if "generated_puzzles" not in res_obj.first_valid_message.parsed.dict().keys():
            raise Exception("No valid parsed message found in response: expect 'generated_puzzles' key")


        # validate content
        necessary_keys = RawPuzzle.model_fields.keys()

        for key in necessary_keys:
            for parsed_item in res_obj.first_valid_message.parsed.generated_puzzles:
                if key not in parsed_item.dict().keys():
                    raise Exception(f"Key {key} not found in parsed_item")
        
        result: List[RawPuzzle] = res_obj.first_valid_message.parsed.generated_puzzles
        return  result
    
    except Exception as e:
        raise Exception(f"Error when generating puzzle: {e}")