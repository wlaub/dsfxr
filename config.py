import os, sys
import time, math

import json


class Config:

    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.distros = {}

class ParamDistribution:

    def __init__(self, kind, kwargs):
        self.kind = kind
        self.kwargs = kwargs

