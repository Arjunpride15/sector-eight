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
import tastyerrors, obfuscator
import datetime, time
import pyglet.shapes
from argon2 import PasswordHasher
from session_manager import SessionManager
import logging
import sys
import box, os_version_query

class SectorEightSettings:
    def __init__(self, window):
        self.window = window
        self.interface = pyglet.graphics.Batch()
        self.header_interface = pyglet.graphics.Batch()
        self.mask_interface = pyglet.graphics.Batch()
        logging.basicConfig(format=" Log: %(asctime)s - %(levelname)s - %(message)s")
        self.session_manager_obj = SessionManager()
        self.active_user = self.session_manager_obj.get_active_user()
        self.obfuscator_obj = obfuscator.PseudoEncryptor()
        if self.active_user:
            self.data_storage = \
            shelve.open(f'data\\temp\\game_data\\{self.obfuscator_obj.obfuscate_filename(self.active_user)}')
            self.background = self.data_storage.get('background', (0.2, 0.2, 0.35, 1))
        else:
            Popen(["auth_launch.cmd"])
            sys.exit()
        
        
        self.auth_db = shelve.open("data\\auth_db")
        self.secure_password_dict: dict = self.auth_db.get("password_dict", dict())
        pyglet.options['search_local_libs'] = True
        pyglet.font.add_file('fonts/OpenSans-Regular.ttf')
        self.configObj = conf.Config()
        self.dotted_config_access = box.Box(self.configObj.toml_dict)
        self.music_switch = False
        self.vruler = None
        self.ruler = None
        self.pellets = self.data_storage.get('pellets', 0)
        self.mask_rect = None
        self.type_checklist = (pyglet.text.Label, 
                               pyglet.sprite.Sprite, 
                               pyglet.shapes.Line, 
                               utilities.Badge,
                               utilities.DropDownMenu,
                               utilities.Button,
                               utilities.Card)
        self.offset_y = 0
        self.min_scroll = 0
        self.max_scroll = 10000
        self.scroll_objects = list()
        self.main_view = True
        self.about_button = None
        self.big_welcome = None
        self.about_logo = None
        self.about_card_main = None
        self.license_card = None
        self.about_list = list()
        
        
    def add_scrolllist(self, element):
        if isinstance(element, self.type_checklist):
            self.scroll_objects.append(element)
        elif isinstance(element, list):
            for item in element:
                self.scroll_objects.append(item)
        else:
            raise tastyerrors.BadType(f'''Invalid argument("element") passed to home_backend.SectorEightSettings.add_scrollist; 
                                      argument passed was {element}''')
    def play(self, music_file=None):
        
        if music_file == None:
            if not self.music_switch:
                winsound.PlaySound(self.configObj.toml_dict['music']['settingsBackground'], 
                                    winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                                    
        else:
            device = miniaudio.PlaybackDevice()
            stream = miniaudio.stream_file(music_file)
            device.start(stream)
        
            
    def stop_music(self):
        winsound.PlaySound(None, winsound.SND_FILENAME)
        self.music_switch = False
    
    def handle_mouse_click(self, x, y, button, modifiers):
        if self.about_button.is_clicked(x, y):
            self.show_about_panel()
            self.big_welcome.visible = False
    
    def show_about_panel(self):
        if len(self.about_list) != 0:
            return
        logging.info("Handled!")
        about_img = pyglet.resource.image("images/logo.png")
        self.about_logo = pyglet.sprite.Sprite(about_img,
                                               x=self.vruler.x + 140,
                                               y=140, batch=self.interface)
        
        card_text = \
        f"""
        Sector Eight Version: {self.dotted_config_access.version.SectorEightVersion}
        
        Operating System: {os_version_query.get_detailed_os_name()}
        
        CPU: {os_version_query.get_cpu_info()}
        
        GPU: {pyglet.gl.gl_info.get_renderer()}
        
        OpenGL Version: {pyglet.gl.gl_info.get_version()[0]}.{pyglet.gl.gl_info.get_version()[1]}
        """
        card_height = 600
        self.about_card_main = utilities.Card(self.about_logo.x - 100,
                                              self.about_logo.y - card_height - 100, 1000,
                                              card_height, batch=self.interface,
                                              header_font_size=30, body_font_size=20,
                                              header_text="General Info",
                                              body_text=card_text)
        with open(self.dotted_config_access.license_info.LicensePath, "r") as f:
            license_text = f.read()
        
        license_card_height = 4320
        self.license_card = utilities.Card(self.about_card_main.x,
                                           self.about_card_main.y - license_card_height - 100,
                                           1000, license_card_height, header_text="Apache License, Version 2.0",
                                           body_text=license_text,
                                           batch=self.interface, font_name=["Georgia", "serif"])
        self.add_scrolllist(
            [
                self.about_logo,
                self.about_card_main,
                self.license_card
            ]
        )
        self.about_list.append(self.about_logo)
        self.about_list.append(self.license_card)
    
    def init_window(self):
        self.welcome_label = pyglet.text.Label(f'Welcome, {self.active_user}!', 
                                              font_name="Open Sans", 
                                              font_size=20,
                                              x=250, 
                                              y=740, 
                                              batch=self.header_interface, 
                                              color=(255, 255, 255, 255))
        self.pellet_label = pyglet.text.Label(f'\N{COIN}: {self.pellets}', 
                                              font_name="Open Sans", 
                                              font_size=20,
                                              x=83 + self.welcome_label.x + 300, 
                                              y=740, 
                                              batch=self.header_interface, 
                                              color=(253, 189, 1, 255))
        vruler_x = self.welcome_label.x - 20
        self.vruler = pyglet.shapes.Line(x=vruler_x, y=0,
                                         x2=vruler_x, y2=self.window.height,
                                         thickness=1.6, color=(255, 255, 255, 255), batch=self.header_interface)
        ruler_y = self.welcome_label.y - 20
        self.ruler = pyglet.shapes.Line(x=0, y=ruler_y, x2=self.window.width, y2=ruler_y,
                                        thickness=1.6, color=(255, 255, 255, 255), batch=self.header_interface)
        self.mask_rect = pyglet.shapes.Rectangle(
            x=0, y=ruler_y, width=self.window.width, height=self.window.width - ruler_y,
            color=utilities.convertGLtoRGBA(*self.background), batch=self.mask_interface
        )
        self.big_welcome = pyglet.text.Label(
            """
            Welcome to Sector Eight Settings

                ℹ️                           🛒
            ⚙️
                        🛒
                                        🏡
                        🎮
                                🪙""", 
                                             x=vruler_x + 100,
                                             y=ruler_y - 40,
                                             font_name=["Open Sans", "Segoe UI Emoji"],
                                             multiline=True,
                                             font_size=40,
                                             width=1200,
                                             batch=self.interface
            
                                            )
        self.about_button = utilities.Button("\u2139 About", 10, 30, vruler_x - 10 - 10,
                                             40, self.interface, (0, 229, 255))
        
        self.add_scrolllist(
            [
                self.big_welcome
            ]
        )
    def update(self, dt):
        ...
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()
        logging.disable(logging.WARNING)