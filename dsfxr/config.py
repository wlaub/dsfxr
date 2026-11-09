import os, sys
import time, math
import copy

import json



class Project:
    def __init__(self, app, filename):
        self.app = app
        self.filename = filename
        self.name = self._get_name(filename)
        self.basedir = self._get_basedir(filename)
        self.versions = []
        self.current = {'params':{},'variance':{}}
        self.dirty = True

    def _get_name(self, filename):
        return filename.split('/')[-1][:-5]

    def _get_basedir(self, filename):
        return os.path.join(*(filename.split('/')[:-1]))

    @classmethod
    def load(cls, app, filename):
        with open(filename, 'r') as fp:
            data = json.load(fp)
        result = cls(app, filename)
        result.from_dict(data)
        result.dirty_check()
        return result

    def from_dict(self, data):
        self.current = data['current']
        self.versions = data['versions']

    def to_dict(self):
        result = {
            'name': self.name,
            'current': self.current,
            'versions': self.versions,
            }
        return result

    def save(self):
        if len(self.versions) == 0 or self.current != self.versions[-1]:
            self.versions.append(copy.deepcopy(self.current))
        with open(self.filename, 'w') as fp:
            json.dump(self.to_dict(), fp)
        self.dirty_check()

    def dirty_check(self):
        if len(self.versions) > 0:
            if active:=self.app.version_select.active:
                last = active[1]
            else:
                last = self.versions[-1]
            if self.current['params'] != last['params'] or self.current['variance'] != last['variance']:
                self.dirty = True
            else:
                self.dirty = False
        else:
            self.dirty = True


    def update_params(self, params, variance):
        self.current['params'] = params
        self.current['variance'] = variance
        self.dirty_check()


class Config:

    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.distros = {}

class ParamDistribution:

    def __init__(self, kind, kwargs):
        self.kind = kind
        self.kwargs = kwargs

