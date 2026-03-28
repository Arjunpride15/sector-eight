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
import utilities
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
        self.eater_sprite = None
        self.food_sprite = None
        self.magnet_dict = {}
        self.magnet_sprite = None
        self.ghost_sprite = None
        self.music_switch = False
        self.walls = list()
        self.font_list = ['Cascadia Mono', 'Cascadia Code','Courier New']
        self.grid_pos = None
        # Pellets!
        self.data_store = shelve.open('game_data')
        self.pellets = self.data_store.get('pellets', 0)
        self.pellet_label = pyglet.text.Label(
            f'Pellets: {self.pellets}',
            font_name=self.font_list,
            font_size=18,
            x=20, y=800,
            anchor_x='left', anchor_y='bottom',
            batch=self.interface,
            color=(255, 255, 0, 255) # Yellow/Gold color
        
        )
        # Laser Stuff
        self.laser_powers = 5
        self.laser_label = pyglet.text.Label(
            f'Laser Power: {self.laser_powers}',
            font_name=self.font_list,
            font_size=18,
            x=200, y=800,
            anchor_x='left', anchor_y='bottom',
            batch=self.interface,
            color=(34, 139, 34, 255)# Forest green color
        )
        self.laser_obj = None
        self.xp_speedups = 3
        self.xp_label = pyglet.text.Label(
            f'XP Speedups: {self.xp_speedups}',
            font_name=self.font_list,
            font_size=18,
            x=450, y=800,
            anchor_x='left', anchor_y='bottom',
            batch=self.interface,
            color=(0, 130, 160, 255)
        )
        self.walls = list()
        self.direction = (0, 0)  # (dx, dy)
        self.speed = 120         # Pixels per second
        self.TILE_SIDE = 40
        self.ghost_respawn_coord = [0, 0]
                
    
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
                self.ghost_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/ghost.gif'), 
                                            x=px, y=py, batch=self.interface)
                self.ghost_respawn_coord[0] = self.ghost_sprite.x
                self.ghost_respawn_coord[1] = self.ghost_sprite.y
                
            elif code == 'eater':
                self.eater_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/eater.gif'), 
                                                        x=px, y=py, batch=self.interface)
            elif code == 'magnet':
                self.magnet_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/magnet.gif'), 
                                                    x=px, y=py, batch=self.interface)
                self.magnet_dict[(self.coord_x, self.coord_y)] = self.magnet_sprite
            
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
        if self.laser_powers >= 1:
            self.laser_obj = shapes.Line(0, self.eater_sprite.y + (self.TILE_SIDE / 2), 1600, \
                                        self.eater_sprite.y + (self.TILE_SIDE / 2), \
                                        thickness=4, color=(21, 234, 100), batch=self.interface)
            laser_path = self.confObj.toml_dict['music']['laserBeamEffect']
            self.play(music_file=laser_path)
            self.laser_obj.opacity = 150
            self.laser_powers = self.laser_powers - 1
            self.laser_label.text = f'Laser Power: {self.laser_powers}'
        else:
            self.laser_label.color = (237, 145, 33, 255)
            self.laser_label.text = "Laser Power: N/A"
    
    def redraw_ghost(self, dt):
        self.ghost_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/ghost.gif'), 
                                            x=self.ghost_respawn_coord[0], y=self.ghost_respawn_coord[1], batch=self.interface)
        revive_path = self.confObj.toml_dict['music']['ghostReviveEffect']
        self.play(music_file=revive_path)
    def increase_speed(self):
        self.speed = self.speed + 120
    def reset_speed(self, dt):
        self.speed = 120
    def xp_speed(self):
        if self.xp_speedups >= 1:
            self.increase_speed()
            pyglet.clock.schedule_once(self.reset_speed, 30)
            self.xp_speedups = self.xp_speedups - 1
            self.xp_label.text =  f'XP Speedups: {self.xp_speedups}'
            self.play(music_file=self.confObj.toml_dict['music']['xpSpeedUpEffect'])
        else:
            self.xp_label.color = (237, 145, 33, 255)
            self.xp_label.text = "XP Speedups: N/A"
    def magnet(self):
        for food_items in self.food_dict.items():
            coords = food_items[0]
            distance = utilities.coord_distance(coords[0], coords[1], self.eater_sprite.x, self.eater_sprite.y)
            if distance <= 100:
                self.food_dict[self.grid_pos].delete() 
                del self.food_dict[self.grid_pos]      
                
                self.pellets += 1
                self.pellet_label.text = f'Pellets: {self.pellets}'
                
                # Persistence
                self.data_store['pellets'] = self.pellets
                self.data_store.sync()
                         
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
            self.grid_pos = (int((self.eater_sprite.x + 20) // 40), 
                        int((self.eater_sprite.y + 20) // 40))
            
            if self.grid_pos in self.food_dict:
                # Remove pellet and update count
                self.food_dict[self.grid_pos].delete() 
                del self.food_dict[self.grid_pos]      
                
                self.pellets += 1
                self.pellet_label.text = f'Pellets: {self.pellets}'
                
                # Persistence
                self.data_store['pellets'] = self.pellets
                self.data_store.sync()
                
                # Audio
                chomp_path = self.confObj.toml_dict['music']['chompEffect']
                self.play(music_file=chomp_path)
            if self.grid_pos in self.magnet_dict:
                self.magnet_dict[self.grid_pos].delete()
                del self.magnet_dict[self.grid_pos]
                self.magnet()
                
            if self.laser_obj is not None and self.ghost_sprite is not None:
                # Check if the laser's Y-height is within the ghost's top and bottom bounds
                laser_y = self.laser_obj.y
                if self.ghost_sprite.y <= laser_y <= (self.ghost_sprite.y + self.ghost_sprite.height):
                    # Hit detected!
                    self.ghost_sprite.delete() # Properly remove the sprite from the batch
                    self.ghost_sprite = None
                    pyglet.clock.schedule_once(self.redraw_ghost, 30.5)
                    
    def return_batch(self):
        return self.interface
       
    def start_(self):
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        self.play_main_music_file(self)
        # print(repr(self.walls))
        pyglet.app.run()