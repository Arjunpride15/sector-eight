import grid
import tastyerrors
import time
import pyglet
from playsound import playsound
import conf

confObj = conf.Config()
class SectorEight:
    def __init__(self, interface, LIST_INTERFACE):
        self.map_ = grid.identify()
        self.coord_x = 0
        self.coord_y = 0
        self.interface = interface
        self.LIST_INTERFACE = LIST_INTERFACE
        
        
    def canvas_init(self):
            for code in self.map_:
                if code == 'wall':
                    self.LIST_INTERFACE.append(pyglet.sprite.Sprite(img=(pyglet.resource.image('images/tile.gif')), \
                                                               x=(self.coord_x * 40), y=(self.coord_y * 40), batch=self.interface))
                    self.coord_x += 1
                if code == 'blacktile':
                    self.LIST_INTERFACE.append(pyglet.sprite.Sprite(img=(pyglet.resource.image('images/blacktile.gif')), \
                                                               x=(self.coord_x * 40), y=(self.coord_y * 40), batch=self.interface))
                    self.coord_x += 1
                if code == 'food':
                    self.LIST_INTERFACE.append(pyglet.sprite.Sprite(img=(pyglet.resource.image('images/pellet.gif')), \
                                                               x=(self.coord_x * 40), y=(self.coord_y * 40), batch=self.interface))
                    self.coord_x += 1
                if code == 'ghost':
                    self.LIST_INTERFACE.append(pyglet.sprite.Sprite(img=(pyglet.resource.image('images/ghost.gif')), \
                                                               x=(self.coord_x * 40), y=(self.coord_y * 40), batch=self.interface))
                    self.coord_x += 1
                if code == 'eater':
                    self.LIST_INTERFACE.append(pyglet.sprite.Sprite(img=(pyglet.resource.image('images/eater.gif')), \
                                                               x=(self.coord_x * 40), y=(self.coord_y * 40), batch=self.interface))
                    self.coord_x += 1
                if code == 'newline':
                    self.coord_x = 0
                    self.coord_y += 1
                    
                    
                    
    @staticmethod
    def play(file):
        playsound(file)
    @classmethod
    def play_main_music_file(cls):
        while True:
            cls.play(confObj.main_music_path())
    
    def start_(self):
        pyglet.app.run()