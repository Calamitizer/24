#! /usr/bin/env python

import os
import sys
import math
import random
import itertools
import pygame
from pygame.locals import *
from pygame.compat import geterror
from helpers import *
#from helpers import *

class PNC:
    def __init__(self):
        self.running = True
        self.screen = None
        self.allcolors = {
            'K': Color((0,0,0)),
            'R': Color((255,0,0)),
            'G': Color((0,255,0)),
            'B': Color((0,0,255)),
            'C': Color((0,255,255)),
            'M': Color((255,0,255)),
            'Y': Color((255,255,0)),
            'W': Color((255,255,255)),
        } 
        self.tilecolors = {'R': self.allcolors['R'], 'G': self.allcolors['G'], 'B': self.allcolors['B']}
        self.toolcolors = {'C': self.allcolors['C'], 'M': self.allcolors['M'], 'Y': self.allcolors['Y'], 'W': self.allcolors['W']}
        self.matches = {'C': ['G','B'], 'M': ['R','B'], 'Y': ['R','G'], 'W': ['R','G','B']}
        self.grid = 2
        self.buttonsize = 256
        self.colordirs = {
            'R': (0, self.buttonsize/4),
            'B': tuple(map(int, ((self.buttonsize/4) * (-1 * math.sqrt(3./4.)),(self.buttonsize/4) * (-1./2.)))),
            'G': tuple(map(int, ((self.buttonsize/4) * (math.sqrt(3./4.)),(self.buttonsize/4) * (-1./2.))))}
        self.size = self.width, self.height = self.grid * self.buttonsize, self.grid * self.buttonsize
        self.colorkeys = {K_1: 'C', K_2: 'M', K_3: 'Y', K_4: 'W'}
        self.version = '0.01'
        self.title = '27' + ' v' + self.version 
        self.fps = 30
        self.paused = 0

    def on_init(self):
        pygame.init()
        self.sysfont = pygame.font.Font(None, 36)  
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(self.title)
        self.running = True
        self.drawBG()
        self.clock = pygame.time.Clock()
        self.load_images()
        self.load_sounds()
        self.init_sprites()
        self.init_tools()
        self.init_tiles()
        self.init_spaces()
        self.mousex = 0
        self.mousey = 0
        pygame.mouse.set_visible(False)
        
    def drawBG(self):
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((250, 250, 250))
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

    def load_images(self):
        self.images = {}
        self.images['cursor'] = load_image('cursor.gif', -1)
    
    def load_sounds(self):
        self.sounds = {}
        
        self.sounds['whiff'] = load_sound('whiff.wav')
        self.sounds['punch'] = load_sound('punch.wav')
    
    def init_sprites(self):
        self.clickables = pygame.sprite.Group()
        self.spritesdict = {}
        
        self.cursor = pygame.sprite.GroupSingle()
        self.spritesdict['cursor'] = Cursor()
        self.cursor.add(self.spritesdict['cursor'])

        self.sprites = pygame.sprite.Group()
        
        self.tools = pygame.sprite.Group()
        tools = ['A','B','C','D']
    
    def init_spaces(self):
        self.spacegroup = pygame.sprite.Group()
        for i in xrange(self.grid):
            for j in xrange(self.grid):
                self.spacegroup.add(Tile_Space(i, j))
    
    def init_menu(self):
        self.menuoptions = pygame.sprite.Group()
        items = ['Return','Restart','Quit']
        self.menulist = []
        for i, item in enumerate(items):
            self.menulist.append(MenuOption(item))
            self.clickables.add(self.menulist[-1])
            self.menuoptions.add(self.menulist[-1])
            w = self.menulist[-1].rect.width
            h = self.menulist[-1].rect.height
            x = (self.width/2) - (w/2)
            y = (self.height/2) - (len(items)*h/2) + (i*h) + (i*2)
            self.menulist[-1].x = x
            self.menulist[-1].y = y

    def init_tools(self):
        self.toolgroup = pygame.sprite.GroupSingle()
        self.change_tool('W')
        
    def change_tool(self, c):
        print c
        self.remove_tool()
        self.tool = Tool(c)
        self.toolgroup.add(self.tool)
        
    def remove_tool(self):
        try:
            self.tool.kill()
        except AttributeError:
            pass
        self.tool = None

    def init_tiles(self):
        self.tilelist = []
        self.tilegroup = pygame.sprite.Group()
        self.colorlists = {}
        self.colorgroups = {}
        self.layoutdict = {}
        for c in self.tilecolors:
            self.init_color(c)
            
        # refactor
        self.screenpositions = {}
        for i in xrange(self.grid):
            for j in xrange(self.grid):
                self.screenpositions[(i,j)] = (i*self.buttonsize, j*self.buttonsize)

        self.shuffle(False)

    def init_color(self, c):
        self.colorlists[c] = list()
        self.colorgroups[c] = pygame.sprite.Group()
        self.layoutdict[c] = list()
        for i in xrange(1, self.grid**2):
            tile = (Number_Tile(c,i))
            self.tilelist.append(tile)
            self.colorlists[c].append(tile)
            self.clickables.add(tile)
            self.tilegroup.add(tile)
            self.colorgroups[c].add(tile)

    def to2D(self, i):
        return (i%self.grid, i/self.grid)
        
    def to1D(self, i, j):
        return (self.grid*j) + i
    
    def shuffle(self, s):
        self.won = 0
        for c in self.tilecolors:
            layout = list(self.colorlists[c])
            layout.append(None)
            if s:
                random.shuffle(layout)
                if not self.is_solvable(layout):
                    print `False` + `c` + ': ' + `[tile.n if tile != None else 0 for tile in layout]`
                    n = layout.index(None)
                    if n == 0:
                        i, j = 1, 2
                    elif n == 1:
                        i, j = 0, 2
                    else:
                        i, j = 0, 1
                    layout[j], layout[i] = layout[i], layout[j]
            self.layoutdict[c] = layout
            print `c` + ': ' + `[tile.n if tile != None else 0 for tile in layout]`
            for i, tile in enumerate(layout):
                if tile != None:
                    tile.i, tile.j = self.to2D(i)
    
    def is_solvable(self, layout):
        inv = self.count_inv(layout)
        g = self.grid
        if g % 2 == 1:
            return inv % 2 == 0
        elif g % 2 == 0:
            b = g - self.to2D(layout.index(None))[1]
            return inv % 2 != b % 2

    def count_inv(self, layout):
        order = [tile.n if tile != None else 0 for tile in layout]
        inv = 0
        for i, n in enumerate(order):
            for _, m in enumerate(order[i+1:]):
                if n > m and m != 0:
                    inv += 1
        return inv
    
    def find_tile(self, c, i, j):
        for tile in self.colorlists[c]:
            if tile.i == i and tile.j == j:
                return tile
        return None

    def check_win(self):
        for _, tile in enumerate(self.tilelist):
            if tile.n != 1 + self.to1D(tile.i, tile.j):
                self.won = 0
                return
        self.win()

    def win(self):
        self.won = 1
    
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.quit()
        if not self.paused:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.quit()
                if event.key == K_p:
                    self.pause()
                if event.key == K_s:
                    self.shuffle(True)
                if event.key == K_r:
                    self.shuffle(False)
                if event.key == K_w:
                    self.check_win()
                if event.key in self.colorkeys:
                    self.change_tool(self.colorkeys[event.key])
            elif event.type == MOUSEBUTTONDOWN:
                clicked = [_ for _ in self.clickables if _.is_over((self.mousex, self.mousey))]
                for s in clicked:
                    s.on_click()
            elif event.type == MOUSEBUTTONUP:
                pass
        elif self.paused:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.unpause()
                if event.key == K_p:
                    self.unpause()
            elif event.type == MOUSEBUTTONDOWN:
                for item in self.menuoptions:
                    if item.selected:
                        item.on_click()        
        
    def on_loop(self):
        self.mousex, self.mousey = pygame.mouse.get_pos()
        self.tilegroup.update()
        self.spacegroup.update()
        self.toolgroup.update()
        self.cursor.update()
        self.check_win()
        
    def on_render(self):
        if not self.paused:
            self.tilegroup.clear(self.screen, self.background)
            self.screen.blit(self.background, (0,0))
            self.spacegroup.draw(self.screen)
            self.toolgroup.draw(self.screen)
            #self.targetgroup.draw(self.screen)
            #self.sprites.update()
            #self.sprites.draw(self.screen)
            #self.toolgroup.update()
            #self.toolgroup.draw(self.screen)

        if self.paused:
            self.cover = pygame.Surface(self.size).convert()
            self.cover.fill((0,0,0))
            font = pygame.font.Font(None, 72)
            text = font.render('Pause', 1, (255,0,0))
            textpos = text.get_rect(center=(self.width/2,self.height/5))
            self.cover.blit(text,textpos)
            
            self.menuoptions.update()
            for i, item in enumerate(self.menulist):
                self.cover.blit(item.image, (item.x,item.y))
                
            self.screen.blit(self.cover, (0,0))
        
        text = self.sysfont.render('FPS: {0:.2f}'.format(self.clock.get_fps()), 1, (255,0,0))
        textpos = text.get_rect(bottomleft=(0,self.height))
        self.screen.blit(text,textpos)
        
        text = self.sysfont.render('Inv: {0:.0f}, Won: {1:.0f}'.format(0, self.won), 1, (255,0,0))
        textpos = text.get_rect(bottomright=(self.width,self.height))
        self.screen.blit(text,textpos)
        
        self.cursor.draw(self.screen)
                
        pygame.display.flip()
        
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self.quit()
        while self.running:
            deltat = self.clock.tick(self.fps)
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def pause(self):
        self.init_menu()
        self.paused = 1
        
    def unpause(self):
        #self.menuoptions.clear(self.screen, self.background)
        self.menuoptions.empty()
        self.paused = 0
    
    def menufunction(self, name):
        if name == 'Return':
            self.unpause()
        elif name == 'Restart':
            print name
        elif name == 'Quit':
            self.quit()
    
    def quit(self):
        self.running = False

