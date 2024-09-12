from typing import Any, List
from dotenv import load_dotenv
import os

from openai import OpenAI, ChatCompletion

# load_dotenv("../.env")
load_dotenv()
# print(os.getenv("OPENAI_API_KEY"))
openai_client = OpenAI()

chatgpt_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]

# response format: { "type": "json_schema", "json_schema": {...} }
# response format: { "type": "json_object" }
def call_chatGPT(system_prompt, prompt, model="gpt-3.5-turbo", max_tokens=None, chat_history:List[dict[str,str]]=[], response_format=None, chatGPT_completion_func = openai_client.chat.completions.create):
	optional_params = {"model": model, "max_tokens": max_tokens, "chat_history": chat_history, "response_format": response_format, "chatGPT_completion_func": chatGPT_completion_func}

	# remove None values from optional_params
	optional_params = {k: v for k, v in optional_params.items() if v is not None}

	raw_response: ChatCompletion = raw_call_ChatGPT(system_prompt, prompt, **optional_params)

	try:
		chatGPT_return_obj = ChatGPTReturnObj(raw_response)
		return chatGPT_return_obj
	except AssertionError as e:
		print(f"Error: {e}")
		print(f"raw_response: {raw_response}")
	return None

openai_chat_completion_optional_params = ["max_tokens", "response_format"]

def raw_call_ChatGPT(system_prompt, prompt, model="gpt-3.5-turbo", max_tokens=None, chat_history:List[dict[str,str]]=[], response_format=None, 
					 chatGPT_completion_func = openai_client.chat.completions.create):
	optional_params = {"model": model, "max_tokens": max_tokens, "chat_history": chat_history, "response_format": response_format}

	# remove None values from optional_params
	optional_params = {k: v for k, v in optional_params.items() if v is not None}

	# pick only the optional params
	optional_params = {k: v for k, v in optional_params.items() if k in openai_chat_completion_optional_params}


	# Call the GPT-3 API
	assert model in chatgpt_models, f"Model {model} not found in available models: {chatgpt_models}"
	
	# vlidate chat_history
	if len(chat_history) > 0:
		for message in chat_history:
			assert "role" in message, "role key not found in chat_history"
			assert "content" in message, "content key not found in chat_history"
			assert message["role"] in ["user", "system", "assistant"], "role key should be 'user', 'assistant', or 'system'"

	messages: List[dict[str,str]] = [
		{"role": "system", "content": system_prompt},
		*chat_history,
		{"role": "user", "content": prompt}
	]


	response = chatGPT_completion_func(
		model=model,
		messages=messages,
		**optional_params
	)
	return response




class ChatGPTReturnObj:
	def __init__(self, raw_response):
		self._error, self._choices, self._model, self._created = self.chatGPT_return_validator(raw_response)

	def chatGPT_return_validator(self, raw_response):
		error = None
		# handle error
		assert raw_response.choices is not None, "choices key not found in response"
		assert len(raw_response.choices) > 0, "choices key is empty"

		assert raw_response.model is not None, "model key not found in response"
		assert raw_response.created is not None, "created key not found in response"

		# validate choices
		for choice in raw_response.choices:
			assert choice.message is not None, "message key not found in choices"
			assert choice.finish_reason is not None, "finish_reason key not found in choices"

			if choice.finish_reason  != "stop":
				error = choice.finish_reason
		
		return error, raw_response.choices, raw_response.model, raw_response.created
	
	@property
	def choices(self):
		return self._choices
	
	@property
	def error(self):
		return self._error
	
	@property
	def model(self):
		return self._model
	
	@property
	def created(self):
		return self._created
	
	@property
	def first_valid_message(self):
		for choice in self._choices:
			if choice.finish_reason == "stop" and choice.message.role == "assistant" and choice.message.refusal is None:
				return choice.message
		return None
	
	@property
	def num_valid_choices(self):
		return len([choice for choice in self._choices if choice.finish_reason == "stop" and choice.message.role == "assistant"])
	


openai_text2image_model = ["dall-e-3", "dall-e-2"]
size_options = ["1024x1024",  "1024x1792", "1792x1024"]

def generate_image(prompt, model, size="1024x1024", quality="standard"):
	response = openai_client.images.generate(
		model=model,
		prompt=prompt,
		size=size,
		quality=quality,
		n=1,
	)
	return response