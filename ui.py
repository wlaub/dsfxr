

import pygame

class Button:
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


class Slider:
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

    def render(self, screen):
        font = self.app.font

        bg_color = (255,255,255)
        fill_color = (128,128,128)


        fg_color = (0,0,0)

        v = max(self.vmin,min(self.vmax,self.value))
        if v != self.value:
            bg_color = (255,192,192)

        pygame.draw.rect(screen, bg_color, self.rect)
        dx = (v-self.vmin)/(self.vrange)*(self.width-2)
        pygame.draw.rect(screen, fill_color, pygame.Rect(self.xpos+1, self.ypos+1, dx, self.height-2))

        text = font.render(f'{self.label} {self.value:0.2f}', True, fg_color)
        x = self.xpos + (self.width-text.width)/2
        y = self.ypos + (self.height-text.height)/2
        screen.blit(text, (x,y))

    def update(self, mpos):
        self.hovered = self.rect.collidepoint(mpos)
        if self.clicked_on:
            self.value = self.vmin + self.vrange*(mpos[0]-self.xpos)/self.width
            self.value = max(self.vmin,min(self.vmax,self.value))

    def mouse_down(self, mpos):
        if self.hovered:
            self.clicked_on = True
            self.click_start = mpos

    def mouse_up(self, mpos):
        if self.clicked_on:
            self.app.sound_valid = False
            self.app.play_sound()
        self.clicked_on = False