class Color:
    def __init__(self, (r, g, b)):
        self.r = r
        self.g = g
        self.b = b
        self.h = (self.r, self.g, self.b)
    def __str__(self):
        return `self.h`
    def __repr__(self):
        return 'Color({0})'.format(self.h)
    def __add__(self,rhs):
        r = min(self.r + rhs.r, 255)
        g = min(self.g + rhs.g, 255)
        b = min(self.b + rhs.b, 255)
        return Color((r, g, b))
    def __sub__(self, rhs):
        r = max(self.r - rhs.r, 0)
        g = max(self.g - rhs.g, 0)
        b = max(self.b - rhs.b, 0)
        return Color((r, g, b))
    def __eq__(self, rhs):
        return self.h == rhs.h
    def __ne__(self, rhs):
        return not self.__eq__(rhs)
    def __gt__(self, other):
        self._illegal('>')
    def __ge__(self, other):
        self._illegal('>=')
    def __lt__(self, other):
        self._illegal('<')
    def __le__(self, other):
        self._illegal('<=')
    def __nonzero__(self):
        return bool(self.h == (0, 0, 0))
    def _illegal(self, op):
        print 'Illegal operation "%s" for cyclic integers' % op

class MenuOption(pygame.sprite.Sprite):
    """An button on the pause menu"""
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.selected = 0
        self.font = self.dfont = None
        self.size = self.dsize = 36
        self.color = self.dcolor = (127,127,127)
        self.render()
        
    def render(self):
        font = pygame.font.Font(self.font, self.size)
        self.image = font.render(self.name, 1, self.color)
        self.rect = self.image.get_rect()
    
    def revert_font(self):
        self.font = self.dfont
        self.size = self.dsize
        self.color = self.dcolor
        self.render()
    
    def change_font(self, font):
        self.font = font
        self.render()
        
    def change_size(self, size):
        self.size = size
        self.render()
        
    def change_color(self, color):
        self.color = color
        self.render()

    def is_over(self, (x,y)):
        xb = (self.x <= x) and (x < self.x + self.rect.width)
        yb = (self.y <= y) and (y < self.y + self.rect.height)
        return xb and yb        

    def update(self):
        if self.is_over((PNC.mousex,PNC.mousey)):
            if self.selected == 0:
                self.select()
        else:
            if self.selected == 1:
                self.deselect()
    
    def select(self):
        self.selected = 1
        self.change_color((255,0,0))
        
    def deselect(self):
        self.selected = 0
        self.change_color(self.dcolor)
    
    def on_click(self):
        PNC.menufunction(self.name)

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('cursor.gif')

    def update(self):
        pos = (PNC.mousex, PNC.mousey)
        self.rect.center = pos

    def click(self, target):
        w = -1*self.rect.width/2 + 5
        hitbox = self.rect.inflate(w, w)
        return hitbox.colliderect(target.rect)

