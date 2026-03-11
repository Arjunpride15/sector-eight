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
                    
                    device = miniaudio.PlaybackDevice()
                    # Use the loop=True parameter here
                    main_stream = miniaudio.stream_file(self.main_music_file)
                    device.start(main_stream)
                    self.music_switch = True                    
            else:
                # For custom music files passed via kwargs
                device = miniaudio.PlaybackDevice()
                stream = miniaudio.stream_file(kwargs['music_file'])
                device.start(stream)
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
            # 1. Calculate the potential new position based on speed and direction 
            new_x = self.eater_sprite.x + (self.direction[0] * self.speed * dt)
            new_y = self.eater_sprite.y + (self.direction[1] * self.speed * dt)
            
            # 2. Check for wall collisions BEFORE moving 
            collision = False
            for wall in self.walls:
                # Check if the eater's new bounding box overlaps with the wall 
                if (new_x < wall.x + wall.width and
                    new_x + self.eater_sprite.width > wall.x and
                    new_y < wall.y + wall.height and
                    new_y + self.eater_sprite.height > wall.y):
                    collision = True
                    break  # Stop checking once a collision is found

            # 3. Only update position if the path is clear
            if not collision:
                self.eater_sprite.x = new_x
                self.eater_sprite.y = new_y

            # 4. Check for food collision (existing logic) 
            grid_pos = (int(self.eater_sprite.x // 40), int(self.eater_sprite.y // 40))
            if grid_pos in self.food_dict:
                self.food_dict[grid_pos].delete() 
                del self.food_dict[grid_pos]      
                # Note: Using self.play() here is cleaner than self.__class__.play(self, ...)
                self.play(music_file=self.confObj.toml_dict['music']['chompEffect'])
    
    def return_batch(self):
        return self.interface    
    def start_(self):
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.clock.schedule_interval(self.play_main_music_file, 43/60.0)
        pyglet.app.run()