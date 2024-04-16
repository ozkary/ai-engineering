#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  Generate code from a GitHub issue example
#  Base Class for AI services
#

from abc import ABC, abstractmethod

class BaseAIService(ABC):
    """Base class for AI service providers."""

    def __init__(self, api_key: str, model: str = 'none', endpoint: str = None):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint

    @abstractmethod
    def create(self, prompt: str) -> str:
        """Generates text based on the given prompt."""
        raise NotImplementedError
    