class Tool(pygame.sprite.Sprite):
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.size = 64
        self.selected = 0
        self.get_image()
        
    def get_image(self):
        self.image = pygame.Surface((self.size, self.size)).convert()
        colorkey = self.image.get_at((0,0))
        self.image.set_colorkey(colorkey, RLEACCEL)
        pygame.draw.circle(self.image, (1,1,1), (self.size/2, self.size/2), self.size/2)
        pygame.draw.circle(self.image, PNC.toolcolors[self.color].h, (self.size/2, self.size/2), self.size/2 - 4)
        self.rect = self.image.get_rect()

    def update(self):
        pos = (PNC.mousex, PNC.mousey)
        self.rect.center = pos

class Tile_Space(pygame.sprite.Sprite):
    def __init__(self, i, j):
        pygame.sprite.Sprite.__init__(self)
        self.fontstyle = None
        self.fontsize = 72
        self.i = i
        self.j = j
        self.x = self.i * PNC.buttonsize
        self.y = self.j * PNC.buttonsize
        self.colors = set()
        self.font = pygame.font.Font(self.fontstyle, self.fontsize)
        self.get_colors()
        self.get_image()

    def get_colors(self):
        for c in PNC.tilecolors:
            tile = PNC.find_tile(c, self.i, self.j)
            if tile:
                self.add_color(c)
            else:
                self.remove_color(c)
            
    def add_color(self, c):
        if not c in self.colors:
            self.colors.add(c)
        
    def remove_color(self, c):
        if c in self.colors:
            self.colors.remove(c)

    def get_image(self):
        self.image = pygame.Surface((PNC.buttonsize,PNC.buttonsize)).convert()
        r = PNC.tilecolors['R'].h if 'R' in self.colors else PNC.allcolors['K'].h
        g = PNC.tilecolors['G'].h if 'G' in self.colors else PNC.allcolors['K'].h
        b = PNC.tilecolors['B'].h if 'B' in self.colors else PNC.allcolors['K'].h
        color = tuple(map(sum, zip(r, g, b)))
        color = tuple(255 - v for v in color)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.render_font()

    def render_font(self):
        for c in self.colors:
            tile = PNC.find_tile(c, self.i, self.j)
            text = self.font.render(`tile.n`, 1, PNC.tilecolors[c].h)
            rect = text.get_rect()
            x = PNC.buttonsize/2 - PNC.colordirs[c][0]
            y = PNC.buttonsize/2 - PNC.colordirs[c][1]
            rect.center = (x, y)
            self.image.blit(text, rect)

    def update(self):
        self.get_colors()
        self.get_image()
        self.x = PNC.buttonsize*self.i
        self.y = PNC.buttonsize*self.j
        self.rect.topleft = (self.x, self.y)

