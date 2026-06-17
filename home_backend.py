import winsound
import miniaudio
import utilities
import pyglet
import conf
import shelve
from subprocess import Popen
from canvas import NotImplementedWarning
from typing import NamedTuple
import random
import tastyerrors
import datetime, time
import pyglet.shapes

class SectorEightHome:
    def __init__(self, window):
        self.window = window
        self.scroll_objects = list()
        self.interface = pyglet.graphics.Batch()
        self.configObj = conf.Config()
        pyglet.options['search_local_libs'] = True
        pyglet.font.add_file('fonts/OpenSans-Regular.ttf')
        self.main_items = list()
        self.data_storage = shelve.open('data\\game_data')
        self.log_file = shelve.open(r"data\purchases")
        self.pellets = self.data_storage.get('pellets', 0)
        self.music_switch = False
        self.loading_screen = pyglet.sprite.Sprite(img=pyglet.resource.image('images/loading.png'), 
                                        x=0, y=311, batch=self.interface)
        self.loading_screen.opacity = 0
        self.pellet_label = None
        self.welcome_label = None
        self.vruler = None
        self.ruler = None
        self.side_panel_btn = None
        self.background = (51, 51, 89, 255)
        self.num_side_btn_clicked = 0
        
    def sync_data(self, name, var):
        self.data_storage[name] = var
        self.data_storage.sync()
    
    def play(self, **kwargs):
        try:
            if not kwargs:
                if not self.music_switch:
                    winsound.PlaySound(self.configObj.toml_dict['music']['homeBackground'], 
                                       winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                                       
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
    def show_loading_screen(self, dt):
        self.loading_screen.opacity = 255
        
    def hide_loading_screen(self, dt):
        self.loading_screen.opacity = 0
        self.main_init_window()
    def toggle_side_panel(self):
        if self.num_side_btn_clicked % 2 == 0:
            print("Showing side panel")
            self.num_side_btn_clicked += 1
        else:
            print("Hiding side panel")
            self.num_side_btn_clicked += 1
    def init_window(self):
        pyglet.clock.schedule_interval_for_duration(self.show_loading_screen, 1/60, 2.4)
        pyglet.clock.schedule_once(self.hide_loading_screen, 2.4)
    
    def main_init_window(self):
        self.welcome_label = pyglet.text.Label(f'Welcome!', 
                                              font_name="Open Sans", 
                                              font_size=20,
                                              x=100, 
                                              y=740, 
                                              batch=self.interface, 
                                              color=(255, 255, 255, 255))
        
        self.pellet_label = pyglet.text.Label(f'\N{COIN}: {self.pellets}', 
                                              font_name="Open Sans", 
                                              font_size=20,
                                              x=83 + self.welcome_label.x + 200, 
                                              y=740, 
                                              batch=self.interface, 
                                              color=(253, 189, 1, 255))
        vruler_x = self.welcome_label.x - 20
        self.vruler = pyglet.shapes.Line(x=vruler_x, y=0,
                                         x2=vruler_x, y2=self.window.height,
                                         thickness=1.6, color=(255, 255, 255, 255), batch=self.interface)
        ruler_y = self.welcome_label.y - 20
        self.ruler = pyglet.shapes.Line(x=0, y=ruler_y, x2=self.window.width, y2=ruler_y,
                                        thickness=1.6, color=(255, 255, 255, 255), batch=self.interface)
        
        self.side_panel_btn = utilities.Button("\u2630", 10, self.ruler.y + 20, 50, 50, self.interface,
                                               self.background, font_name="Open Sans", font_size=35)
        
    def update(self, dt):
        ...
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()          