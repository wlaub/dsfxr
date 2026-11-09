
import json
import random

import pygame
import pygame.mixer

import pyfxr

class SoundManager:
    def __init__(self, basedir):
        self.basedir = basedir

        self.sound_infos = {}
        for filebase in os.listdir(source_dir): #TODO walk the tree
            if filebase[-5:] != '.json': continue
            filename = os.path.join(source_dir, filebase)
            sound_path = filebase[-5:]
            thing = SoundInfo(filename)
            self.sounds_infos[sound_path] = thing

        self.queues = {}

    def get_sound(self, sound_path, version = None):
        #path_to_sound[:version]
        if version is None:
            try:
                sound_path, version = sound_path.split(':')
            except:
                version = -1
        queue = self.get_queue(sound_path, version)
        result = queue.get_sound()
        return result

    def get_queue(self, sound_path, version):
        key = (sound_path, version)
        if not key in self.queues.keys():
            si = self.sound_infos[sound_path]
            if version < 0:
                version += len(si.versions)
            self.queues[key] = DSFXR(si, version)
        return self.queues[key]

class SoundInfo:
    def __init__(self, filename):
        with open(filename, 'r') as fp:
            data = fp.read()
        self.name = data['name']
        self.variant_count = data.get('variant_count', 7)
        self.versions = {i:x for i,x in enumerate(data['versions'])}



class DSFXR:
    def __init__(self, sound_info, version):
        self.sound_info = sound_info
        self.variant_count = sound_info.variant_count

        self.version = sound_info.versions[version]
        self.params = version['params']
        self.variance = version['variance']
        self.wave_type = self.params.pop('wave_type')

        _,_,channels = pygame.mixer.get_init()
        self.stereo = channels==2

        self.variants = []
        self.pool = []
        self.dirty = False

        for _ in range(self.variant_count)
            self.make_sound()

    def make_sound(self):
        tparams = {}
        for param, value in self.params.items():
            v = self.variance[param]
            offset = random.uniform(-v,v)
            tparams[param] = value + offset

        thing = pyfxr.SFXR(wave_type = self.wave_type, **params)

        buffer = thing.build(stereo=self.stereo)
        sound = pygame.mixer.Sound(buffer=buffer)

        self.variants.append(sound)
        self.variants = self.variants[1:]
        self.dirty = False

    def get_sound(self):
        self.dirty = True

        if not self.pool:
            self.pool = random.sample(self.variants, k=len(self.variants))

        result, self.pool = self.pool[0], self.pool[1:]
        return result