class Number_Tile(pygame.sprite.Sprite):
    def __init__(self, color, n):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.n = n
        self.selected = 0
        self.font = self.dfont = None
        self.fontsize = self.dfontsize = 36
        self.fontcolor = self.dfontcolor = (250,250,250)
        self.i = 0
        self.j = 0
        self.x = 0
        self.y = 0
        self.get_image()
        self.render_font()

    def get_image(self):
        self.image = pygame.Surface((PNC.buttonsize,PNC.buttonsize)).convert()
        self.rect = self.image.get_rect()

    def render_font(self):
        font = pygame.font.Font(self.font, self.fontsize)
        text = font.render(`self.n`, 1, self.fontcolor)
        pos = text.get_rect()
        pos.center = self.image.get_rect().center
        self.image.blit(text, pos)

    def revert_font(self):
        self.font = self.dfont
        self.fontsize = self.dfontsize
        self.fontcolor = self.dfontcolor
        self.render_font()
    
    def change_font(self, font):
        self.font = font
        self.render_font()
        
    def change_size(self, size):
        self.fontsize = size
        self.render_font()
        
    def change_color(self, color):
        self.fontcolor = color
        self.render_font()

    def update(self):
        self.x = PNC.buttonsize*self.i
        self.y = PNC.buttonsize*self.j
        if self.is_over((PNC.mousex,PNC.mousey)):
            if self.selected == 0:
                self.select()
        else:
            if self.selected == 1:
                self.deselect()

    def is_over(self, (x,y)):
        xb = (self.x <= x) and (x < self.x + self.rect.width)
        yb = (self.y <= y) and (y < self.y + self.rect.height)
        return xb and yb

    def select(self):
        self.selected = 1
        self.fontcolor = (250,0,0)
        self.render_font()

    def deselect(self):
        self.selected = 0
        self.fontcolor = self.dfontcolor
        self.render_font()

    def on_click(self):
        print 'Clicked!'
        d = self.find_free()
        print self.color
        if d and self.color in PNC.matches[PNC.tool.color]:
            print self.color
            self.move(d)
            PNC.sounds['punch'].play()
        else:
            PNC.sounds['whiff'].play()

    def find_free(self):
        for i, j in [(-1,0), (1,0), (0,-1), (0,1)]:
            if self.i + i in range(PNC.grid) and self.j + j in range(PNC.grid):
                tile = PNC.find_tile(self.color, self.i + i, self.j + j)
                if not tile:
                    return (i ,j)

    def move(self, (i, j)):
        print True
        self.i += i
        self.j += j

if __name__ == "__main__" :
    PNC = PNC()
    PNC.on_execute()
    pass
