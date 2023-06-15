import openai
import json
import os

def generate_response(prompt : str) -> str:
    response = openai.Completion.create(
        engine="text-davinci-003", 
        prompt=prompt ,
        max_tokens=256, 
        top_p=1,
        stop=None, 
        temperature=0.5,
        frequency_penalty=0,
        presence_penalty=0        
    )

def build_prompt(context: str, technologies: str, description: str, result: str= '') -> str:    
    prompt = {'Context': context, 'Technologies': technologies, 'Description' : description, 'Result' : result}                
    # print(prompt)
    return json.dumps(prompt, sort_keys=False, indent=2)
    

def user_story_prompt(context: str, technologies: str, requirements: str, result: str= '') -> str:    
    prompt = {'User Story': context, 'Technologies': technologies, 'Requirements' : requirements, 'Specifications' : result}                
    # print(prompt)
    return json.dumps(prompt, sort_keys=False, indent=2)


openai.api_key = os.getenv("OPENAI_API_KEY")
print('==>', openai.api_key)
    
