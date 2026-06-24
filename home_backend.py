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
        self.user = "test_player"
        self.font_list = self.configObj.toml_dict['font']['fontList']
        self.side_panel_btn = None
        self.background = (51, 51, 89, 255)
        self.num_side_btn_clicked = 0
        self.user_img = None
        self.user_label = None
        self.side_panel_user_ui = list()
        self.settings_button = None
        self.shop_btn = None
        self.game_btn = None
        self.query_btn = None
        self.logout_btn = None
        self.cyclic_badge = None
        self.badge_1 = None
        self.badge_2 = None
        self.badge_3 = None
        self.badge_4 = None
        self.cyclic_state_list = None
        self.left_nav_btn = None
        self.right_nav_btn = None
        
    def sync_data(self, name, var):
        self.data_storage[name] = var
        self.data_storage.sync()
    
    def add_multiple_elements(self, / ,array: list, *args):
        for element in args:
            array.append(element)
            
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
    
    def show_side_panel(self):
        self.welcome_label.x = 270
        for item in self.side_panel_user_ui:
            item.opacity = 255
        self.settings_button.set_visible(True)
        self.shop_btn.set_visible(True)
        self.game_btn.set_visible(True)
        self.query_btn.set_visible(True)
        self.logout_btn.set_visible(True)
        self.left_nav_btn.set_visible(False)
        self.right_nav_btn.set_visible(False)
        
    def hide_side_panel(self):
        self.welcome_label.x = 100
        for item in self.side_panel_user_ui:
            item.opacity = 0
        self.settings_button.set_visible(False)
        self.shop_btn.set_visible(False)
        self.game_btn.set_visible(False)
        self.query_btn.set_visible(False)
        self.logout_btn.set_visible(False)
        self.left_nav_btn.set_visible(True)
        self.right_nav_btn.set_visible(True)
    def toggle_side_panel(self):
        if self.num_side_btn_clicked % 2 == 0:
            #print("Showing side panel")
            self.show_side_panel()
            self.num_side_btn_clicked += 1
        else:
            #print("Hiding side panel")
            self.hide_side_panel()
            self.num_side_btn_clicked += 1
    def init_window(self):
        pyglet.clock.schedule_interval_for_duration(self.show_loading_screen, 1/60, 2.4)
        pyglet.clock.schedule_once(self.hide_loading_screen, 2.4)
    
    def main_init_window(self):
        self.welcome_label = pyglet.text.Label(f'Welcome, {self.user}!', 
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
        self.user_img = pyglet.sprite.Sprite(pyglet.resource.image("images/user.png"), x=50.0, y=self.ruler.y - 130,
                                             batch=self.interface)
        self.user_img.opacity = 0
        
        self.user_label = pyglet.text.Label(self.user, self.user_img.x - 10, self.user_img.y - 35, 
                                            font_name=self.font_list, batch=self.interface, color=(255, 255, 255), 
                                            font_size=15)
        self.user_label.opacity = 0
        self.settings_button = utilities.Button("Settings \u2699\ufe0f", 
                                                        5, self.user_label.y - 60,
                                                        240, 40, self.interface, (20, 20, 25), text_color=(57, 255, 20),
                                                        font_size=14, radius=10)
        
        self.settings_button.set_visible(False)
        self.shop_btn = utilities.Button("Shop \U0001f6d2", 
                                            5, self.settings_button.y - 60,
                                            240, 40, self.interface, (24, 26, 46), text_color=(255, 50, 177),
                                            font_size=14, radius=10)
        self.shop_btn.set_visible(False)
        self.game_btn = utilities.Button("Game \U0001f3ae", 
                                            5, self.shop_btn.y - 60,
                                            240, 40, self.interface, (24, 26, 46), text_color=(0, 150, 255),
                                            font_size=14, radius=10)
        self.game_btn.set_visible(False)
        self.query_btn = utilities.Button("Query \u2754", 
                                            5, self.game_btn.y - 60,
                                            240, 40, self.interface, (24, 26, 46), text_color=(186, 85, 211),
                                            font_size=14, radius=10)
        self.query_btn.set_visible(False)
        self.logout_btn = utilities.Button("Logout \U0001f3c3", 
                                            5, self.query_btn.y - 60,
                                            240, 40, self.interface, (24, 26, 46), text_color=(220, 53, 69),
                                            font_size=14, radius=10)
        self.logout_btn.set_visible(False)
        self.cyclic_badge = utilities.CyclicBadge(4)
        self.badge_1 = utilities.Badge(300, self.shop_btn.y - 200, 1000, 400, (32, 38, 68),
                                       (0, 150, 180), (250, 250, 250), (0, 210, 225), "Action Badge: Shop",
                                       "\U0001f6d2\ufe0f", "Launch \u2197", batch=self.interface)
        self.badge_2 = utilities.Badge(300, self.shop_btn.y - 200, 1000, 400, (32, 38, 68),
                                       (0, 150, 180), (250, 250, 250), (0, 210, 225), "Action Badge: Settings",
                                       "\u2699\ufe0f", "Launch \u2197", batch=self.interface)
        self.badge_3 = utilities.Badge(300, self.shop_btn.y - 200, 1000, 400, (32, 38, 68),
                                       (0, 150, 180), (250, 250, 250), (0, 210, 225), "Action Badge: Help",
                                       "\u2754\ufe0f", "Launch \u2197", batch=self.interface)
        self.badge_4 = utilities.Badge(300, self.shop_btn.y - 200, 1000, 400, (32, 38, 68),
                                       (0, 150, 180), (250, 250, 250), (0, 210, 225), "Action Badge: Game",
                                       "\U0001f3ae\ufe0f", "Launch \u2197", batch=self.interface)
        self.left_nav_btn = utilities.Button("\U0000276E", self.badge_1.x - 70, self.badge_1.y + 200, 50, 50, self.interface, (255, 215, 0), 25)
        self.right_nav_btn = utilities.Button("\U0000276F", self.badge_1.x + self.badge_1.width + 30, self.badge_1.y + 200, 50, 50, self.interface, (255, 215, 0), 25)
        self.add_multiple_elements(self.side_panel_user_ui, self.user_img, self.user_label)
        
        
        
    def update(self, dt):
        if self.welcome_label != None:
            self.pellet_label.x = 83 + self.welcome_label.x + 200
            self.vruler.x = self.vruler.x2 = self.welcome_label.x - 20
            self.ruler.y = self.ruler.y2 = self.welcome_label.y - 20
            try:
                self.cyclic_state_list = self.cyclic_badge.cyclic_list
                self.badge_1.set_visible(self.cyclic_state_list[0])
                self.badge_2.set_visible(self.cyclic_state_list[1])
                self.badge_3.set_visible(self.cyclic_state_list[2])
                self.badge_4.set_visible(self.cyclic_state_list[3])
            except AttributeError:
                ...
        
        
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()          