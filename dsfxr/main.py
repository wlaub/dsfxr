import os, sys
import math, time
import datetime
import json
import random
import shutil

import pygame
import pygame.mixer

import pyfxr

import crossfiledialog as cfd

import ui
from config import Project
import dsfxr

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
                raise
                print(e)

    def __init__(self):

        source_dir = 'sounds/projects'
        if len(sys.argv) > 1:
            source_dir = sys.argv[1]
        self.source_dir = source_dir

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

        self.history = []
        self.files = {}

        self.widgets = []

        rows = [10,220,330,540,850]

        xpos = rows[0]
        ypos = 10
        w = 200
        h =  self.hs-20

        def on_file_select(self, target):
            filename, project = target

            params = project.current['params']
            variance = project.current['variance']
            self.app.load_params(params, variance)
            self.app.version_select.active = None
            self.app.active_version_slider.value = project.active_version
            self.app.variant_count_slider.value = project.variant_count


        self.file_select = l = ui.ListBox(self, 'files', xpos, ypos, w, h)
        l.items = lambda: sorted(self.files.items())
        l.on_select = on_file_select
        l.is_item_dirty = lambda x: x.dirty

        self.widgets.append(l)



        xpos = rows[1]
        ypos = 10
        w = 100
        h =  self.hs-20

        self.version_select = l = ui.ListBox(self, 'undo', xpos, ypos, w, h)
        def version_select_items():
            if (active := self.file_select.active) is not None:
                return list(enumerate(active[1].versions))[::-1]
            return []

        def on_version_select(self, item):
            idx, version = item
            params = version['params']
            variance = version['variance']
            self.app.load_params(params, variance)

        l.on_select = on_version_select
        l.items = version_select_items


        self.widgets.append(l)


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

        xpos = rows[3]
        ypos = 10
        w = 300
        h = 21

        self.wave_type = 0
        self.wave_buttons = []
        def wave_button(i):
            self.wave_type = i
            self.update_wave_buttons()
            self.sound_valid = False
            self.play_sound()

        waves = ['sq', 'saw', 'sine', 'noise']
        dw = (w-(len(waves)-1)*3)/len(waves)

        for i, wave in enumerate(waves):

            b = ui.Button(self, wave, xpos+i*(dw+3), ypos, dw, h)

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
        xpos = rows[4]
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


        xpos = rows[2]
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
            sound = self.get_sound(raw=True)
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

        ypos += 21


        b = ui.Button(self, 'save', xpos, ypos, w, h)
        def save_project():
            if (active := self.file_select.active) is not None:
                project = active[1]
                if project.dirty:
                    project.save()

        b.callback = save_project
        self.widgets.append(b)
        ypos += h+21


        b = ui.Button(self, 'fork', xpos, ypos, w, h)
        def fork_project():
            if (active := self.file_select.active) is not None:
                project = active[1]
                new_filename = cfd.save_file('', os.path.abspath(project.basedir))
                if new_filename == '': return
                shutil.copy(project.filename, new_filename)
                project = Project.load(self, new_filename)
                self.files[project.name] = project

        b.callback = fork_project
        self.widgets.append(b)
        ypos += h+21

        b = ui.Button(self, 'new', xpos, ypos, w, h)
        def new_project():
            new_filename = cfd.save_file('', os.path.abspath(self.source_dir))
            if new_filename == '': return
            project = Project(self, new_filename)

            default = pyfxr.SFXR()
            project.current['params'] = {k:getattr(default, k)for k,v in self.params.items()}
            project.current['params']['wave_type'] = 0
            self.files[project.name] = project

        b.callback = new_project
        self.widgets.append(b)
        ypos += h+21

        dw = 63
        sw = 42
        self.active_version_slider = s = ui.IntSlider(self, "act'v", xpos, ypos, sw,h)
        s.min_value = lambda:0
        s.max_value = self._get_max_version
        s.on_change = self._update_active_version

        self.widgets.append(s)

        sw = 42
        self.variant_count_slider = s = ui.IntSlider(self, 'vrnts', xpos+dw, ypos, sw,h)
        s.value = 1
        s.min_value = lambda:1
        s.on_change = self._update_variant_count


        self.widgets.append(s)



        #TODO active_version
        #TODO variant_count


        self.running = True

        for filebase in os.listdir(source_dir):
            filename = os.path.join(source_dir, filebase)
            project = Project.load(self, filename)
            self.files[project.name] = project

        """
        sm = dsfxr.SoundManager(source_dir)

        for _ in range(7):
            sound = sm.get_sound('growl_1')
            sound.play()
            time.sleep(sound.get_length())
        """

        """
        source_dir = 'sounds/references'
        for filebase in os.listdir(source_dir):
            filename = os.path.join(source_dir, filebase)

            name = '.'.join(filebase.split('.')[:-1])
            print(name)

            with open(filename, 'r') as fp:
                raw = json.load(fp)
            params = {k[2:]:v for k,v in raw.items() if k[:2] == 'p_'}
            params['wave_type'] = raw['wave_type']
            params.pop('vib_delay',None)

            project = Project(self, name, os.path.join('sounds/projects', f'{name}.json'))
            project.current['params'] = params

            self.files[name] = project
        """

        """

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

    def _update_active_version(self, widget):
        if (active := self.file_select.active) is not None:
            active[1].active_version = widget.value

    def _update_variant_count(self, widget):
        if (active := self.file_select.active) is not None:
            active[1].variant_count = widget.value


    def _get_max_version(self):
        if (active := self.file_select.active) is not None:
            return len(active[1].versions)-1
        else:
            return 1000

    def update_wave_buttons(self):
        for idx, button in enumerate(self.wave_buttons):
            if idx == self.wave_type:
                button.bg_color = (192,192,255)
            else:
                button.bg_color = (255,255,255)


    def load_params(self, params, variance):
        for param, value in params.items():
            if param == 'wave_type':
                self.wave_type = value
            else:
                self.params[param].value=value

        for param, value in variance.items():
            self.variance_sliders[param].value=value


        self.update_wave_buttons()
        self.sound_valid = False
        self.play_sound()


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

    def get_sound(self, raw=False):
        if not self.sound_valid or True:
            self.sound_valid = True
            params = {x.label:x.value for x in self.params.values()}
            params['wave_type'] = self.wave_type

            variance = {x.label:x.value for x in self.variance_sliders.values()}

            if (active:=self.file_select.active) is not None:
                active[1].update_params(params, variance)
                if active[1].dirty:
                    self.version_select.active = None

            if not raw:
                for param, _ in self.params.items():
                    v = variance[param]
                    offset = random.uniform(-v,v)
                    params[param] += offset
                    self.params[param].pointer = params[param]
                    self.params[param].variance = v
                    self.variance_sliders[param].pointer = offset

            self.sound = pyfxr.SFXR(**params)

            """
            if len(self.history) > 0:
                last_label, last = self.history[0]
                new = (params,variance)
                if new != last:
                    self.history.insert(0,(last_label+1,new))
            else:
                self.history.append((0, (params, variance)))
            """


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
        self.mods = pygame.key.get_mods()
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
            elif event.type == pygame.MOUSEWHEEL:
                for w in self.widgets:
                    w.scroll(event.y, self.mods&pygame.KMOD_SHIFT, self.mods&pygame.KMOD_CTRL)

        now = datetime.datetime.now()



        self.clear_screen()

        self.draw()

        pygame.display.flip()

        self.clock.tick(60)

if __name__ == '__main__':
    demo = PhysicsDemo()
    demo.run()









