import os, sys
import math, time
import datetime
import json
import random

import pygame
import pygame.mixer

import pyfxr

import ui
from config import Config


class PhysicsDemo:


    def run(self):
        while self.running:
            try:
                self.loop()
            except NotImplementedError as e:
                print(f'NotYetImplementedError: {e}')
                print(f"----------------------: stats dmp'd")
                print(f"----------------------: state clr'd")
            except Exception as e:
                print(e)

    def __init__(self):

        pygame.mixer.pre_init(44100, channels=2)

        pygame.init()

        pygame.mixer.init(channels=16)

        self.ws = 1280
        self.hs = 720

        self.main_screen = pygame.display.set_mode((self.ws, self.hs))
        pygame.display.set_caption(f"dsfxr")
        self.clock = pygame.time.Clock()

        pygame.mouse.set_visible(True)

        self.font = pygame.font.Font(None, 28)

        self.widgets = []

        params = {  'env_attack':(0,1,0),
                    'env_sustain':(0,1,0.3),
                    'env_punch':(0,1,0.4),
                    'env_decay':(0,1,0),
                    'base_freq':(0,1,0.3),
                    'freq_limit':(0,1,0),
                    'freq_ramp':(-1,1,0),
                    'freq_dramp':(-1,1,0),
                    'vib_strength':(0,1,0),
                    'vib_speed':(0,1,0),
                    'arp_mod':(-1,1,0),
                    'arp_speed':(0,1,0),
                    'duty':(0,1,0),
                    'duty_ramp':(-1,1,0),
                    'repeat_speed':(0,1,0),
                    'pha_offset':(-1,1,0),
                    'pha_ramp':(-1,1,0),
                    'lpf_freq':(0,1,1),
                    'lpf_ramp':(-1,1,0),
                    'lpf_resonance':(0,1,0),
                    'hpf_freq':(0,1,0),
                    'hpf_ramp':(-1,1,0),
                    'sound_vol':(0,1,0.5),
                    }

        xpos = 220
        ypos = 10
        w = 200
        h = 21

        self.wave_type = 0
        self.wave_buttons = []
        def wave_button(i):
            self.wave_type = i
            self.update_wave_buttons()
            self.sound_valid = False
            self.play_sound()

        for i, wave in enumerate(['sq','saw','sine','noise']):

            b = ui.Button(self, wave, xpos+i*w/4, ypos, w/4-3, h)

            b.callback = lambda i=i: wave_button(i)
            self.widgets.append(b)
            self.wave_buttons.append(b)
        self.update_wave_buttons()

        ypos += h+3

        self.params = {}
        for name, (vmin, vmax, vdef) in params.items():
            s = ui.Slider(self, name, xpos, ypos, w, h, vmin, vmax, vdef)
            self.widgets.append(s)
            self.params[name] = s
            ypos += h+3

        #variance
        xpos = 430
        ypos = 10+21+3
        w = 300
        h = 21

        def update_variance(self):
            self.app.params[self.label].variance = self.value

        self.variance_sliders = {}
        for name, (vmin, vmax, vdef) in params.items():
            s = ui.Slider(self, name, xpos, ypos, w, h, 0,0.5,0)
            s.on_change = update_variance
            self.widgets.append(s)
            self.variance_sliders[name]=s
            ypos += h+3




        self.channel = None
        self.sound_valid = False
        self.get_sound()


        xpos = 10
        ypos = 10
        w = 200
        h = 28

        b = ui.Button(self, 'play sound', xpos, ypos, w, h)

        b.callback = self.play_sound
        self.widgets.append(b)
        ypos += h+21

        b = ui.Button(self, 'randomize', xpos, ypos, w, h)
        def randomize():
            self.sound = pyfxr.randomize()
            self.sound.wave_type = self.wave_type
            self.apply_sound_to_sliders()
            self.play_sound()

        b.callback = randomize
        self.widgets.append(b)
        ypos += h+3

        b = ui.Button(self, 'mutate', xpos, ypos, w, h)
        def mutate():
            sound = self.get_sound()
            self.sound = sound.mutate()
            self.apply_sound_to_sliders()
            self.play_sound()

        b.callback = mutate
        self.widgets.append(b)
        ypos += h+21

        presets = {
                'pickup/coin': pyfxr.pickup,
                'laser/shoot': pyfxr.laser,
                'explosion': pyfxr.explosion,
                'powerup': pyfxr.powerup,
                'hit/hurt': pyfxr.hurt,
                'jump': pyfxr.jump,
                'blip/select': pyfxr.select,
                }

        def apply_preset(callback):
            params = callback().as_dict()
            self.sound = pyfxr.SFXR(**params)
            self.apply_sound_to_sliders()
            self.play_sound()


        for label, callback in presets.items():
            b = ui.Button(self, label, xpos, ypos, w, h)

            b.callback = lambda cb=callback: apply_preset(cb)
            self.widgets.append(b)
            ypos += h+3



        self.running = True

        """
        source_dir = 'sounds/references'
        self.configs = {}
        for filebase in os.listdir(source_dir):
            filename = os.path.join(source_dir, filebase)

            name = '.'.join(filebase.split('.')[:-1])
            print(name)

            with open(filename, 'r') as fp:
                raw = json.load(fp)
            params = {k[2:]:v for k,v in raw.items() if k[:2] == 'p_'}

            for param in {'env_attack', 'arp_speed', 'duty', 'lpf_resonance', 'env_punch', 'vib_strength', 'hpf_freq'}:
                if params[param] < 0:
                    params[param]*=-1

            params['wave_type'] = raw['wave_type']

            if params.get('vib_delay', False) is None:
                params.pop('vib_delay',None)

            thing = pyfxr.SFXR(**params)
            buffer = thing.build()

            config = Config(name, params)
            self.configs[name] = config

            if name == 'player_dead_1' and False:
                print(thing.as_dict())
                dead_thing = thing
                sound = pygame.mixer.Sound(buffer=buffer)
                channel = sound.play()
                time.sleep(sound.get_length()+1)


        with open('sounds/real_sfxr.json', 'rb') as fp:
            import struct
            braw = fp.read()
            fields = ['version', 'p_wave_type', 'sound_vol', 'p_base_freq', 'p_freq_limit', 'p_freq_ramp', 'p_freq_dramp', 'p_duty', 'p_duty_ramp', 'p_vib_strength', 'p_vib_speed', 'p_vib_delay', 'p_env_attack', 'p_env_sustain', 'p_env_decay', 'p_env_punch', 'filter_on', 'p_lpf_resonance', 'p_lpf_freq', 'p_lpf_ramp', 'p_hpf_freq', 'p_hpf_ramp', 'p_pha_offset', 'p_pha_ramp', 'p_repeat_speed', 'p_arp_speed', 'p_arp_mod']
            print(len(braw))
            schema = 'iiffffffffffffff?ffffffffff'
            temp = braw[:]
            data = {}
            for glyph, field in zip(schema, fields):
                if glyph != '?':
                    chunk, temp = temp[:4], temp[4:]
                else:
                    chunk, temp = temp[:1], temp[1:]
                val = struct.unpack(glyph, chunk)[0]
#                print(field, val)
                data[field] = val


        params = {k[2:]:v for k,v in data.items() if k[:2] == 'p_'}
        thing = pyfxr.SFXR(**params)
        thing = pyfxr.load_sfxr('sounds/real_sfxr.json')

        N = 1
        start_time = time.time()
        for _ in range(N):
            thing = pyfxr.SFXR(**params)
            buffer = thing.build(stereo=True)
        end_time = time.time()
        print(f'{(end_time-start_time)/N} s ({N=})')

        sound = pygame.mixer.Sound(buffer=buffer)
#        channel = sound.play()
#        time.sleep(sound.get_length()+1)

#            raw = struct.unpack('iiffffffffffffff?ffffffffff', braw) #i have no idea why this doesn't work. it says it needs a buffer of 108 bytes but like... that is not what i have described here
#            data = dict(zip(fields, raw))

        thing = pyfxr.randomize()
        thing.sound_vol = 0.5
        for _ in range(3):
            thing = thing.mutate()
#            print(thing)
            buffer = thing.build()
            sound = pygame.mixer.Sound(buffer=buffer)
#            channel = sound.play()
#            time.sleep(sound.get_length()+1)
        """

    def update_wave_buttons(self):
        for idx, button in enumerate(self.wave_buttons):
            if idx == self.wave_type:
                button.bg_color = (192,192,255)
            else:
                button.bg_color = (255,255,255)


    def apply_sound_to_sliders(self):
        params = self.sound.as_dict()
        default_params = pyfxr.SFXR()
        for s in self.params.values():
            s.value = params.get(s.label, getattr(default_params, s.label))
        if 'wave_type' in params.keys():
            self.wave_type = params['wave_type']
        else:
            self.wave_type = default_params.wave_type.value
        self.update_wave_buttons()

    def get_sound(self):
        if not self.sound_valid or True:
            self.sound_valid = True
            params = {x.label:x.value for x in self.params.values()}

            variance = {x.label:x.value for x in self.variance_sliders.values()}

            for param, value in params.items():
                v = variance[param]
                offset = random.uniform(-v,v)
                params[param] += offset
                self.params[param].pointer = params[param]
                self.variance_sliders[param].pointer = offset

            params['wave_type'] = self.wave_type
            self.sound = pyfxr.SFXR(**params)
        return self.sound

    def play_sound(self):
        if self.channel is not None and self.channel.get_busy():
            self.channel.stop()

        thing = self.get_sound()
        buffer = thing.build(stereo=True)
        sound = pygame.mixer.Sound(buffer=buffer)
        self.channel = sound.play()

    def draw(self):
        for w in self.widgets:
            w.render(self.main_screen)

    def do_updates(self):
        pass
    def clear_screen(self):
        self.main_screen.fill((0,0,0))

    def loop(self):

        tick = False
        self.keys = pygame.key.get_pressed()
        self.mpos = pygame.mouse.get_pos()

        for w in self.widgets:
            w.update(self.mpos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for w in self.widgets:
                        w.mouse_down(self.mpos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for w in self.widgets:
                        w.mouse_up(self.mpos)


        now = datetime.datetime.now()



        self.clear_screen()

        self.draw()

        pygame.display.flip()

        self.clock.tick(60)

if __name__ == '__main__':
    demo = PhysicsDemo()
    demo.run()









