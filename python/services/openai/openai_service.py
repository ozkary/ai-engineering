"""OpenAI Service"""
# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  OpenAI service by Microsoft
#  See https://oai.azure.com/ to manage keys and deployments
#
import os
import json

# import openai library
from openai import AzureOpenAI

# Set up OpenAI API credentials in the ~/.bashrc file
# api_key = os.getenv("AZURE_OPENAI_KEY")
# api_base = os.getenv("AZURE_OPENAI_ENDPOINT")    # custom endpoint
# api_url = os.getenv("AZURE_OPENAI_DEPLOYMENT")   # this will change based on your deployment

class OpenAIService:
    def __init__(self, api_key: str, engine: str = None, end_point: str = None, temperature: float = 0.5, max_tokens: int = 2500, n: int = 1, stop: str = None):
        
        self.client = AzureOpenAI(
                        azure_endpoint = end_point, 
                        api_key=api_key,  
                        api_version="2024-02-01")
                        
        self.engine = 'depCodeDavinci002' 
        # engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n = n
        self.stop = stop
        
    def create(self, prompt: str) -> str:
        """Create a completion using the OpenAI API."""
                
        response = self.client.completions.create(
            model=self.engine,
            prompt=prompt,
            max_tokens=self.max_tokens,
            n=self.n,
            stop=self.stop,
            temperature=self.temperature
        )

        print(response.choices[0].text)       
        return response.choices[0].text
