import grid
import tastyerrors
import time
import pyglet
from playsound import playsound
import conf

class SectorEight:
    def __init__(self, interface, LIST_INTERFACE):
        self.map_ = grid.identify()
        self.coord_x = 0
        self.coord_y = 0
        self.interface = interface
        self.LIST_INTERFACE = LIST_INTERFACE
        self.confObj = conf.Config()
        self.background_source = None
        self.music_player = None
        self.main_music_file = self.confObj.main_music_path()
        
        
        
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


                        
    def play(self, music_file):
        # 1. Load the file into memory (High performance, no lag)
        self.background_source = pyglet.media.load(music_file, streaming=True)
        
        # 2. Create a persistent player instance
        self.music_player = pyglet.media.Player()
        
        # 3. Queue the source
        self.music_player.queue(self.background_source)
        self.music_player.loop = True
        self.music_player.play()
    def stop_music(self):
        self.music_player.pause()
    def play_main_music_file(self):
        self.__class__.play(self, self.main_music_file)
    
    def start_(self):
        pyglet.app.run()