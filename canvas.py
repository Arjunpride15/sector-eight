import grid
import tastyerrors
import time
import pyglet
import conf
import winsound
import miniaudio
import shelve
from pyglet import shapes
import threading
class SectorEight:
    def __init__(self):
        # Basic stuff
        self.map_ = grid.identify()
        self.coord_x = 0
        self.coord_y = 0
        self.interface = pyglet.graphics.Batch()
        self.confObj = conf.Config()
        # Music stuff
        self.main_music_file = self.confObj.main_music_path()
        
        # For canvas_init()
        self.food_dict = {}
        self.ghost_dict = {}
        self.eater_sprite = None
        self.food_sprite = None
        self.ghost_sprite = None
        self.music_switch = False
        # Pellets!
        self.data_store = shelve.open('game_data')
        self.pellets = self.data_store.get('pellets', 0)
        self.pellet_label = pyglet.text.Label(
            f'Pellets: {self.pellets}',
            font_name='Courier New',
            font_size=18,
            x=20, y=800, # Positioning in the bottom-left
            anchor_x='left', anchor_y='bottom',
            batch=self.interface,
            color=(255, 255, 0, 255) # Yellow/Gold color
        )
        
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
                    winsound.PlaySound("audio/main-music.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                                       
            else:
                # For custom music files passed via kwargs
                device = miniaudio.PlaybackDevice()
                stream = miniaudio.stream_file(kwargs['music_file'])
                device.start(stream)
        except KeyError:
            return 'KeyError Encountered'
    
        
    def stop_music(self):
        winsound.PlaySound(None, winsound.SND_FILENAME)
        self.music_switch = False
    
        
    def play_main_music_file(self, dt):
        
        self.__class__.play(self)
        
    def laser(self):
        
        self.horizontal_line = shapes.Line(0, self.eater_sprite.y, 1600,self.eater_sprite.y , \
                                            thickness=4, color=(21, 234, 100), batch=self.interface)
        self.horizontal_line.opacity = 150
        
        
        
    def update(self, dt):
        if self.eater_sprite:
            # 1. Calculate the potential new position
            new_x = self.eater_sprite.x + (self.direction[0] * self.speed * dt)
            new_y = self.eater_sprite.y + (self.direction[1] * self.speed * dt)
            
            # 2. Collision Leeway (Hitbox Shrinking)
            # We subtract a few pixels from the edges so the eater 'fits' better
            padding = 6 
            
            collision = False
            for wall in self.walls:
                # Check overlap with padding applied to the eater's box
                if (new_x + padding < wall.x + wall.width and
                    new_x + self.eater_sprite.width - padding > wall.x and
                    new_y + padding < wall.y + wall.height and
                    new_y + self.eater_sprite.height - padding > wall.y):
                    collision = True
                    break

            # 3. Apply movement if clear
            if not collision:
                self.eater_sprite.x = new_x
                self.eater_sprite.y = new_y

            # 4. Pellet Detection (Your original logic)
            # We use +20 to check the 'tile' the eater is mostly over
            grid_pos = (int((self.eater_sprite.x + 20) // 40), 
                        int((self.eater_sprite.y + 20) // 40))
            
            if grid_pos in self.food_dict:
                # Remove pellet and update count
                self.food_dict[grid_pos].delete() 
                del self.food_dict[grid_pos]      
                
                self.pellets += 1
                self.pellet_label.text = f'Pellets: {self.pellets}'
                
                # Persistence
                self.data_store['pellets'] = self.pellets
                self.data_store.sync()
                
                # Audio
                chomp_path = self.confObj.toml_dict['music']['chompEffect']
                self.play(music_file=chomp_path)
    
    def return_batch(self):
        return self.interface
       
    def start_(self):
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        self.play_main_music_file(self)
        
        pyglet.app.run()