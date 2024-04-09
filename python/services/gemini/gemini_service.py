"""Gemini AI Service"""
# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  AI Gemini service by Google
#

import sys
print(f' Python ver ${sys.version_info}')

# import vendor modules
import google.generativeai as genai
print(f'Gemini version {genai.__version__}')

# import custom modules
from services.base_service import BaseAIService

class GeminiAIService(BaseAIService):
    def __init__(self, api_key: str, engine: str = 'gemini-pro', end_point: str = None):
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(engine)
        
        # Use these settings only when using a custom endpoint like https://ozkary.genai.com        
        if end_point is not None:
            self.api_base = end_point                  
            self.api_version = '1.0' # this will change as the API evolves        
        
    def create(self, prompt: str) -> str:
        """Create a completion using the Gemini API."""
                
        response = self.model.generate_content(prompt)

        print(response.text)       
        return response.text.strip()
