

import pygame

class Widget:
    def scroll(self, inc, shift=False, ctrl=False):
        pass

class Button(Widget):
    def __init__(self, app, label, xpos, ypos, width, height):
        self.app = app
        self.label = label
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height

        self.rect = pygame.Rect(xpos, ypos, width, height)

        self.clicked_on = False
        self.hovered = False

        self.callback = lambda : 0

        self.bg_color = (255,255,255)

    def render(self, screen):
        font = self.app.font

        bg_color = self.bg_color if not self.hovered else (128,128,128)
        if self.hovered:
            if self.clicked_on:
                bg_color = (128,128,128)
            else:
                bg_color = (192,192,192)


        fg_color = (0,0,0)

        pygame.draw.rect(screen, bg_color, self.rect)

        text = font.render(self.label, True, fg_color)
        x = self.xpos + (self.width-text.width)/2
        y = self.ypos + (self.height-text.height)/2
        screen.blit(text, (x,y))

    def update(self, mpos):
        self.hovered = self.rect.collidepoint(mpos)

    def mouse_down(self, mpos):
        if self.hovered:
            self.clicked_on = True

    def mouse_up(self, mpos):
        if self.hovered and self.clicked_on:
            self.callback()

        self.clicked_on = False


class Slider(Widget):
    def __init__(self, app, label, xpos, ypos, width, height, vmin, vmax, vdef):
        self.app = app
        self.label = label
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height

        self.vmin = vmin
        self.vmax = vmax
        self.vrange = self.vmax-self.vmin
        self.vdef = vdef
        self.value = vdef

        self.rect = pygame.Rect(xpos, ypos, width, height)

        self.click_start = 0
        self.clicked_on = False
        self.hovered = False

        self.callback = lambda : 0

        self.variance = 0
        self.pointer = None
        self.on_change = None
        self.on_update = None

    def render(self, screen):
        font = self.app.font

        bg_color = (255,255,255)
        fill_color = (192,192,128)
        text_color = (0,0,0)

        fg_color = (0,0,0)
        var_color = (128,128,192)

        vl = max(self.vmin,min(self.vmax,self.value-self.variance))
        vr = max(self.vmin,min(self.vmax,self.value+self.variance))
        v = max(self.vmin,min(self.vmax,self.value))
        if v != self.value:
            bg_color = (255,192,192)

        pygame.draw.rect(screen, bg_color, self.rect)
        dx = (v-self.vmin)/(self.vrange)*(self.width-2)
        pygame.draw.rect(screen, fill_color, pygame.Rect(self.xpos+1, self.ypos+1, dx, self.height-2))
        dxl = (vl-self.vmin)/(self.vrange)*(self.width-2)
        dxr = (vr-self.vmin)/(self.vrange)*(self.width-2)
        w = max(dxr-dxl,1)
        pygame.draw.rect(screen, var_color, pygame.Rect(self.xpos+1+dxl, self.ypos+1, w, self.height-2))

        if self.pointer is not None:
            p = min(self.vmax,self.pointer)
            if p < self.vmin:
                p = 2*self.vmin-p
            px = (p-self.vmin)/(self.vrange)*(self.width-2)
            pygame.draw.line(screen, (0,0,0), (self.xpos+1+px, self.ypos), (self.xpos+1+px, self.ypos+self.height))

        text = font.render(f'{self.label}', True, text_color)
#        x = self.xpos + (self.width-text.width)/2
        x = self.xpos + 2
        y = self.ypos + (self.height-text.height)/2
        screen.blit(text, (x,y))

        text = font.render(f'{self.value:0.4f}', True, text_color)
        x = self.xpos + self.width - text.width - 2
        y = self.ypos + (self.height-text.height)/2
        screen.blit(text, (x,y))


    def update(self, mpos):
        self.hovered = self.rect.collidepoint(mpos)
        if self.clicked_on:
            if self.on_change:
                self.on_change(self)
            self.value = self.vmin + self.vrange*(mpos[0]-self.xpos)/self.width
            self.value = max(self.vmin,min(self.vmax,self.value))

    def scroll(self, inc, shift=False, ctrl=False):
        if not self.hovered: return
        inc*=.05
        if shift: inc *= 0.1
        if ctrl: inc*= 0.02
        self.value += inc

    def mouse_down(self, mpos):
        if self.hovered:
            self.clicked_on = True
            self.click_start = mpos

    def mouse_up(self, mpos):
        if self.clicked_on:
            if self.on_update:
                self.on_update(self)
            self.app.sound_valid = False
            self.app.play_sound()
        self.clicked_on = False


class IntSlider(Slider):
    def __init__(self, app, label, xpos, ypos, width, height):
        super().__init__(app, label, xpos, ypos, width, height, 0,0,0)
        self.min_value = None
        self.max_value = None

    def mouse_down(self, mpos):
        pass
    def mouse_up(self, mpos):
        pass
    def scroll(self, inc, shift, ctrl):
        if not self.hovered: return
        old_value = self.value
        self.value += inc
        if self.min_value:
            self.value = max(self.value,self.min_value())
        if self.max_value:
            self.value = min(self.value,self.max_value())
        self.value = int(self.value)
        if self.on_change and self.value != old_value:
            self.on_change(self)


    def render(self, screen):
        font = self.app.font

        bg_color = (255,255,255)
        fill_color = (192,192,128)
        text_color = (0,0,0)

        fg_color = (0,0,0)
        var_color = (128,128,192)

        pygame.draw.rect(screen, bg_color, self.rect)

        text = font.render(f'{self.label}', True, var_color)
#        x = self.xpos + (self.width-text.width)/2
        x = self.xpos + (self.width-text.width)/2
        y = self.ypos + self.height+2
        screen.blit(text, (x,y))

        text = font.render(f'{self.value}', True, text_color)
        x = self.xpos + (self.width - text.width)/2
        y = self.ypos + (self.height-text.height)/2
        screen.blit(text, (x,y))



class ListBox(Widget):
    def __init__(self, app, label, xpos, ypos, width, height):
        self.app = app
        self.label = label
        self.xpos = xpos
        self.ypos = ypos
        self.width = width
        self.height = height

        self.line_height = 21

        self.rect = pygame.Rect(xpos, ypos, width, height)

        self.clicked_on = False
        self.hovered = False

        self.active = None
        self.on_select = None

        self.items = lambda: []

        self.is_item_dirty = lambda x: False

    def render(self, screen):
        font = self.app.font

        bg_color = (128,128,128)

        fg_color = (0,0,0)

        sel_color = (128,128,255)

        pygame.draw.rect(screen, bg_color, self.rect)

        x = self.xpos + 1
        y = self.ypos +1
        for label, item in self.items():
            if (label, item) == self.active:
                pygame.draw.rect(screen, sel_color, pygame.Rect(x, y, self.width-2, self.line_height))

            string = str(label)
            if self.is_item_dirty(item):
                string += '*'
            text = font.render(string, True, fg_color)

            screen.blit(text, (x,y))
            y+= self.line_height

    def update(self, mpos):
        self.hovered = self.rect.collidepoint(mpos)

    def mouse_down(self, mpos):
        if self.hovered:
            self.clicked_on = True

    def mouse_to_idx(self, mpos):
        y = (mpos[1]-self.ypos-1)/self.line_height
        return int(y)

    def mouse_up(self, mpos):
        if self.clicked_on:
            idx = self.mouse_to_idx(mpos)
            items = list(self.items())
            if len(items) > idx:
                target = items[idx]
                if self.active != target:
                    self.active = target
                    if self.on_select:
                        self.on_select(self, target)
        self.clicked_on = False



