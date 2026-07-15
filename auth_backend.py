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
        self.text_box = None
        self.main_card = None
        self.welcome_label = None
        self.log_in_btn = None
        self.log_up_btn = None
        
    def play(self, music_file=None):
        
        if music_file == None:
            if not self.music_switch:
                winsound.PlaySound(self.configObj.toml_dict['music']['authBackground'], 
                                    winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                                    
        else:
            device = miniaudio.PlaybackDevice()
            stream = miniaudio.stream_file(music_file)
            device.start(stream)
        
            
    def stop_music(self):
        winsound.PlaySound(None, winsound.SND_FILENAME)
        self.music_switch = False
    
    def show_loading_screen(self):
        self.loading_txt.opacity = 255
        
    def hide_loading_screen(self, dt):
        self.loading_txt.opacity = 0
        
    def init_window(self):
        self.show_loading_screen()
        pyglet.clock.schedule_once(self.hide_loading_screen, 2)
        pyglet.clock.schedule_once(self.main_init_window, 2)
        
    def main_init_window(self, dt):
        #self.text_box = utilities.TextBox(10, 10, 300, 40, self.interface, masked=True)
        self.main_card = pyglet.shapes.RoundedRectangle(x=200, y=10, width=550, height=880, radius=18,
                                                        color=(228, 233, 239, 255), batch=self.interface)
        self.welcome_label = pyglet.text.Label(text="Welcome!", x=self.main_card.x + 135, y=800, 
                                               color=(24, 28, 81, 255), batch=self.interface,
                                               font_name="Open Sans", font_size=50)
        self.log_in_btn = utilities.Button("Log In", self.welcome_label.x, self.welcome_label.y - 200,
                                            width=300, height=50, batch=self.interface, colour=(26, 115, 232),
                                            font_name="Open Sans")
        self.log_up_btn = utilities.Button("Register", self.log_in_btn.x, self.log_in_btn.y - 150,
                                            width=300, height=50, batch=self.interface, colour=(255, 215, 0),
                                            font_name="Open Sans", text_color=(30, 30, 30, 255))
    def update(self, dt):
        if self.text_box:
            ...
            #print(self.text_box.text)
        
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()
        
        
        