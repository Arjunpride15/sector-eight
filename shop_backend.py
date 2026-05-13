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


class ShopItem(NamedTuple):
    item_name: str
    item_price: int
    item_esc_char: str
    bg_color: tuple

class SectorEightShop:
    def __init__(self, window):
        self.WINDOW = window
        self.scroll_objects = list()
        self.interface = pyglet.graphics.Batch()
        self.configObj = conf.Config()
        self.data_storage = shelve.open('data\\game_data')
        self.music_switch = False
        self.pellets = self.data_storage.get('pellets', 0)
        self.font_list = self.configObj.toml_dict['font']['fontList']
        self.emoji_font = self.configObj.toml_dict['font']['emojiFont']
        self.heading_font = 'Segoe UI'
        self.picks_list = ['TOP PICKS FOR YOU', 'RECOMMENDED', 'SUGGESTED', 'OFTEN BOUGHT']
        self.pellet_label = pyglet.text.Label(f'Pellets: {self.pellets}', 
                                              font_name=self.font_list, 
                                              font_size=18, 
                                              x=20, 
                                              y=800, 
                                              batch=self.interface, 
                                              color=(253, 189, 1, 255))
        self.picks_label = pyglet.text.Label(random.choice(self.picks_list), 
                                              font_name=self.heading_font, 
                                              font_size=20,
                                              weight="ultrabold",
                                              stretch="expanded", 
                                              x=10, 
                                              y=430, 
                                              batch=self.interface,
                                               
                                              color=(30, 189, 225, 255))
        self.product_names = ["Laser Boost", "XP Speedups", "Powerups", "Invisibiity", "Extra Life"]
        self.available_items = [
            ShopItem('Laser Boost', 25, "\U0001f52b", (57, 255, 20, 255)),
            ShopItem('XP Speedups', 50, "\u26a1", (127, 235, 232, 255)),
            ShopItem('Powerups', 15, "\u2728", (254, 1, 154, 255)),
            ShopItem('Invisibiity', 35, "\u2b50", (138, 0, 255, 255)),
            ShopItem('Extra Life', 100, "\u2764", (255, 0, 102, 255))
        ]
        self.ruler = None
        self.type_checklist = (pyglet.text.Label, pyglet.sprite.Sprite, pyglet.shapes.Line, utilities.Badge)
        self.ruler_x = self.picks_label.x
        self.ruler_y = (self.picks_label.y - 10)
        self.number_of_vrulers = 2
        self.vruler_list = list()
        for _ in range(self.number_of_vrulers):
            vruler = pyglet.shapes.Line(-100, 0, -100, self.ruler_y,
                                            thickness=2.0, color=(30, 189, 200, 200), batch=self.interface)
            self.vruler_list.append(vruler)
        self.vr1 = self.vruler_list[1]
        self.vr1.x = self.vr1.x2 = 1_500
        self.offset_x = 0
        self.min_scroll = -20000 # How far right the shop goes
        self.max_scroll = 0     # The starting left boundary
        self.badge_list: list[utilities.Badge] = list()
        
    def add_scrolllist(self, element):
        if isinstance(element, self.type_checklist):
            self.scroll_objects.append(element)
        elif isinstance(element, list):
            for item in element:
                self.scroll_objects.append(item)
        else:
            raise tastyerrors.BadType(f'''Invalid argument("element") passed to shop_backend.SectorEightShop.add_scrollist; argument passed was {element}''')
        
    def init_window(self):
        
        self.ruler = pyglet.shapes.Line(-10, self.ruler_y,  self.ruler_x + 100_000, self.ruler_y,
                                        thickness = 2.0, color = (30, 189, 200, 200), batch=self.interface)
        for i, item in enumerate(self.available_items):
            if i == 0:
                item_badge = utilities.Badge(
                    self.vr1.x + 20,
                    0, 800, self.ruler_y, item.bg_color, (150, 200, 150, 225), (200, 200, 200), (0, 0, 0, 225),
                    item.item_name, item.item_esc_char, f"Buy for {item.item_price}P", bob=True, batch=self.interface
                )
                self.badge_list.append(item_badge)
            elif i != 0:
                item_badge = utilities.Badge(
                    self.badge_list[i - 1].x + 900,
                    0, 800, self.ruler_y, item.bg_color, (150, 200, 150, 225), (200, 200, 200), (0, 0, 0, 225),
                    item.item_name, item.item_esc_char, f"Buy for {item.item_price}P", bob=True, batch=self.interface
                )
                self.badge_list.append(item_badge)
        
        
        self.add_scrolllist([self.picks_label,
                             self.ruler,
                             self.vr1])
        self.add_scrolllist(self.badge_list)
    def buy(self, item):
        if not item in self.product_names:
            raise tastyerrors.ProcessingError(f"Invalid product passed to buy ({item})")
            return
        
        
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
    def update(self, dt):
        for obj in self.scroll_objects:
            if hasattr(obj, 'update'):
                obj.update(dt)       
    
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()