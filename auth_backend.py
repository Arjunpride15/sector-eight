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
from argon2 import PasswordHasher
from session_manager import SessionManager

class SectorEightAuthManager:
    def __init__(self, window):
        self.window = window
        self.interface = pyglet.graphics.Batch()
        self.session_manager_obj = SessionManager()
        self.active_user = self.session_manager_obj.get_active_user()
        if self.active_user:
            self.data_storage = shelve.open(f'data\\temp\\game_data\\{self.active_user}')
        self.auth_db = shelve.open("data\\auth_db")
        self.secure_password_dict: dict = self.auth_db.get("password_dict", dict())
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
        self.state = "welcome"
        self.username = ""
        self.argon_hasher = PasswordHasher(
            time_cost=4,
            memory_cost=65536,
            parallelism=5,
            hash_len=32,
            salt_len=32
        )
       
        
        
            
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
                if self.state == "welcome":
                    if self.log_in_btn.is_clicked(x, y):
                        self.handle_opt_btn_resize_order(type_="Log In")
                        self.draw_log_in_page()
                        
                        
                    if self.register_btn.is_clicked(x, y):
                        self.handle_opt_btn_resize_order(type_="Register")
                        self.draw_register_page()
                
                else:
                    if self.text_box.text != "":
                        if "usrname_prompt" in self.state:
                            if self.next_btn.is_clicked(x, y):
                                self.handle_pin_ui_request()
                        elif self.state == "log_in_pin_prompt":
                            if self.next_btn.is_clicked(x, y):
                                self.verify(self.username, self.text_box.text)
                        elif self.state == "register_pin_prompt":
                            if self.next_btn.is_clicked(x, y):
                                self.create_account(self.username, self.text_box.text)
    
    def draw_log_in_page(self):
        self.text_box.set_visible(True)
        self.next_btn.set_visible(True)
        self.state = "log_in_usrname_prompt"
        self.text_box.masked = False

    def draw_register_page(self):
        self.text_box.set_visible(True)
        self.next_btn.set_visible(True)
        self.state = "register_usrname_prompt"
        self.text_box.masked = False
    
    def handle_pin_ui_request(self):
        #print(self.text_box.text)
    
        self.username = self.text_box.text
        self.welcome_label.text = f"Welcome, {self.username}"
        
        self.text_box.masked = True

        self.text_box.placeholder_color = (110, 115, 125, 255)
        self.text_box.text = ""
        self.text_box.placeholder = "Enter PIN"
        self.text_box.update_text_rendering()
        
        if self.state == "log_in_usrname_prompt":
            self.state = "log_in_pin_prompt"
        elif self.state == "register_usrname_prompt":
            self.state = "register_pin_prompt"
    
    
        
    def handle_success(self):
        self.main_card.visible = False
        self.next_btn.set_visible(False)
        self.text_box.set_visible(False)
        #self.handle_session_management()
        self.session_manager_obj.save_session(username=self.username)
        self.welcome_label.x = 50
        self.welcome_label.y = self.window.height // 2 + 50
        self.welcome_label.width = self.window.width - 100
        self.welcome_label.multiline = True
        self.welcome_label.font_size = 28
        self.welcome_label.color = (255, 255, 255, 255) # Include alpha
        self.welcome_label.text = \
        "Success!\nYou may now safely close this window.\nSector Eight Authentication Manager"
        
        
    
    def verify(self, username, password):
        clean_username = username.strip().lower()

        if clean_username not in self.secure_password_dict:
            self.handle_opt_btn_resize_order(type_="Log In")
            self.state = "log_in_usrname_prompt" # Reset state!
            self.text_box.placeholder_color = (200, 0, 0)
            self.text_box.masked = False
            self.text_box.text = ""
            self.text_box.placeholder = "User doesn't exist!"
            self.text_box.update_text_rendering()
            self.username = ""
            return

        stored_hash = self.secure_password_dict[clean_username]
        
        try:
            self.argon_hasher.verify(stored_hash, password)
            self.text_box.placeholder_color = (110, 115, 125)
            self.text_box.placeholder = "Enter PIN"
            self.text_box.update_text_rendering()
        except Exception:
            self.text_box.placeholder_color = (200, 0, 0)
            self.text_box.text = ""
            self.text_box.placeholder = "Incorrect PIN!"
            self.text_box.update_text_rendering()
            self.username = ""
            return  # Stop execution!
        else:
            self.handle_success()
            
    
    def create_account(self, username, password):
        clean_username = username.strip().lower()

        # 1. Check if user already exists
        if clean_username in self.secure_password_dict:
            self.handle_opt_btn_resize_order(type_="Register")
            self.state = "register_usrname_prompt"
            self.text_box.placeholder_color = (200, 0, 0)
            self.text_box.masked = False
            self.text_box.text = ""
            self.text_box.placeholder = "User already exists"
            self.username = ""
            self.text_box.update_text_rendering()
            return  # Stop execution!

        # 2. Reset placeholder styling if successful
        self.text_box.placeholder_color = (110, 115, 125)
        self.text_box.placeholder = "Enter PIN"
        self.text_box.update_text_rendering()

        # 3. Hash password and save to dictionary
        self.secure_password_dict[clean_username] = self.argon_hasher.hash(password)
        
        # 4. Write BACK to shelve so changes persist on disk!
        self.auth_db["password_dict"] = self.secure_password_dict
        self.auth_db.sync()
        self.handle_success()
        
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
        self.welcome_label.font_size = 30
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
            #print(self.session_manager_obj.get_active_user())
        
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()
        
        
        