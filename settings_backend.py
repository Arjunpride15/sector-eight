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
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import security_prompt

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
        self.texture_scaling_dropdown = None
        self.texture_scaling_dropdown_options = [
            "Nearest-Neighbor",
            "Bilinear Interpolation",
            "Trilinear Mipmapping"
        ]
        self.texture_scaling_label = None
        self.opengl_advanced_settings_heading = None
        self.default_texture_scaling_index = \
            self.texture_scaling_dropdown_options.index(self.dotted_config_access.performance.TextureScaling)
        self.account_list = list()
        self.account_btn = None
        self.profile_picture = None
        self.edit_profile_btn = None
        self.edit_password_btn = None
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
            if self.texture_scaling_dropdown and self.current_panel == "performance":
                self.texture_scaling_dropdown.on_mouse_press(x, y, button, modifiers)
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
            if self.account_btn.is_clicked(x, y):
                if self.current_panel != "my_account":
                    self.destroy_panel()
                self.show_my_account_panel()
            if self.vsync_toggle_btn:
                self.vsync_toggle_btn.on_mouse_press(x, y, button, modifiers)
            if self.edit_profile_btn.is_clicked(x, y) and self.current_panel == "my_account":
                filename = self.show_file_dialog()
                self.edit_profile_picture(filename)
            if self.edit_password_btn:
                if self.edit_password_btn.is_clicked(x, y) and self.current_panel == "my_account":
                    security_prompt.prompt_pin_pyglet(f"Confirm Windows credentials to edit {self.active_user}'s Sector Eight Password",
                                                      self.edit_password)
    
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
            self.window, self.fps_label.x + 70, self.fps_label.y - 10, 280, 40,
            fps_options, default_index=self.default_fps_index, batch=self.interface, on_select=self.set_fps
        )
        
        self.vsync_toggle_btn = utilities.ToggleButton(
            x=self.fps_label.x, y=self.fps_label.y - 130,
            text="VSync On/Off", is_on=self.dotted_config_access.performance.VSync, 
            batch=self.interface,
            on_toggle=self.turn_vsync_on_or_off,
            on_color=(0, 240, 255, 255)
        )
        
        self.opengl_advanced_settings_heading = pyglet.text.Label(
            text="Advanced OpenGL Graphics Settings", x=self.vsync_toggle_btn.x, 
            y=self.vsync_toggle_btn.y - 90, 
            font_size=30, font_name="Open Sans",
            batch=self.interface
        )
        self.texture_scaling_label = pyglet.text.Label(
            text="Texture Scaling: ", x=self.opengl_advanced_settings_heading.x, 
            y=self.opengl_advanced_settings_heading.y - 90,
            font_name="Open Sans", font_size=20, batch=self.interface
            
        )
        self.texture_scaling_dropdown = utilities.DropDownMenu(
            self.window, x=self.texture_scaling_label.x + 230, y=self.texture_scaling_label.y - 10,
            width=280, height=40, options=self.texture_scaling_dropdown_options,
            batch=self.interface, on_select=self.change_texture_scaling_mode, 
            default_index=self.default_texture_scaling_index
        )
        self.add_scrolllist(
            [
                self.fps_heading,
                self.fps_dropdown,
                self.fps_label,
                self.vsync_toggle_btn,
                self.texture_scaling_dropdown,
                self.texture_scaling_label,
                self.opengl_advanced_settings_heading
            ]
        )
        self.current_panel = "performance"
        self.performance_list.append(self.fps_heading)
        self.performance_list.append(self.fps_label)
        self.performance_list.append(self.fps_dropdown)
        self.performance_list.append(self.vsync_toggle_btn)
        self.performance_list.append(self.texture_scaling_dropdown)
        self.performance_list.append(self.texture_scaling_label)
        self.performance_list.append(self.opengl_advanced_settings_heading)
    def set_fps(self, fps: str):
        fps = int(fps.strip(" FPS"))
        self.dotted_config_access.performance.FPS = fps
        self.configObj.toml_dict = self.dotted_config_access.to_dict()
        self.configObj.sync()
        #print(fps)
    
    def change_texture_scaling_mode(self, texture_scaling_str):
        self.dotted_config_access.performance.TextureScaling = texture_scaling_str
        self.configObj.toml_dict = self.dotted_config_access.to_dict()
        self.configObj.sync()
    
    def show_my_account_panel(self):
        if self.current_panel == "my_account":
            return
        
        profile_picture_x = ((self.window.width - self.vruler.x) // 2) - 50
        try:
            self.profile_picture = pyglet.sprite.Sprite(
                pyglet.resource.image(f"images/{self.obfuscator_obj.obfuscate_filename(self.active_user)}.tif"),
                                                        x=profile_picture_x, y=self.ruler.y - 390,
                                                        batch=self.interface)
        except pyglet.resource.ResourceNotFoundException:
            self.profile_picture = pyglet.sprite.Sprite(
                pyglet.resource.image(f"images/user.png"), x=profile_picture_x, y=self.ruler.y - 390,
                                                        batch=self.interface)
        self.profile_picture.scale = 3
        self.edit_profile_btn = utilities.Button(
            "\U0001F58C Edit Profile Picture", self.profile_picture.x,
            self.profile_picture.y - 60, 350, 40, self.interface, (0, 240, 255, 255)
        )
        self.edit_password_btn = utilities.Button(
            "\u270F Edit Password", self.edit_profile_btn.x,
            self.edit_profile_btn.y - 100, 350, 40, self.interface, (70, 130, 180)
        )
        self.add_scrolllist(
            [
                self.profile_picture,
                self.edit_profile_btn,
                self.edit_password_btn
            ]
        )
        self.account_list.append(self.profile_picture)
        self.account_list.append(self.edit_profile_btn)
        self.account_list.append(self.edit_password_btn)
        self.current_panel = "my_account"
    
    def show_file_dialog(self):
        root = tk.Tk()
        root.withdraw()  # Hide the main Tk window
        root.attributes('-topmost', True)  # Bring file picker in front of Pyglet
        try:
            file = filedialog.askopenfilename(parent=root, title="Select Profile Picture",
            filetypes=[
                ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"),
                ("PNG Files (*.png)", "*.png"),
                ("JPEG Files (*.jpg)", "*.jpg;*.jpeg"),
                ("GIF Files (*.gif)", "*.gif"),
                ("TIFF Files (*.tiff)", "*.tiff")
            ]
            )
        finally:
            root.destroy()
        return file
    def edit_profile_picture(self, input_image_path):
        if not input_image_path:
            return

        output_path = f"images/{self.obfuscator_obj.obfuscate_filename(self.active_user)}.tif"
        
        # 1. Process and save the file with Pillow
        pillow_image: Image.Image = Image.open(input_image_path)
        resized_image: Image.Image = pillow_image.resize((100, 100))
        resized_image.save(output_path)
        
        # 2. Delete the old Pyglet sprite to free memory
        if self.profile_picture:
            self.profile_picture.delete()
        
        # 3. Load directly from disk path (bypasses pyglet.resource lookup)
        profile_picture_x = ((self.window.width - self.vruler.x) // 2) - 50
        loaded_image = pyglet.image.load(output_path)
        
        self.profile_picture = pyglet.sprite.Sprite(
            loaded_image, 
            x=profile_picture_x, 
            y=self.ruler.y - 390,
            batch=self.interface
        )
        self.profile_picture.scale = 3

        # 4. Update the tracking list reference
        if self.account_list:
            self.account_list[0] = self.profile_picture
    
    def edit_password(self, correct_auth):
        print(correct_auth)
    def destroy_panel(self):
        self.big_welcome.visible = False
        
        # For About panel: 
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
        
        # For the Performance panel:
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
        # For the My Account panel:
        try:
            for i, item in enumerate(self.account_list.copy()):
                if item:
                    item.delete()
                try:
                    self.scroll_objects.remove(item)
                except ValueError:
                    ...
            self.account_list.clear()
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
        self.account_btn = utilities.Button(
            "\U0001F464 My Account", self.performance_btn.x, 
            self.performance_btn.y + self.performance_btn.height + 30,
            self.performance_btn.width, self.performance_btn.height, self.interface,
            (124, 77, 255)
        )
        
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