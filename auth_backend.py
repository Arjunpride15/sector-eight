import winsound
import miniaudio
import utilities
import pyglet
import conf
import shelve
from subprocess import Popen
from canvas import NotImplementedWarning
from typing import NamedTuple, Iterable
import random
import tastyerrors
import datetime, time
import pyglet.shapes

class SectorEightAuthManager:
    def __init__(self, window):
        self.window = window
        self.interface = pyglet.graphics.Batch()
        self.data_storage = shelve.open("data\\game_data")
        self.auth_db = shelve.open("data\\auth_db")
        pyglet.options['search_local_libs'] = True
        pyglet.font.add_file('fonts/OpenSans-Regular.ttf')
        self.configObj = conf.Config()
        self.music_switch = False
        self.loading_txt = pyglet.text.Label("Sector Eight \n \tAuthentication Manager",
                                             x=50, y=(self.window.height // 2) - 50,
                                             multiline=True, font_size=50, 
                                             color=(255, 255, 255), font_name="Open Sans",
                                             batch=self.interface, width=600)
        self.loading_txt.opacity = 0
        self.loading_done = False
    
    def play(self, **kwargs):
        try:
            if not kwargs:
                if not self.music_switch:
                    winsound.PlaySound(self.configObj.toml_dict['music']['authBackground'], 
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
    def increase_intro_txt_opacity(self,dt):
        if self.loading_txt.opacity <= 255:
            self.loading_txt.opacity += 4.25
    def decrease_intro_txt_opacity(self,dt):
        if self.loading_txt.opacity >= 0:
            self.loading_txt.opacity -= 4.25
    def set_loading_as_done(self, dt):
        self.loading_done = True
    def show_loading_screen(self):
        pyglet.clock.schedule_interval_for_duration(self.increase_intro_txt_opacity, 1/60, 2)
    def hide_loading_screen(self, dt):
        
        pyglet.clock.schedule_interval_for_duration(self.decrease_intro_txt_opacity, 1/60, 2)
        pyglet.clock.schedule_once(self.set_loading_as_done, 2)
    def main_init_window(self):
        self.show_loading_screen()
        pyglet.clock.schedule_once(self.hide_loading_screen, 2)
    
    def update(self, dt):
        if self.loading_done == True:
            self.loading_txt.opacity = 0
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()
        
        
        