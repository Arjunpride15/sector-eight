import winsound
import miniaudio
import utilities
import pyglet
import conf
import shelve
from subprocess import Popen
from canvas import NotImplementedWarning
from typing import NamedTuple

class ShopItem(NamedTuple):
    item_name: str
    item_price: int
    item_esc_char: str

class SectorEightShop:
    def __init__(self, window):
        self.WINDOW = window
        self.interface_objects = list()
        self.interface = pyglet.graphics.Batch()
        self.configObj = conf.Config()
        self.data_storage = shelve.open('data\\game_data')
        self.music_switch = False
        self.pellets = self.data_storage.get('pellets', 0)
        self.font_list = self.configObj.toml_dict['font']['fontList']
        self.emoji_font = self.configObj.toml_dict['font']['emojiFont']
        self.heading_font = 'Segoe UI'
        self.pellet_label = pyglet.text.Label(f'Pellets: {self.pellets}', 
                                              font_name=self.font_list, 
                                              font_size=18, 
                                              x=20, 
                                              y=800, 
                                              batch=self.interface, 
                                              color=(253, 189, 1, 255))
        self.picks_label = pyglet.text.Label('TOP PICKS', 
                                              font_name=self.heading_font, 
                                              font_size=18,
                                              weight="bold", 
                                              x=10, 
                                              y=400, 
                                              batch=self.interface,
                                               
                                              color=(30, 189, 225, 255))
        self.prices = [
            ShopItem('Laser Boost', 25, "\U0001f52b"),
            ShopItem('XP Speedups', 50, "\u26a1"),
            ShopItem('Powerups', 15, "\u2728"),
            ShopItem('Invisibiity', 35, "\u2b50"),
            ShopItem('Extra Life', 100, "\u2764")
        ]
        
    def init_window(self):
        self.interface_objects.append(self.picks_label)
    def play(self, **kwargs):
        try:
            if not kwargs:
                if not self.music_switch:
                    winsound.PlaySound("audio/shop-music.wav", winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
                                       
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
    
    def start(self):
        self.play()
        pyglet.app.run()