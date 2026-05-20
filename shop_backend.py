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
import datetime
from recommendations import SectorEightRecommendations

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
        self.rec_obj = SectorEightRecommendations()
        self.rec_badge = None
        pyglet.options['search_local_libs'] = True
        pyglet.font.add_file('fonts/MerriweatherSans-Light.ttf')
        self.data_storage = shelve.open('data\\game_data')
        self.log_file = shelve.open(r"data\purchases")
        self.laser_powers = self.data_storage.get('laser', 5)
        self.xp_speedups = self.data_storage.get('xp', 3)
        self.powerups = self.data_storage.get('powerups', 10)
        self.invisible_powers = self.data_storage.get('invisiblity', 7)
        self.extra_lives = self.data_storage.get('extra_lives', 0)
        self.log = self.log_file.get("log", list())
        self.log_str = ''
        self.music_switch = False
        self.pellets = self.data_storage.get('pellets', 0)
        self.font_list = self.configObj.toml_dict['font']['fontList']
        self.emoji_font = self.configObj.toml_dict['font']['emojiFont']
        self.heading_font = 'Segoe UI'
        self.picks_list = ['TOP PICKS FOR YOU', 'RECOMMENDED', 'SUGGESTED', 'OFTEN BOUGHT']
        self.info_label = pyglet.text.Label('Shop | Sector Eight',
                                            font_name="Merriweather Sans",
                                            weight="light",
                                            font_size=70,
                                            x=11,
                                            y=580,
                                            batch=self.interface,
                                            color=(230, 230, 230, 230, 255))
        self.pellet_label = pyglet.text.Label(f'Pellets: {self.pellets}', 
                                              font_name=self.font_list, 
                                              font_size=20,
                                              stretch="expanded" ,
                                              x=20, 
                                              y=780, 
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
        
        self.transaction_id = 0
        self.id_label = pyglet.text.Label(f"Latest Transaction ID: {self.transaction_id}",
                                          font_name=self.font_list,
                                          font_size=20,
                                          stretch="expanded",
                                          x=250,
                                          y=780,
                                          batch=self.interface,
                                          color=(4, 217, 255, 255))
        self.product_names = {"Laser Boost": self.laser_powers, 
                              "XP Speedups": self.xp_speedups, 
                              "Powerups": self.powerups, 
                              "Invisibiity": self.invisible_powers, 
                              "Extra Life": self.extra_lives,
                              }
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
        self.vr1.x = self.vr1.x2 = 1_100
        self.product_label = pyglet.text.Label(
            text="PRODUCTS",
            font_name=self.heading_font,
            font_size=20,
            weight="ultrabold",
            stretch="expanded",
            x=self.vr1.x,
            y=430,
            batch=self.interface,
            color=(30, 189, 225, 255)
        )
        self.offset_x = 0
        self.min_scroll = -20000 # How far right the shop goes
        self.max_scroll = 0     # The starting left boundary
        self.badge_list: list[utilities.Badge] = list()
        
    def sync_data(self, name, var):
        self.data_storage[name] = var
        self.data_storage.sync()    
    def add_scrolllist(self, element):
        if isinstance(element, self.type_checklist):
            self.scroll_objects.append(element)
        elif isinstance(element, list):
            for item in element:
                self.scroll_objects.append(item)
        else:
            raise tastyerrors.BadType(f'''Invalid argument("element") passed to shop_backend.SectorEightShop.add_scrollist; 
                                      argument passed was {element}''')
        

    
    def generate_id(self, digits: int) -> int:
        purchase_id = str()
        for _ in range(digits):
            purchase_id = purchase_id + str(random.randint(0, 9))
        return int(purchase_id) 
    
    def log_buy(self, trans_id, name_item):
        self.log_str = f"{str(datetime.datetime.now())} {name_item} {trans_id}"
        self.log.append(self.log_str)
        self.log_file['log'] = self.log
        self.log_file.sync()        
    def buy(self, item):
        if not item in self.product_names.keys():
            raise tastyerrors.ProcessingError(f"Invalid product passed to buy ({item})")
            return
        self.transaction_id = self.generate_id(12)
        for index, prod in enumerate(self.available_items):
            if item == prod.item_name:
                break
        if self.pellets > 0 or self.pellets > self.available_items[index].item_price:
            self.pellets -= self.available_items[index].item_price
            self.pellet_label.text = f"Pellets: {self.pellets}"
            self.sync_data('pellets', self.pellets)
        else:
            raise tastyerrors.InsufficientFundsError(f"Sufficient pellets aren't available to buy {item}")
        if item == "Laser Boost":
            self.laser_powers += 1
            self.sync_data("laser", self.laser_powers)
        elif item == "XP Speedups":
            self.xp_speedups += 1
            self.sync_data('xp', self.xp_speedups)
        elif item == "Powerups":
            self.powerups += 1
            self.sync_data('powerups', self.powerups)
        elif item == "Invisibility":
            self.invisible_powers += 1
            self.sync_data('invisibility', self.invisible_powers)
        elif item == "Extra Life":
            self.extra_lives += 1
            self.sync_data('extra_lives', self.extra_lives)
        self.log_buy(self.transaction_id, item)
        
    def make_recommended_item(self):
        suggested_item = self.rec_obj.get_recommended_item()
        for item in self.available_items:
            if suggested_item == item.item_name:
                break
        discount = random.randint(1, item.item_price - 1)
            
        self.rec_badge = utilities.Badge(
            x=20, y=0,
            width=1000, height=self.ruler_y, bg_color=item.bg_color, 
            btn_color=(150, 200, 150, 225), emoji_color=(200, 200, 200), main_text_color=(0, 0, 0, 225),
            main_text=item.item_name, emoji="\U0001F4AF", 
            btn_text=f"Offer: Buy now for {item.item_price - discount}P", bob=True, batch=self.interface
            
        )
    def init_window(self):
        
        self.ruler = pyglet.shapes.Line(-10, self.ruler_y,  self.ruler_x + 100_000, self.ruler_y,
                                        thickness = 2.0, color = (30, 189, 200, 200), batch=self.interface)
        self.make_recommended_item()
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
                             self.vr1,
                             self.product_label])
        self.add_scrolllist(self.badge_list)
        self.add_scrolllist(self.rec_badge)    
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
        self.id_label.text = f"Latest Transaction ID: {self.transaction_id}"
        self.product_names = {"Laser Boost": self.laser_powers, 
                              "XP Speedups": self.xp_speedups, 
                              "Powerups": self.powerups, 
                              "Invisibiity": self.invisible_powers, 
                              "Extra Life": self.extra_lives,
                              }
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()