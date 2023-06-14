# -*- coding: utf-8 -*-
#
#  2023 ozkary.com.
#
#  GitHub API data types
#

from dataclasses import dataclass

@dataclass
class Issue:
    id: str
    title: str
    body: str

@dataclass
class Parameter:
    label: str
    state: str


