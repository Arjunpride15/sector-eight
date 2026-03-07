import grid
import tastyerrors
import time
import pyglet
import conf
import miniaudio

class SectorEight:
    def __init__(self):
        self.map_ = grid.identify()
        self.coord_x = 0
        self.coord_y = 0
        self.interface = pyglet.graphics.Batch()
        self.confObj = conf.Config()
        self.main_music_file = self.confObj.main_music_path()
        self.main_stream = miniaudio.stream_file(self.main_music_file)
        self.device = miniaudio.PlaybackDevice()
        self.food_dict = {}
        self.ghost_dict = {}
        self.eater_sprite = None
        self.food_sprite = None
        self.ghost_sprite = None
        self.music_switch = False
        self.walls = list()
        self.direction = (0, 0)  # (dx, dy)
        self.speed = 120         # Pixels per second
                

    def canvas_init(self):
        
        for code in self.map_:
            
            px, py = self.coord_x * 40, self.coord_y * 40
            
            if code == 'wall':
                # Remove .draw() - the Batch handles it!
                s = pyglet.sprite.Sprite(img=pyglet.resource.image('images/tile.gif'), 
                                         x=px, y=py, batch=self.interface)
                self.walls.append(s)
                self.coord_x += 1
                
            elif code == 'blacktile':
                s = pyglet.sprite.Sprite(img=pyglet.resource.image('images/blacktile.gif'), 
                                         x=px, y=py, batch=self.interface)
                self.walls.append(s)
                self.coord_x += 1
                
            elif code == 'food':
                self.food_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/pellet.gif'), 
                                                       x=px, y=py, batch=self.interface)
                # Use a tuple key for faster lookup
                self.food_dict[(self.coord_x, self.coord_y)] = self.food_sprite
                self.coord_x += 1
                
            elif code == 'ghost':
                # Changed to a list in dict because you might have multiple ghosts!
                ghost = pyglet.sprite.Sprite(img=pyglet.resource.image('images/pellet.gif'), 
                                            x=px, y=py, batch=self.interface)
                self.ghost_dict[(self.coord_x, self.coord_y)] = ghost
                self.coord_x += 1
                
            elif code == 'eater':
                self.eater_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/eater.gif'), 
                                                        x=px, y=py, batch=self.interface)
                self.coord_x += 1
                
            elif code == 'newline':
                self.coord_x = 0
                self.coord_y += 1
    def return_eater(self):
        return self.eater_sprite
                        
    def play(self, **kwargs):
        try:
            if not kwargs:
                # Start the device (Music starts)
                if not self.music_switch:
                    self.device.start(self.main_stream)
                    self.music_switch = True                    
            else:
                stream = miniaudio.stream_file(kwargs['music_file'])
                self.device.start(stream)
        except KeyError:
            return 'KeyError Encountered'
        
    def stop_music(self):
        self.device.stop()
        
    def play_main_music_file(self):
        self.__class__.play(self)
        
    def resume_music(self):
        self.device.start(self.stream)
    
    def return_batch(self):
        return self.interface    
    def start_(self):
        
        pyglet.app.run()