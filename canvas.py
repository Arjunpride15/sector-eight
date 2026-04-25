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
import random
from typing import NamedTuple

class RandomPosition(NamedTuple):
    xcoord: int
    ycoord: int
    
class SectorEight:
    def __init__(self, window):
        # Basic stuff
        self.WINDOW = window
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
        self.font_list = self.confObj.toml_dict['font']['fontList']
        self.grid_pos = None
        self.ghost_grid_pos = None
        # Pellets!
        self.data_store = shelve.open('game_data')
        self.pellets = self.data_store.get('pellets', 0)
        self.ghost_pellets = self.data_store.get('ghost_pellets', 0)
        # Laser Stuff
        self.laser_powers = 5
        self.ghost_laser_powers = 5
        self.laser_obj = None
        self.ghost_laser_obj = None
        self.xp_speedups = 3
        self.ghost_xp_speedups = 3
        self.walls = list()
        self.direction = (0, 0)  # (dx, dy)
        self.speed = 120 # Pixels per second
        self.ghost_direction = (-1, 0)
        self.ghost_speed = 120
        self.TILE_SIDE = 40
        self.ghost_respawn_coord = [0, 0]
        self.magnet_active = False
        self.magnet_timer = 0.0
        self.ghost_magnet_active = False
        self.ghost_magnet_timer = 0.0
        self.bool_powerup = False
        self.ghost_bool_powerup = False
        self.powerups = 10
        self.ghost_powerups = 10
        self.invisibility = False
        self.ghost_invisibility = False
        self.invisible_powers = 10
        self.ghost_invisible_powers = 10
        self.eater_respawn_x = 0
        self.eater_respawn_y = 0
        self.laser_detection = False
        self.game_active = True
        self.eater_lives = 4
        self.ghost_lives = 4
        self.heart_symbol = "\u2764"
        self.lives_display = self.heart_symbol * self.eater_lives
        self.game_over_music_playing = False
        self.lost = False
        self.restart_button = None
        
              
    def canvas_init(self):
        
        for code in self.map_:
            px, py = self.coord_x * 40, self.coord_y * 40
            
            if code == 'wall':
                s = pyglet.sprite.Sprite(img=pyglet.resource.image('images/tile.png'), 
                                        x=px, y=py, batch=self.interface)
                self.walls.append(s)
            elif code == 'blacktile':
                s = pyglet.sprite.Sprite(img=pyglet.resource.image('images/blacktile.png'), 
                                        x=px, y=py, batch=self.interface)
                
            elif code == 'food':
                self.food_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/pellet.png'), 
                                                    x=px, y=py, batch=self.interface)
                self.food_dict[(self.coord_x, self.coord_y)] = self.food_sprite
            elif code == 'ghost':
                self.ghost_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/ghost.png'), 
                                            x=px, y=py, batch=self.interface)
                self.ghost_respawn_coord[0] = self.ghost_sprite.x
                self.ghost_respawn_coord[1] = self.ghost_sprite.y
                
            elif code == 'eater':
                self.eater_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/eater.png'), 
                                                        x=px, y=py, batch=self.interface)
            elif code == 'magnet':
                self.magnet_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/magnet.png'), 
                                                    x=px, y=py, batch=self.interface)
                self.magnet_dict[(self.coord_x, self.coord_y)] = self.magnet_sprite
            
            # Handle coordinate movement
            if code == 'newline':
                self.coord_x = 0
                self.coord_y += 1
            else:
                # Increment X for EVERYTHING that isn't a newline
                self.coord_x += 1
        self.translucent_layer = pyglet.shapes.Rectangle(x=0, y=0, width=self.WINDOW.width, height=self.WINDOW.height, \
                                                         color=(0, 0, 0),batch=self.interface)
        self.translucent_layer.opacity = 0 
        # HUD Labels initialized once to prevent stacking
        self.pellet_label = pyglet.text.Label('', font_name=self.font_list, font_size=18, x=20, y=800, batch=self.interface, color=(253, 189, 1, 255))
        self.laser_label = pyglet.text.Label('', font_name=self.font_list, font_size=18, x=210, y=800, batch=self.interface, color=(57, 255, 20, 255))
        self.xp_label = pyglet.text.Label('', font_name=self.font_list, font_size=18, x=420, y=800, batch=self.interface, color=(127, 235, 232, 255))
        self.powerup_label = pyglet.text.Label('', font_name=self.font_list, font_size=18, x=630, y=800, batch=self.interface, color=(254, 1, 154, 255))
        self.invisible_power_label = pyglet.text.Label('', font_name=self.font_list, font_size=18, x=820, y=800, batch=self.interface, color=(138, 0, 255, 255))
        self.life_label = pyglet.text.Label('', font_name=self.font_list, font_size=18, x=1120, y=800, batch=self.interface, color=(255, 0, 102, 255))

        self.translucent_layer = pyglet.shapes.Rectangle(x=0, y=0, width=self.WINDOW.width, height=self.WINDOW.height, 
                                                         color=(0, 0, 0), batch=self.interface)
        self.translucent_layer.opacity = 0
                        
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
        if not self.ghost_invisibility:
            if self.laser_powers >= 1 and self.eater_sprite:
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
        self.ghost_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/ghost.png'), 
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
        # 1. Identify which pellets are within range
        # We use a list to store keys because we cannot delete from the dict while iterating over it
        to_remove = []
        
        # Define the pixel-based center of the player
        player_x = self.eater_sprite.x
        player_y = self.eater_sprite.y

        for grid_coords, sprite in self.food_dict.items():
            # Convert grid coordinates to pixels for an accurate distance check
            # We multiply by TILE_SIDE (40) to match the sprite's position
            pellet_pixel_x = grid_coords[0] * self.TILE_SIDE
            pellet_pixel_y = grid_coords[1] * self.TILE_SIDE
            
            # Calculate distance using your utility function
            distance = utilities.coord_distance(pellet_pixel_x, pellet_pixel_y, player_x, player_y)
            
            if distance <= 175:
                to_remove.append(grid_coords)

        # 2. Process the identified pellets
        if to_remove:
            for coords in to_remove:
                # Properly delete the sprite from the Pyglet batch
                self.food_dict[coords].delete()
                # Remove from the dictionary
                del self.food_dict[coords]
                
                # Increment pellet count
                self.pellets += 1
            
            # 3. Update UI and Persistence once after the loop for efficiency
            self.pellet_label.text = f'Pellets: {self.pellets}'
            self.data_store['pellets'] = self.pellets
            self.data_store.sync()
            
            pickup_path = self.confObj.toml_dict['music']['magnetPickupEffect']
            self.play(music_file=pickup_path)
    def powerup_on(self):        
        self.bool_powerup = True
                     
    def powerup_off(self, dt):
        self.bool_powerup = False
    def powerup(self):
        if self.powerups >= 1:
            self.powerup_on()
            pyglet.clock.schedule_once(self.powerup_off, 0.6)
            self.powerups = self.powerups - 1
            self.powerup_label.text = f'Powerups: {self.powerups}'
            self.play(music_file=self.confObj.toml_dict['music']['powerUpEffect'])
        else:
            
            self.powerup_label.color = (237, 145, 33, 255)
            self.powerup_label.text = 'Powerups: N/A'         
     
    def invisible_on(self):
        self.eater_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/invisible-eater.png'), 
                                                        x=self.eater_sprite.x, y=self.eater_sprite.y, batch=self.interface)
        self.invisibility = True
    def invisible_off(self, dt):
        self.eater_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/eater.png'), 
                                                        x=self.eater_sprite.x, y=self.eater_sprite.y, batch=self.interface)
        self.invisibility = False
    def invisible_power(self):
        if self.invisible_powers >= 1:
            self.invisible_on()
            pyglet.clock.schedule_once(self.invisible_off, 45.0)
            self.invisible_powers = self.invisible_powers - 1
            self.invisible_power_label.text = f'Invisible Power: {self.invisible_powers}'
            self.play(music_file=self.confObj.toml_dict['music']['invisibleEffect'])
        else:
            self.invisible_power_label.color =  (237, 145, 33, 255)
            self.invisible_power_label.text = 'Invisible Power: N/A'
    def blit_random_coin(self, dt):
        # 1. Generate a random GRID position
        grid_x = random.randint(0, 39)
        grid_y = random.randint(0, 19)
        pixel_x = grid_x * self.TILE_SIDE
        pixel_y = grid_y * self.TILE_SIDE

        # 2. Check if this pixel position hits any wall
        hit_wall = False
        for wall_obj in self.walls:
            if (pixel_x < wall_obj.x + wall_obj.width and
                pixel_x + self.TILE_SIDE > wall_obj.x and
                pixel_y < wall_obj.y + wall_obj.height and
                pixel_y + self.TILE_SIDE > wall_obj.y):
                hit_wall = True
                break
        
        # 3. If it's a clear spot, spawn the coin
        if not hit_wall:
            new_coin = pyglet.sprite.Sprite(
                img=pyglet.resource.image('images/pellet.png'), # or coin.png
                x=pixel_x, 
                y=pixel_y, 
                batch=self.interface
            )
            
            # USE GRID COORDINATES FOR THE DICTIONARY KEY
            # This matches how self.grid_pos is calculated in update()
            self.food_dict[(grid_x, grid_y)] = new_coin
    def update_labels(self):
        # Update text of existing labels
        self.pellet_label.text = f'Pellets: {self.pellets:,}'
        self.laser_label.text = f'Laser Power: {self.laser_powers}'
        self.xp_label.text = f'XP Speedups: {self.xp_speedups}'
        self.powerup_label.text = f'Powerups: {self.powerups}'
        self.invisible_power_label.text = f'Invisible Power: {self.invisible_powers}'
        self.life_label.text = self.heart_symbol * self.eater_lives   
                
                
            
                       
    def update(self, dt):
        collision = False
        self.update_labels()
        
        if self.eater_sprite:
            # 1. Calculate the potential new position
            new_x = self.eater_sprite.x + (self.direction[0] * self.speed * dt)
            new_y = self.eater_sprite.y + (self.direction[1] * self.speed * dt)
            if not self.bool_powerup:
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
                self.eater_sprite.x = round(new_x)
                self.eater_sprite.y = round(new_y)

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
                # Remove the magnet item from the map
                self.magnet_dict[self.grid_pos].delete()
                del self.magnet_dict[self.grid_pos]
                
                # Activate the 60-second power-up
                self.magnet_active = True
                self.magnet_timer = 60.0 
                
                # Play a pickup sound
                pickup_sound = self.confObj.toml_dict['music'].get('magicEffect')
                if pickup_sound:
                    self.play(music_file=pickup_sound)
                
            if self.laser_obj is not None and self.ghost_sprite is not None:
                # Check if the laser's Y-height is within the ghost's top and bottom bounds
                laser_y = self.laser_obj.y
                if self.ghost_sprite.y <= laser_y <= (self.ghost_sprite.y + self.ghost_sprite.height):
                    # Hit detected!
                    self.ghost_sprite.delete() # Properly remove the sprite from the batch
                    self.ghost_sprite = None
                    self.ghost_lives = self.ghost_lives - 1
                    pyglet.clock.schedule_once(self.redraw_ghost, 30.5)
            if self.magnet_active:
                self.magnet_timer -= dt
                # Run the magnet suction logic every frame while active
                self.magnet()
                
                # Check if time has run out
                if self.magnet_timer <= 0:
                    self.magnet_active = False
                    self.magnet_timer = 0
                    self.play(music_file=self.confObj.toml_dict['music']['magnetLosingEffect']) 

    def ghost_laser(self):
        if not self.invisibility:
            if self.ghost_laser_powers >= 1 and self.ghost_sprite is not None and self.eater_sprite is not None:
                self.ghost_laser_obj = shapes.Line(0, self.ghost_sprite.y + (self.TILE_SIDE / 2), 1600, \
                                            self.ghost_sprite.y + (self.TILE_SIDE / 2), \
                                            thickness=4, color=(240, 0, 25), batch=self.interface)
                laser_path = self.confObj.toml_dict['music']['laserBeamEffect']
                self.play(music_file=laser_path)
                self.ghost_laser_obj.opacity = 150
                self.ghost_laser_powers = self.ghost_laser_powers - 1
                
            
    
    def redraw_eater(self, dt):
        self.eater_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/eater.png'), 
                                            x=self.eater_respawn_x, y=self.eater_respawn_y, batch=self.interface)
        revive_path = self.confObj.toml_dict['music']['ghostReviveEffect']
        self.play(music_file=revive_path)
    def ghost_increase_speed(self):
        self.ghost_speed = self.ghost_speed + 120
    def ghost_reset_speed(self, dt):
        self.ghost_speed = 120
    def ghost_xp_speed(self):
        if self.ghost_xp_speedups >= 1:
            self.ghost_increase_speed()
            pyglet.clock.schedule_once(self.ghost_reset_speed, 30)
            self.ghost_xp_speedups = self.ghost_xp_speedups - 1
            self.play(music_file=self.confObj.toml_dict['music']['xpSpeedUpEffect'])
        
    def ghost_magnet(self):
        # 1. Identify which pellets are within range
        # We use a list to store keys because we cannot delete from the dict while iterating over it
        to_remove = []
        
       
        ghost_x = self.ghost_sprite.x
        ghost_y = self.ghost_sprite.y

        for grid_coords, sprite in self.food_dict.items():
            # Convert grid coordinates to pixels for an accurate distance check
            # We multiply by TILE_SIDE (40) to match the sprite's position
            pellet_pixel_x = grid_coords[0] * self.TILE_SIDE
            pellet_pixel_y = grid_coords[1] * self.TILE_SIDE
            
            # Calculate distance using your utility function
            distance = utilities.coord_distance(pellet_pixel_x, pellet_pixel_y, ghost_x, ghost_y)
            
            if distance <= 175:
                to_remove.append(grid_coords)

        # 2. Process the identified pellets
        if to_remove:
            for coords in to_remove:
                # Properly delete the sprite from the Pyglet batch
                self.food_dict[coords].delete()
                # Remove from the dictionary
                del self.food_dict[coords]
                
                # Increment pellet count
                self.ghost_pellets += 1
            
            
            self.data_store['ghost_pellets'] = self.ghost_pellets
            self.data_store.sync()
            
            pickup_path = self.confObj.toml_dict['music']['magnetPickupEffect']
            self.play(music_file=pickup_path)
    def ghost_powerup_on(self):        
        self.ghost_bool_powerup = True
                     
    def ghost_powerup_off(self, dt):
        self.ghost_bool_powerup = False
    def ghost_powerup(self):
        if self.ghost_powerups >= 1:
            self.ghost_powerup_on()
            pyglet.clock.schedule_once(self.ghost_powerup_off, 0.6)
            self.ghost_powerups = self.ghost_powerups - 1
            self.play(music_file=self.confObj.toml_dict['music']['powerUpEffect'])
                 
     
    def ghost_invisible_on(self):
        self.ghost_sprite.opacity = 50
        self.ghost_invisibility = True
    def ghost_invisible_off(self, dt):
        self.ghost_sprite.opacity = 50
        self.ghost_invisibility = False
    def ghost_invisible_power(self):
        if self.ghost_invisible_powers >= 1:
            self.ghost_invisible_on()
            pyglet.clock.schedule_once(self.ghost_invisible_off, 45.0)
            self.ghost_invisible_powers = self.ghost_invisible_powers - 1
            
            self.play(music_file=self.confObj.toml_dict['music']['invisibleEffect'])
        
                           
    def ghost_update(self, dt):
        collision = False
        #self.wanderer()
        if self.ghost_sprite:
            # 1. Calculate the potential new position
            new_x = self.ghost_sprite.x + (self.ghost_direction[0] * self.ghost_speed * dt)
            new_y = self.ghost_sprite.y + (self.ghost_direction[1] * self.ghost_speed * dt)
            if not self.ghost_bool_powerup:
                # 2. Collision Leeway (Hitbox Shrinking)
                # We subtract a few pixels from the edges so the eater 'fits' better
                padding = 6 
                
                collision = False
                for wall in self.walls:
                    # Check overlap with padding applied to the eater's box
                    if (new_x + padding < wall.x + wall.width and
                        new_x + self.ghost_sprite.width - padding > wall.x and
                        new_y + padding < wall.y + wall.height and
                        new_y + self.ghost_sprite.height - padding > wall.y):
                        collision = True
                        
                        break

            # 3. Apply movement if clear
            if not collision:
                self.ghost_sprite.x = round(new_x)
                self.ghost_sprite.y = round(new_y)

            # 4. Pellet Detection (Your original logic)
            # We use +20 to check the 'tile' the eater is mostly over
            self.ghost_grid_pos = (int((self.ghost_sprite.x + 20) // 40), 
                        int((self.ghost_sprite.y + 20) // 40))
            new_x = self.ghost_sprite.x + (self.ghost_direction[0] * self.ghost_speed * dt)
            if self.ghost_grid_pos in self.food_dict:
                # Remove pellet and update count
                self.food_dict[self.ghost_grid_pos].delete() 
                del self.food_dict[self.ghost_grid_pos]      
                
                self.ghost_pellets += 1
                
                
                # Persistence
                self.data_store['ghost_pellets'] = self.ghost_pellets
                self.data_store.sync()
                
                # Audio
                chomp_path = self.confObj.toml_dict['music']['chompEffect']
                self.play(music_file=chomp_path)
            
            if self.ghost_grid_pos in self.magnet_dict:
                # Remove the magnet item from the map
                self.magnet_dict[self.ghost_grid_pos].delete()
                del self.magnet_dict[self.ghost_grid_pos]
                
                # Activate the 60-second power-up
                self.ghost_magnet_active = True
                self.ghost_magnet_timer = 60.0 
                
                # Play a pickup sound
                pickup_sound = self.confObj.toml_dict['music'].get('magicEffect')
                if pickup_sound:
                    self.play(music_file=pickup_sound)
                
            if self.ghost_laser_obj is not None and self.eater_sprite is not None:
                
                laser_y = self.ghost_laser_obj.y
                if self.eater_sprite.y <= laser_y <= (self.eater_sprite.y + self.eater_sprite.height):
                    self.eater_respawn_x = self.eater_sprite.x
                    self.eater_respawn_y = self.eater_sprite.y
                    # Hit detected!
                    self.eater_sprite.delete() # Properly remove the sprite from the batch
                    self.eater_sprite = None
                    self.eater_lives = self.eater_lives - 1
                    pyglet.clock.schedule_once(self.redraw_eater, 10)
            if self.ghost_magnet_active:
                self.ghost_magnet_timer -= dt
                # Run the magnet suction logic every frame while active
                self.ghost_magnet()
                
                # Check if time has run out
                if self.ghost_magnet_timer <= 0:
                    self.ghost_magnet_active = False
                    self.ghost_magnet_timer = 0
                    self.play(music_file=self.confObj.toml_dict['music']['magnetLosingEffect'])
    def no_laser(self, dt):
        self.ghost_laser_obj = None
    def reset_detection(self, dt):
        self.laser_detection = False
    def wanderer(self, dt):
        if self.ghost_sprite:
            # 1. Wall Detection (Decision only)
            # We look ahead to see if we are ABOUT to hit a wall
            dx, dy = self.ghost_direction
            predict_x = self.ghost_sprite.x + (dx * 5) 
            predict_y = self.ghost_sprite.y + (dy * 5)
            
            hit_wall = False
            for wall in self.walls:
                if (predict_x < wall.x + wall.width and predict_x + 34 > wall.x and
                    predict_y < wall.y + wall.height and predict_y + 34 > wall.y):
                    hit_wall = True
                    break
                    
            if hit_wall:
                # Pick a new direction
                self.ghost_direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            
            # 2. Random Power Activation (Wanderer Specifics)
            if not self.ghost_magnet_active and random.random() < 0.005: 
                self.ghost_magnet_active = True
                self.ghost_magnet_timer = 10.0 

            # 3. Laser Logic (1-second delay check)
            # We only schedule if the player is in sight AND a laser isn't already firing
            if self.eater_sprite:
                if self.ghost_laser_obj is None:
                    if abs(self.ghost_sprite.y - self.eater_sprite.y) < 15:
                        if not self.invisibility:
                            self.laser_detection = True
                            pyglet.clock.schedule_once(self.reset_detection, 0.55)
                    
    
    def chaser(self, dt):
        if self.ghost_sprite and self.eater_sprite:
            # 1. Use a Deadzone to prevent oscillation
            # Only change direction if the distance is greater than 5 pixels
            diff_x = self.eater_sprite.x - self.ghost_sprite.x
            diff_y = self.eater_sprite.y - self.ghost_sprite.y
            deadzone = 5

            if abs(diff_x) > deadzone:
                self.ghost_direction = (1, 0) if diff_x > 0 else (-1, 0)
            elif abs(diff_y) > deadzone:
                self.ghost_direction = (0, 1) if diff_y > 0 else (0, -1)

            # 2. XP Speedup Usage
            # Chasers use speedups when far away to catch the eater
            dist = utilities.coord_distance(
                self.ghost_sprite.x, self.ghost_sprite.y, 
                self.eater_sprite.x, self.eater_sprite.y
            )
            
            if dist > 300 and self.ghost_xp_speedups >= 1:
                # Ghost doubles its speed for 30 seconds
                self.ghost_xp_speed()

            # 3. Aggressive Sniping
            # Detection triggers the 1-second delay logic
            if abs(self.ghost_sprite.y - self.eater_sprite.y) < 15:
                # The self.invisibility check allows the eater to 'sneak'
                if not self.invisibility:
                    self.laser_detection = True
                    pyglet.clock.schedule_once(self.reset_detection, 0.55)
                    
    def ambusher(self, dt):
        if self.ghost_sprite and self.eater_sprite:
            # 1. Distance check for tactical positioning
            dist_to_player = utilities.coord_distance(
                self.ghost_sprite.x, self.ghost_sprite.y, 
                self.eater_sprite.x, self.eater_sprite.y
            )

            # 2. Hiding Behavior: If far away, stop and vanish 
            if dist_to_player > 400:
                self.ghost_direction = (0, 0) # Stop in a 'box'
                if not self.ghost_invisibility and self.ghost_invisible_powers >= 1:
                    self.ghost_invisible_power()
            else:
                # 3. Sudden Strike: If player approaches, activate movement 
                if self.ghost_direction == (0, 0):
                    self.ghost_direction = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                
                # Use Powerups to surprise the player 
                if not self.ghost_bool_powerup and self.ghost_powerups >= 1:
                    self.ghost_powerup()

            # 4. Sudden Laser Detection 
            # Ambusher has a slightly wider detection window for 'sudden' firing
            if abs(self.ghost_sprite.y - self.eater_sprite.y) < 20:
                if not self.invisibility: # Keeping your stealth mechanic 
                    self.laser_detection = True
                    pyglet.clock.schedule_once(self.reset_detection, 0.55)
    def timid(self, dt):
        if self.ghost_sprite and self.eater_sprite:
            # 1. Calculate distance to the player
            player_dist = utilities.coord_distance(
                self.ghost_sprite.x, self.ghost_sprite.y, 
                self.eater_sprite.x, self.eater_sprite.y
            )

            # 2. Shy Reaction: If player is within 250 pixels, run away
            if player_dist < 250:
                # Trigger invisibility to 'hide' while fleeing
                if not self.ghost_invisibility and self.ghost_invisible_powers >= 1:
                    self.ghost_invisible_power()

                # Determine flee direction based on player's relative position
                if abs(self.eater_sprite.x - self.ghost_sprite.x) > abs(self.eater_sprite.y - self.ghost_sprite.y):
                    # Player is further away horizontally, so flee horizontally
                    self.ghost_direction = (1, 0) if self.eater_sprite.x < self.ghost_sprite.x else (-1, 0)
                else:
                    # Player is further away vertically, so flee vertically
                    self.ghost_direction = (0, 1) if self.eater_sprite.y < self.ghost_sprite.y else (0, -1)
                    
            else:
                # 3. If safe, try to 'hide' in a corner or stop moving
                if random.random() < 0.01: 
                    self.ghost_direction = (0, 0) # Stop and hide
                elif self.ghost_direction == (0, 0) and random.random() < 0.05:
                    # Occasionally start moving again to find a new hiding spot
                    self.ghost_direction = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
            if self.eater_sprite:
                    if self.ghost_laser_obj is None:
                        if abs(self.ghost_sprite.y - self.eater_sprite.y) < 15:
                            if not self.invisibility:
                                self.laser_detection = True
                                pyglet.clock.schedule_once(self.reset_detection, 0.55)
                
    def change_personality(self, dt):
        self.laser_detection = False
        personalities = [self.wanderer, 
                         self.timid, 
                         self.chaser, 
                         self.ambusher
                         ]
        for item in personalities:
            try:
                pyglet.clock.unschedule(item)
            except Exception:
                continue
        random_personality = random.choice(personalities)
        pyglet.clock.schedule_interval(random_personality, 1/60)
    def fire_laser(self, dt):
        if self.laser_detection:
            pyglet.clock.schedule_once(lambda dt: self.ghost_laser(), 1.0)
            pyglet.clock.schedule_once(self.no_laser, 1.5)
            
                    
    def return_batch(self):
        return self.interface
    def you_won(self):
        if not self.game_over_music_playing:
            self.game_over_music_playing = True
            self.stop_music()
            winsound.PlaySound(self.confObj.toml_dict['music']['victory'], winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
            
            self.win_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/you-won.png'), x=112, y=200, batch=self.interface)
            self.win_sprite.opacity = 255
            self.restart_button = utilities.Button('Restart', (self.WINDOW.width // 2) - (75), 100, 150, 50, self.interface, (57, 20, 255, 200))

    def you_lost(self):
        if not self.game_over_music_playing:
            self.game_over_music_playing = True
            self.stop_music()
            winsound.PlaySound(self.confObj.toml_dict['music']['lose'], winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
            
            self.lost_sprite = pyglet.sprite.Sprite(img=pyglet.resource.image('images/you-lost.png'), x=112, y=200, batch=self.interface)
            self.lost_sprite.opacity = 255
            self.restart_button = utilities.Button('Restart', (self.WINDOW.width // 2) - (75), 100, 150, 50, self.interface, (57, 20, 255, 200))
    def check_state(self, dt):
        if not self.game_active:
            return

        if self.ghost_lives == 0 or (self.food_dict == {} and self.pellets > self.ghost_pellets):
            self.game_active = False
            self.game_paused = True
            self.you_won()
            self.translucent_layer.opacity = 100
            self.translucent_layer.color = (57, 255, 20) # Green

        elif self.eater_lives == 1:
            self.translucent_layer.opacity = 60
            self.translucent_layer.color = (237, 145, 33) # Orange

        elif self.eater_lives == 0:
            self.game_active = False
            self.game_paused = True
            self.you_lost()
            self.translucent_layer.opacity = 128
            self.translucent_layer.color = (255, 20, 60) # Red
    def restart_game(self):
        print('button clicked')
    def start_(self):
        # Enable Blending for transparency
        import pyglet.gl as gl
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        self.canvas_init()
        self.change_personality(1)
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.clock.schedule_interval(self.ghost_update, 1/60.0)
        pyglet.clock.schedule_interval(self.fire_laser, 2.0)
        pyglet.clock.schedule_interval(self.change_personality, 30.0)
        pyglet.clock.schedule_interval(self.blit_random_coin, 30)
        pyglet.clock.schedule_interval(self.check_state, 1/60)
        self.play_main_music_file(self)
        pyglet.app.run()