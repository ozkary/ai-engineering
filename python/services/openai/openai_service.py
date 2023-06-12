"""OpenAI Service"""
# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  OpenAI service
#

import openai

class OpenAIService:
    def __init__(self, api_key: str, engine: str = 'text-davinci-003', temperature: float = 0.5, max_tokens: int = 100, n: int = 1, stop: str = None):
        openai.api_key = api_key
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
        
        return response.choices[0].text.strip()
