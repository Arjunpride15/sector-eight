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
                               utilities.Card,
                               utilities.ToggleButton)
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
        self.license_btn = None
        self.num_times_license_btn_clicked = 0
        self.about_list = list()
        with open(self.dotted_config_access.license_info.LicensePath, "r") as f:
            self.license_text = f.read()
        self.current_panel = "welcome"
        self.performance_btn = None
        self.fps_dropdown = None
        self.fps_heading = None
        self.fps_label = None
        self.max_fps_checker_obj = os_version_query.SystemCapabilityCheckerFor120FPS(self.window)
        self.fps_120_capable = self.max_fps_checker_obj.evaluate_120fps_support()["can_enable_120fps"]
        #print(self.fps_120_capable, self.max_fps_checker_obj.evaluate_120fps_support()["hardware_details"])
        if self.fps_120_capable:
            self.fps_list = [30, 60, 120]
        else:
            self.fps_list = [30, 60]
        self.performance_list = list()
        self.default_fps_index = self.fps_list.index(self.dotted_config_access.performance.FPS)
        self.vsync_toggle_btn = None
        
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
        if button == mouse.LEFT:
            if self.fps_dropdown:
                self.fps_dropdown.on_mouse_press(x, y, button, modifiers)
            if self.about_button.is_clicked(x, y):
                if not self.current_panel == "about":
                    self.destroy_panel()
                self.show_about_panel()
            if self.license_btn:
                if self.license_btn.is_clicked(x, y):
                    self.toggle_license_card_visibility()
            if self.performance_btn.is_clicked(x, y):
                if not self.current_panel == "performance":
                    self.destroy_panel()
                self.show_performance_panel()
            if self.vsync_toggle_btn:
                self.vsync_toggle_btn.on_mouse_press(x, y, button, modifiers)
    
    def toggle_license_card_visibility(self):
        if self.num_times_license_btn_clicked % 2 == 0:
             license_card_height = 4320
             self.license_card = utilities.Card(self.about_card_main.x,
                                            self.about_card_main.y - license_card_height - 100,
                                            1000, license_card_height, header_text="Apache License, Version 2.0",
                                            body_text=self.license_text,
                                            batch=self.interface, font_name=["Georgia", "serif"])
             self.license_btn.label.text = "Hide License ^"
             self.add_scrolllist(self.license_card)
             self.about_list.append(self.license_card)
             self.num_times_license_btn_clicked += 1
        else:
            self.scroll_objects.remove(self.license_card)
            self.about_list.remove(self.license_card)
            self.license_card.delete()
            self.license_card = None
            self.license_btn.label.text = "Show License ⏑"
            self.num_times_license_btn_clicked += 1
    
    def show_about_panel(self):
        if self.current_panel == "about":
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
        self.license_btn = utilities.Button("Show License ⏑", self.about_card_main.x,
                                            self.about_card_main.y - 80, 
                                            self.about_card_main.width, 40, self.interface, (35, 40, 70))
        
        self.add_scrolllist(
            [
                self.about_logo,
                self.about_card_main,
                self.license_btn
                
            ]
        )
        self.about_list.append(self.about_logo)
        self.about_list.append(self.about_card_main)
        self.about_list.append(self.license_btn)
        self.current_panel = "about"
    
    def turn_vsync_on_or_off(self, state: bool):
        self.dotted_config_access.performance.VSync = state
        self.configObj.toml_dict = self.dotted_config_access.to_dict()
        self.configObj.sync()
    def show_performance_panel(self):
        if self.current_panel == "performance":
            return
        
        self.fps_heading = pyglet.text.Label(
            text="FPS and VSync Settings", x=self.vruler.x + 30,
            y=self.ruler.y - 50, font_size=30, font_name="Open Sans",
            batch=self.interface
        )
        fps_options = [f"{fps_num} FPS" for fps_num in self.fps_list]
        
        self.fps_label = pyglet.text.Label(
            "FPS: ", self.fps_heading.x, self.fps_heading.y - 100,
            font_name="Open Sans", font_size=20, batch=self.interface,
            color=(255, 255, 255)
        )
        self.fps_dropdown = utilities.DropDownMenu(
            self.window, self.fps_label.x + 70, self.fps_label.y - 10, 200, 40,
            fps_options, default_index=self.default_fps_index, batch=self.interface, on_select=self.set_fps
        )
        
        self.vsync_toggle_btn = utilities.ToggleButton(
            x=self.fps_label.x, y=self.fps_label.y - 130,
            text="VSync On/Off", is_on=self.dotted_config_access.performance.VSync, 
            batch=self.interface,
            on_toggle=self.turn_vsync_on_or_off,
            on_color=(0, 240, 255, 255)
        )
        self.add_scrolllist(
            [
                self.fps_heading,
                self.fps_dropdown,
                self.vsync_toggle_btn
            ]
        )
        self.current_panel = "performance"
        self.performance_list.append(self.fps_heading)
        self.performance_list.append(self.fps_dropdown)
        self.performance_list.append(self.vsync_toggle_btn)
    
    def set_fps(self, fps: str):
        fps = int(fps.strip(" FPS"))
        self.dotted_config_access.performance.FPS = fps
        self.configObj.toml_dict = self.dotted_config_access.to_dict()
        self.configObj.sync()
        #print(fps)
    def destroy_panel(self):
        self.big_welcome.visible = False
        try:
            for i, item in enumerate(self.about_list.copy()):
                if item:
                    item.delete()
                try:
                    self.scroll_objects.remove(item)
                except ValueError:
                    ...
            self.about_list.clear()
            self.current_panel = None
            self.num_times_license_btn_clicked = 0
        except AttributeError:
            ...
        try:
            for i, item in enumerate(self.performance_list.copy()):
                if item:
                    item.delete()
                try:
                    self.scroll_objects.remove(item)
                except ValueError:
                    ...
            self.performance_list.clear()
            self.current_panel = None    
        except AttributeError:
            ...
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
        self.performance_btn = utilities.Button("\u26a1 Performance", self.about_button.x,
                                                self.about_button.y + self.about_button.height + 30,
                                                self.about_button.width, self.about_button.height,
                                                self.interface, (0, 230, 118, 255))
        
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