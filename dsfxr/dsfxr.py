import os
import json
import random
import threading

import pygame
import pygame.mixer

import pyfxr


class SoundManager:
    def __init__(self, basedir):
        self.basedir = basedir

        self.sound_infos = {}
        for dirpath, dirnames, filenames in os.walk(basedir):
            for filebase in filenames:
                if filebase[-5:] != '.json': continue
                filename = os.path.join(dirpath, filebase)
                sound_path = filename[len(basedir)+1:-5]
                thing = SoundInfo(filename)
                self.sound_infos[sound_path] = thing
#                print(f'loaded {sound_path}')

        self.queues = {}

        self.lock = threading.Lock()
        self.caching = set()
        self.cache_list = []

        self.dirty = set()
        self.dirty_list = []

        #TODO sound regen thread?

    def _cache_sound(self, queue):
        with self.lock:
            if not queue in self.caching:
                self.caching.add(queue)
                self.cache_list.append(queue)

    def mark_dirty(self, queue):
        with self.lock:
            if not queue in self.dirty:
                self.dirty.add(queue)
                self.dirty_list.append(queue)

    def thread_tick(self):
        with self.lock:
            if len(self.cache_list) > 0:
                q = self.cache_list[0]
                if q.add_sound():
                    self.caching.remove(q)
                    self.cache_list.remove(q)
            elif len(self.dirty_list) > 0:
                q = self.cache_list[0]
                q.make_sound()
                self.dirty.remove(q)
                self.dirty_list.remove(q)

    def _get_key(self, sound_path, version = None):
        if version is None:
            try:
                sound_path, version = sound_path.split(':')
                version = int(version)
            except:
                version = None
        return (sound_path, version)

    def preload_sound(self, sound_path, version = None):
        key = self._get_key(sound_path, version)
        self.get_queue(key)

    def get_sound(self, sound_path, version = None):
        #path_to_sound[:version]
        key = self._get_key(sound_path, version)
        queue = self.get_queue(key)
        result = queue.get_sound()
        self.mark_dirty(queue)
        return result

    def get_queue(self, key):
        if not key in self.queues.keys():
            sound_path, version = key
            si = self.sound_infos[sound_path]
            if version is None:
                version = si.active_version
            if version < 0:
                version += len(si.versions)

            q = DSFXR(si, version, precache = True) #TODO depend on thread running

            self.queues[key] = q
            self.caching.add(q)

        return self.queues[key]


class SoundInfo:
    def __init__(self, filename):
        with open(filename, 'r') as fp:
            data = json.load(fp)
        self.name = data['name']
        self.variant_count = data.get('variant_count', 7)
        self.versions = {i:x for i,x in enumerate(data['versions'])}
        self.active_version = data.get('active_version', len(self.versions)-1)



class DSFXR:
    def __init__(self, sound_info, version, precache = False):
        self.sound_info = sound_info
        self.variant_count = sound_info.variant_count

        self.version = sound_info.versions[version]
        self.params = self.version['params']
        self.variance = self.version['variance']
        self.wave_type = self.params.pop('wave_type')

        _,_,channels = pygame.mixer.get_init()
        self.stereo = channels==2

        self.lock = threading.Lock()

        self.variants = []
        self.pool = []
        self.dirty = False

        if precache:
            while not self.add_sound():
                pass

    def add_sound(self):
        sound = self._make_sound()
        with self.lock:
            if len(self.variants) < self.variant_count:
                self.variants.append(sound)
            return len(self.variants) >= self.variant_count

    def _make_sound(self):
        tparams = {}
        for param, value in self.params.items():
            v = self.variance[param]
            offset = random.uniform(-v,v)
            tparams[param] = value + offset

        thing = pyfxr.SFXR(wave_type = self.wave_type, **tparams)

        buffer = thing.build(stereo=self.stereo)
        sound = pygame.mixer.Sound(buffer=buffer)
        return sound

    def make_sound(self):
        if self.dirty:
            sound = self._make_sound()
            with self.lock:
                self.variants.append(sound)
                self.variants = self.variants[1:]
                self.dirty = False

    def get_sound(self):
        self.dirty = True

        if not self.pool:
            self.pool = random.sample(self.variants, k=len(self.variants))

        result, self.pool = self.pool[0], self.pool[1:]
        return result



