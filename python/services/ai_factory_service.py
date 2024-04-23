# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  Factory AI Service
#

import os
from enum import Enum

# import custom code
from .base_service import BaseAIService
from .gemini.gemini_service import GeminiAIService
from .openai.openai_service import OpenAIService

class Provider(Enum):
    """provider types"""
    GEMINI = 'gemini'
    OPENAI = 'azure_openai'

    @staticmethod
    def from_string(value: str) -> "Provider":
        """Maps a string to the corresponding Provider enum value. Use quotes to avoid circular reference"""
        try:
            return Provider(value)
        except ValueError:
            raise ValueError(f"Invalid provider name: {value}")


def get_provider(provider_name: Provider) -> BaseAIService:
    """Factory function to create providers based on name."""
    providers = {
        Provider.GEMINI: GeminiAIService,
        Provider.OPENAI: OpenAIService
    }

    # get the environment values or use a KeyVault
    provider = provider_name.value.upper()
    api_key = os.getenv(f"{provider}_KEY")           # Retrieve API key from environment
    api_engine = os.getenv(f"{provider}_DEPLOYMENT")  # Retrieve deployment/model     
    api_endpoint = os.getenv(f"{provider}_ENDPOINT")    # custom endpoint

    if provider_name not in providers:
        raise ValueError(f"Invalid provider name: {provider}")
    
    if api_key is None:        
        print(f'{provider} : adding keys resolve the environment variables not loading')
        # raise ValueError(f"Invalid API Key: {provider}")    
            
    # print(providers[provider_name])    
    return providers[provider_name](api_key, api_engine, api_endpoint)