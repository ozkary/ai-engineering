#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  HTTP request service
#

import requests
from typing import Dict, Optional, Any

class Request():
    """
    HTTP Request service to handle GET, POST, PATCH, PUT, DELETE requests.
    """

    headers: Optional[Dict[str, str]] = None
    
    def get(self, url: str, **kwargs: Any) -> requests.Response:
        """GET the URL and return the response."""
        return requests.get(url, headers=self.headers, **kwargs)

    def post(self, url: str, data: Dict[str, Any], **kwargs: Any) -> requests.Response:
        """POST to the URL and return the response."""
        return requests.post(url, json=data, headers=self.headers, **kwargs)

    def patch(self, url: str, data: Dict[str, Any], **kwargs: Any) -> requests.Response:
        """PATCH the URL and return the response."""
        return requests.patch(url, json=data, headers=self.headers, **kwargs)

    def put(self, url: str, data: Dict[str, Any], **kwargs: Any) -> requests.Response:
        """PUT the URL and return the reponse."""
        return requests.put(url, json=data, headers=self.headers, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        """DELETE the URL and return the response."""
        return requests.delete(url, headers=self.headers, **kwargs)
