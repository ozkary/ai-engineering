import json
import os

# import openAI
from openai import OpenAI

# import azure openai library
from openai import AzureOpenAI

class OpenAIService:
    def __init__(self, api_key: str, model: str = 'gpt-3.5-turbo-instruct'):
        
        self.client = OpenAI(
            api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
        )
                        
        self.model = model
        # engine
        self.temperature = 0.5
        self.max_tokens = 2500      


    def generate_response(self, prompt : str) -> str:
        completion = self.client.completions.create(
            model=self.model, 
            prompt=prompt ,
            max_tokens=250, 
            top_p=1,
            stop=None, 
            temperature=0.5,
            frequency_penalty=0,
            presence_penalty=0        
        )

        # code = completion.choices[0].text
        print(dict(completion).get('usage'))
        code = completion.model_dump_json(indent=2)  

class AzureOpenAIService:
    def __init__(self, model: str = "gpt-4", temperature: float = 0.5, max_tokens: int = 2500, n: int = 1, stop: str = None):
        
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.end_point = os.getenv("AZURE_OPENAI_ENDPOINT")    # custom endpoint   
        
        self.client = AzureOpenAI(
                        azure_endpoint = self.end_point, 
                        api_key=self.api_key,  
                        api_version="2024-02-01")
                        
        self.engine = model 
        # engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n = n
        self.stop = stop
        
    def create(self, prompt: str) -> str:
        """Create a completion using the Azure OpenAI."""
                
        messages = [{"role":"user", "content":f"{prompt}"}]
        completion = None
        content = None

        try:

            completion = self.client.chat.completions.create(
                model=self.engine,
                messages=messages,
                max_tokens=self.max_tokens,
                n=self.n,
                stop=self.stop,
                temperature=self.temperature
            )
        except Exception as e:
            raise Exception(f"Error sending request: {e}") from e

        try:
            print(completion)  
            content =  completion.choices[0].message.content            
        except Exception as e:
            raise Exception(f"Error reading response: {e}") from e
        
        return content


def build_prompt(context: str, technologies: str, description: str, result: str= '') -> str:    
    """
        build a json prompt for older support (non chat completions)
    """
    prompt = {'Context': context, 'Technologies': technologies, 'Description' : description, 'Result' : result}                
    # print(prompt)
    return json.dumps(prompt, sort_keys=False, indent=2)


def build_message_prompt(context: str, technologies: str, description: str, result: str= '') -> str:    
    """
        builds a message prompt for chat completions 
        Chat message uses JSON as
        {
            "role": "user",
            "content": "prompt"
        } has 
    """
    prompt = f"Context: {context}, Technologies: {technologies}, Description : {description}, Result : {result}"       
    
    # print(prompt)
    return prompt
    

def user_story_prompt(context: str, technologies: str, requirements: str, result: str= '') -> str:    
    prompt = {'User Story': context, 'Technologies': technologies, 'Requirements' : requirements, 'Specifications' : result}                
    # print(prompt)
    return json.dumps(prompt, sort_keys=False, indent=2)
