import grid
import tastyerrors
import time
import pyglet

class SectorEight:
    def __init__(self, interface, LIST_INTERFACE):
        self._map = None
        self.coord_x = None
        self.coord_y = None
        self.interface = interface
        SELF.LIST_INTERFACE = LIST_INTERFACE
        
        
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
    def play(file, **kwargs):
        sound = pyglet.media.load(file, streaming=False)
    
        player = pyglet.media.Player()
        player.queue(sound)
        if kwargs:
            player.volume = kwargs[volume]
            player.loop = kwargs[loop]
        else:
            player.volume = 0.5  # Set volume (0.0 to 1.0)
            player.loop = True   # Enable looping
        player.play()
