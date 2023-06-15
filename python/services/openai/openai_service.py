"""OpenAI Service"""
# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  OpenAI service
#

import json
import openai
import os

class OpenAIService:
    def __init__(self, api_key: str, engine: str = 'text-davinci-003', end_point: str = None, temperature: float = 0.5, max_tokens: int = 350, n: int = 1, stop: str = None):
        openai.api_key = api_key

        # Azure OpenAI API custom resource
        # Use these settings only when using a custom endpoint like https://ozkary.openai.azure.com        
        if end_point is not None:
            openai.api_base = end_point                  
            openai.api_type = 'azure'
            openai.api_version = '2023-05-15' # this will change as the API evolves

        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n = n
        self.stop = stop
        
    def create(self, prompt: str) -> str:
        """Create a completion using the OpenAI API."""
                
        response = openai.Completion.create(
            engine=self.engine,
            prompt=prompt,
            max_tokens=self.max_tokens,
            n=self.n,
            stop=self.stop,
            temperature=self.temperature
        )

        print(response)       
        return response.choices[0].text.strip()
