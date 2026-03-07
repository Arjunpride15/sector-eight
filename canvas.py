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
        self.main_stream = None
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
                s = pyglet.sprite.Sprite(img=pyglet.resource.image('images/tile.gif'), 
                                        x=px, y=py, batch=self.interface)
                self.walls.append(s)
            elif code == 'blacktile':
                s = pyglet.sprite.Sprite(img=pyglet.resource.image('images/blacktile.gif'), 
                                        x=px, y=py, batch=self.interface)
                self.walls.append(s)
            elif code == 'food':
                self.food_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/pellet.gif'), 
                                                    x=px, y=py, batch=self.interface)
                self.food_dict[(self.coord_x, self.coord_y)] = self.food_sprite
            elif code == 'ghost':
                ghost = pyglet.sprite.Sprite(img=pyglet.resource.image('images/ghost.gif'), 
                                            x=px, y=py, batch=self.interface)
                self.ghost_dict[(self.coord_x, self.coord_y)] = ghost
            elif code == 'eater':
                self.eater_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/eater.gif'), 
                                                        x=px, y=py, batch=self.interface)
            
            # Handle coordinate movement
            if code == 'newline':
                self.coord_x = 0
                self.coord_y += 1
            else:
                # Increment X for EVERYTHING that isn't a newline
                self.coord_x += 1
                        
    def play(self, **kwargs):
        try:
            if not kwargs:
                if not self.music_switch:
                    # Use the loop=True parameter here
                    self.main_stream = miniaudio.stream_file(self.main_music_file)
                    self.device.start(self.main_stream)
                    self.music_switch = True                    
            else:
                # For custom music files passed via kwargs
                stream = miniaudio.stream_file(kwargs['music_file'])
                self.device.start(stream)
        except KeyError:
            return 'KeyError Encountered'
        
    def stop_music(self):
        self.device.stop()
        self.music_switch = False
        
    def play_main_music_file(self, dt):
        
        self.__class__.play(self)
        
        
    def resume_music(self):
        self.device.start(self.stream)
    def update(self, dt):
        if self.eater_sprite:
            # Calculate potential new position
            new_x = self.eater_sprite.x + (self.direction[0] * self.speed * dt)
            new_y = self.eater_sprite.y + (self.direction[1] * self.speed * dt)
            
            # For now, let's just move him. 
            # (Next, we'll add wall collision logic here!)
            self.eater_sprite.x = new_x
            self.eater_sprite.y = new_y

            # Check for food collision
            grid_pos = (int(new_x // 40), int(new_y // 40))
            if grid_pos in self.food_dict:
                self.food_dict[grid_pos].delete() # Remove from screen
                del self.food_dict[grid_pos]      # Remove from memory
                # You could play a 'chomp' sound here too!
    
    def return_batch(self):
        return self.interface    
    def start_(self):
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.clock.schedule_interval(self.play_main_music_file, 43/60.0)
        pyglet.app.run()