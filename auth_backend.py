import winsound
import miniaudio
import utilities
import pyglet
from pyglet.window import key, mouse
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
        self.register_btn = None
        self.font_list = self.configObj.toml_dict['font']['fontList']
        self.next_btn = None
        
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
    
    def _handle_mouse_press(self, x, y, button, modifiers):
        if self.loading_done:
            #print(x, y, button, modifiers)
            if button == mouse.LEFT:
                if self.log_in_btn.is_clicked(x, y):
                    self.handle_opt_btn_resize_order(type_="Log In")
                    self.draw_log_in_page()
                    
                    
                if self.register_btn.is_clicked(x, y):
                    self.handle_opt_btn_resize_order(type_="Register")
                    self.draw_register_page()
                
                if self.text_box.text != "":
                    if self.next_btn.is_clicked(x, y):
                        self.basic_handle_next()
    
    def draw_log_in_page(self):
        self.text_box.set_visible(True)
        self.next_btn.set_visible(True)

    def draw_register_page(self):
        self.text_box.set_visible(True)
        self.next_btn.set_visible(True)
    
    def basic_handle_next(self):
        print(self.text_box.text)
        
    def handle_opt_btn_resize_order(self, type_):
        # First set all Welcome page elements' opacity
        # to zero
        self.welcome_label.visible = False
        self.log_in_btn.set_visible(False)
        self.register_btn.set_visible(False)
        
        # Now resize self.main_card and change x & y
        # to center it properly
        self.main_card.width = 910
        self.main_card.height = 350
        self.main_card.x = 20
        self.main_card.y = 350
        
        # Now change the coordinates, opacity, font stuff and text of 
        # self.welcome_label!
        self.welcome_label.x = self.main_card.x + 30
        self.welcome_label.y = self.main_card.y + self.main_card.height - 70
        self.welcome_label.text = type_
        self.welcome_label.font_size = 50
        self.welcome_label.font_name = self.font_list
        self.welcome_label.visible = True
        
    def init_window(self):
        self.show_loading_screen()
        pyglet.clock.schedule_once(self.hide_loading_screen, 2)
        pyglet.clock.schedule_once(self.main_init_window, 2)
        
    def main_init_window(self, dt):
        
        
        self.main_card = pyglet.shapes.RoundedRectangle(x=200, y=10, width=550, height=880, radius=18,
                                                        color=(228, 233, 239, 255), batch=self.interface)
        self.text_box = utilities.TextBox(520, 500, 300, 40, self.interface, 
                                          text_color=(30, 30, 100, 255), bg_color=self.main_card.color,
                                          placeholder="Enter your username")
        self.text_box.set_visible(False)
        self.welcome_label = pyglet.text.Label(text="Welcome!", x=self.main_card.x + 135, y=800, 
                                               color=(24, 28, 81, 255), batch=self.interface,
                                               font_name="Open Sans", font_size=50)
        self.log_in_btn = utilities.Button("Log In", self.welcome_label.x, self.welcome_label.y - 200,
                                            width=300, height=50, batch=self.interface, colour=(26, 115, 232),
                                            font_name="Open Sans")
        self.register_btn = utilities.Button("Register", self.log_in_btn.x, self.log_in_btn.y - 150,
                                            width=300, height=50, batch=self.interface, colour=(255, 215, 0),
                                            font_name="Open Sans", text_color=(30, 30, 30, 255))
        self.next_btn = utilities.Button("Next", self.text_box.x + 300, self.text_box.y - 140,
                                         width=100, height=40, batch=self.interface,
                                         colour=(0, 245, 190), text_color=(20, 20, 30))
        self.next_btn.set_visible(False)
        self.loading_done = True
    def update(self, dt):
        if self.text_box:
            if len(self.text_box.text) > 20:
                self.text_box.typing_disabled = True
            else:
                self.text_box.typing_disabled = False
            #print(self.text_box.text)
        
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()
        
        
        