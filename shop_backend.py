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
import datetime, time
from recommendations import SectorEightRecommendations, SectorEightHistory

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
                                          x=self.pellet_label.x + 230,
                                          y=780,
                                          batch=self.interface,
                                          color=(4, 217, 255, 255))
        self.product_names = {"Laser Boost": self.laser_powers, 
                              "XP Speedups": self.xp_speedups, 
                              "Powerups": self.powerups, 
                              "Invisibility": self.invisible_powers, 
                              "Extra Life": self.extra_lives,
                              }
        self.available_items = [
            ShopItem('Laser Boost', 25, "\U0001f52b", (57, 255, 20, 255)),
            ShopItem('XP Speedups', 50, "\u26a1", (127, 235, 232, 255)),
            ShopItem('Powerups', 15, "\u2728", (254, 1, 154, 255)),
            ShopItem('Invisibility', 35, "\u2b50", (138, 0, 255, 255)),
            ShopItem('Extra Life', 100, "\u2764", (255, 0, 102, 255))
        ]
        self.ruler = None
        self.type_checklist = (pyglet.text.Label, pyglet.sprite.Sprite, pyglet.shapes.Line, utilities.Badge)
        self.ruler_x = self.picks_label.x
        self.ruler_y = self.picks_label.y
        self.number_of_vrulers = 3
        self.vruler_list = list()
        for _ in range(self.number_of_vrulers):
            vruler = pyglet.shapes.Line(-100, 0, -100, self.ruler_y,
                                            thickness=2.0, color=(30, 189, 200, 200), batch=self.interface)
            self.vruler_list.append(vruler)
        self.vr1 = self.vruler_list[1]
        self.vr1.x = self.vr1.x2 = 1_100
        self.vr2 = self.vruler_list[2]
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
        self.min_scroll = -10000 # How far right the shop goes
        self.max_scroll = 0     # The starting left boundary
        self.badge_list: list[utilities.Badge] = list()
        self.item_discount = 0
        self.home_button = None
        self.game_button = None
        self.query_button = None
        self.history_button = None
        self.cross_button = None
        self.translucent_layer = None
        self.main_view = True
        self.cross_button = None
        self.history_badge = None
        self.view_index = -1
        self.history_instance = SectorEightHistory()
        self.datetime_history = self.history_instance.get_date_time_history()
        self.general_history = self.history_instance.get_general_history()
        self.left_nav_btn = None
        self.right_nav_btn = None
        self.miami_glitch_text = None
        self.bool_glitchy_text_visible = False
        self.background = self.data_storage.get('background', (0.2, 0.2, 0.35, 1))
        self.theme_dropdown = None
        self.theme_backgrounds = {
            'Dark+': (30/255, 30/255, 30/255, 1.0),
            'Epic Dark Blue': (15/255, 18/255, 32/255, 1.0),
            'Modern Blue': (0.2, 0.2, 0.35, 1),
            'Simply Light': (0.898, 0.914, 0.941, 1.0),
            'Light Sunset': (253/255, 230/255, 224/255, 1.0),
            'Neon Mania': (random.random(), random.random(), random.random(), 1.0)
        }
        self.go_to_start_of_shop_btn = None
    def sync_data(self, name, var):
        self.data_storage[name] = var
        self.data_storage.sync()
    def update_history(self):
        self.history_instance = SectorEightHistory()
        self.datetime_history = self.history_instance.get_date_time_history()
        self.general_history = self.history_instance.get_general_history() 
    def play(self, **kwargs):
        try:
            if not kwargs:
                if not self.music_switch:
                    winsound.PlaySound(self.configObj.toml_dict['music']['shopBackground'], 
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
        
    def send_mouse_scroll(self, scroll_y):

        # Calculate intended move
        move = 20 if scroll_y < 0 else -20
        
        # Check if the NEW offset would be in bounds
        if self.max_scroll >= (self.offset_x + move) >= self.min_scroll:
            self.offset_x += move
            for sprite in self.scroll_objects:
                sprite.x += move
    def clock_compat_back_mouse_scroll(self, dt):
        self.send_mouse_scroll(-10)
           
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
    
    def log_buy(self, trans_id, name_item, item_price):
        self.log_str = f"{str(datetime.datetime.now())} | {name_item} | {trans_id} | {item_price}"
        self.log.append(self.log_str)
        self.log_file['log'] = self.log
        self.log_file.sync()        
    def buy(self, item, discount=0):
        if not item in self.product_names.keys():
            raise tastyerrors.ProcessingError(f"Invalid product passed to buy ({item})")
            return
        for index, prod in enumerate(self.available_items):
            if item == prod.item_name:
                break
        # Note: The index and prod variables are available to use even after the loop finishes.
        # This approach that we have followed is very performance-centic and lightweight!
        total_price = self.available_items[index].item_price - discount
        if self.pellets > 0 and self.pellets >= total_price:
            self.pellets -= total_price
            self.pellet_label.text = f"Pellets: {self.pellets}"
            self.sync_data('pellets', self.pellets)
            self.play(music_file=self.configObj.toml_dict['music']['shopBuySuccess'])
        else:
            self.play(music_file=self.configObj.toml_dict['music']['shopBuyError'])
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
        self.transaction_id = self.generate_id(12)
        self.log_buy(self.transaction_id, item, total_price)
        
    def make_recommended_item(self):
        suggested_item = self.rec_obj.get_recommended_item()
        for item in self.available_items:
            if suggested_item == item.item_name:
                break
        self.item_discount = random.randint(1, item.item_price - 1)
            
        self.rec_badge = utilities.Badge(
            x=20, y=0,
            width=1000, height=self.ruler_y, bg_color=item.bg_color, 
            btn_color=(150, 200, 150, 225), emoji_color=(200, 200, 200), main_text_color=(0, 0, 0, 225),
            main_text=item.item_name, emoji="\U0001F4AF", 
            btn_text=f"Offer: Buy now for {item.item_price - self.item_discount}P", batch=self.interface
            
        )
        self.rec_obj.release_file() # Needed for the database to close properly.
    def smooth_go_to_start(self):
        scroll_interval = 0.008
        time_taken = ((abs(self.offset_x)/20) + (scroll_interval * 2)) * scroll_interval
        try:
            pyglet.clock.unschedule(self.clock_compat_back_mouse_scroll)
        except Exception:
            ...
        pyglet.clock.schedule_interval_for_duration(self.clock_compat_back_mouse_scroll,
                                                    scroll_interval, time_taken)
            
    def make_option_buttons(self) -> None:
        self.home_button = utilities.Button('\U0001f3e1', 1390, self.pellet_label.y - 25, 60, 50, 
                                            self.interface, (78, 205, 196), 25, self.emoji_font)
        self.game_button = utilities.Button("\U000021A9", 1460, self.pellet_label.y - 25, 60, 50, 
                                            self.interface, (255, 107, 107), 25, self.emoji_font)
        self.query_button = utilities.Button('\u2754', 1530, self.pellet_label.y - 25, 60, 50,
                                             self.interface, (255, 230, 109), 25, self.emoji_font)
        self.history_button = utilities.Button("\U000023F3", 1320, self.pellet_label.y - 25, 60, 50,
                                               self.interface, (0, 229, 255, 255), 25, self.emoji_font)
        
        self.go_to_start_of_shop_btn = utilities.Button("\u23EE", 1250, self.pellet_label.y - 25, 60, 50,
                                             self.interface, (0, 245, 255, 255), 25, self.emoji_font)
        
    def home(self):
        Popen(["unilaunch.cmd", "-sh"])
    
    def game(self):
        Popen(["unilaunch.cmd", "-sg"])
    
    def query(self):
        raise NotImplementedWarning('Query button clicked')
    
    def show_history_badge(self):
        try:
            self.update_history()
            product_datetime = f"Bought on: \
                                    {self.datetime_history[self.view_index]['time']} \
                                    {self.datetime_history[self.view_index]['date']}"
            transaction_str = f"Transaction ID: {self.general_history[self.view_index][2]}"
            product_bought = self.general_history[self.view_index][1]
            price = f"Cost: {self.general_history[self.view_index][3]}"
            self.history_badge = utilities.Badge(400, 200, 800, 600, (32, 34, 84, 255), (100, 255, 237, 255), 
                                                (255, 111, 196, 255), (255, 255, 255, 255), product_bought, "\U000023F3", "Refund",
                                                description=f"{product_datetime} \n {transaction_str} \n {price}", 
                                                batch=self.interface)
        except IndexError:
            if len(self.datetime_history) != 0:
                self.view_index = -1
                self.show_history_badge()
            else:
                if not self.bool_glitchy_text_visible:
                    self.make_glitchy_no_history_label()
    def show_nav_buttons(self):
        self.left_nav_btn = utilities.Button("\U0000276E", 10, 400, 50, 50, self.interface, (255, 215, 0, 255), 25)
        self.right_nav_btn = utilities.Button("\U0000276F", 1540, 400, 50, 50, self.interface, (255, 215, 0, 255), 25)
    def show_history(self):
        self.main_view = False
        self.translucent_layer.opacity = 100
        self.cross_button = utilities.Button('\U00002716', 1530, self.pellet_label.y - 75, 60, 50,
                                             self.interface, (255, 82, 82, 255), 25, self.emoji_font)
        self.show_history_badge()
        for _ in range(499):
            self.send_mouse_scroll(1)
        self.info_label = None
        self.show_nav_buttons()
    def hide_history(self):
        self.main_view = True
        self.translucent_layer.opacity = 0
        self.cross_button = None
        self.history_badge = None
        for _ in range(499):
            self.send_mouse_scroll(-1)
        self.info_label = pyglet.text.Label('Shop | Sector Eight',
                                            font_name="Merriweather Sans",
                                            weight="light",
                                            font_size=70,
                                            x=11,
                                            y=580,
                                            batch=self.interface,
                                            color=(230, 230, 230, 230, 255))
        self.view_index = -1
        self.left_nav_btn = None
        self.right_nav_btn = None
        if self.miami_glitch_text:
            self.miami_glitch_text.clear()
            self.miami_glitch_text = None
        
    def make_glitchy_no_history_label(self):
        self.miami_glitch_text = utilities.MiamiGlitchLabel(self.WINDOW, 
                                                            '404 ERROR: NO HISTORY AVAILABLE',
                                                            self.interface,
                                                            subtitle_text="CLICK \U00002716 BUTTON TO RETURN",
                                                            subtitle=True, 
                                                            frag_text_list=['NO HISTORY', 
                                                                            'OOPS! 404 ERROR',
                                                                            ''])
    def go_left(self):
        self.play(music_file=self.configObj.toml_dict['music']['shopHistoryBrowse'])
        self.view_index += 1
        self.show_history_badge()
    def go_right(self):
        self.play(music_file=self.configObj.toml_dict['music']['shopHistoryBrowse'])
        self.view_index -= 1
        self.show_history_badge()
    def refund(self, trans_id):
        for index, _id in enumerate(self.history_instance.get_trans_id_history()):
            if _id == trans_id:
                break
        else:
            # In this case the transaction ID provided is not present in the log.
            raise tastyerrors.LogicError('Transaction ID provided to refund() isn\'t valid')
        item_history = self.general_history[index]
        item = item_history[1]
        item_price = item_history[3]
        spl_effects = [self.laser_powers, 
                       self.xp_speedups, 
                       self.powerups, 
                       self.invisible_powers, 
                       self.extra_lives]
        
        self.pellets += int(item_price)
        self.pellet_label.text = f"Pellets: {self.pellets}"
        self.sync_data('pellets', self.pellets)
        if item == "Laser Boost" and self.laser_powers != 0:
            self.laser_powers -= 1
            self.sync_data("laser", self.laser_powers)
        elif item == "XP Speedups" and self.xp_speedups != 0:
            self.xp_speedups -= 1
            self.sync_data('xp', self.xp_speedups)
        elif item == "Powerups" and self.powerups != 0:
            self.powerups -= 1
            self.sync_data('powerups', self.powerups)
        elif item == "Invisibility" and self.invisible_powers != 0:
            self.invisible_powers -= 1
            self.sync_data('invisibility', self.invisible_powers)
        elif item == "Extra Life" and self.extra_lives != 0:
            self.extra_lives -= 1
            self.sync_data('extra_lives', self.extra_lives)
        del self.log[index]
        self.log_file['log'] = self.log
        self.log_file.sync()
        self.play(music_file=self.configObj.toml_dict['music']['shopBuySuccess'])
        self.hide_history()
        self.show_history()
    def change_theme(self, theme):
        self.background = self.theme_backgrounds[theme]
        self.sync_data('background', self.background)
        if 'Light' in theme:
             self.info_label = pyglet.text.Label('Shop | Sector Eight',
                                            font_name="Merriweather Sans",
                                            weight="light",
                                            font_size=70,
                                            x=11,
                                            y=580,
                                            batch=self.interface,
                                            color=(25, 25, 25, 255))
        else:
            self.info_label = pyglet.text.Label('Shop | Sector Eight',
                                        font_name="Merriweather Sans",
                                        weight="light",
                                        font_size=70,
                                        x=11,
                                        y=580,
                                        batch=self.interface,
                                        color=(230, 230, 230, 230, 255))
    def init_window(self):
        
        self.ruler = pyglet.shapes.Line(-10, self.ruler_y,  self.ruler_x + 100_000, self.ruler_y,
                                        thickness = 2.0, color = (30, 189, 200, 200), batch=self.interface)
        self.make_recommended_item()
        for i, item in enumerate(self.available_items):
            if i == 0:
                item_badge = utilities.Badge(
                    self.vr1.x + 20,
                    0, 800, self.ruler_y, item.bg_color, (150, 200, 150, 225), (200, 200, 200), (0, 0, 0, 225),
                    item.item_name, item.item_esc_char, f"Buy for {item.item_price}P", batch=self.interface
                )
                self.badge_list.append(item_badge)
            elif i != 0:
                item_badge = utilities.Badge(
                    self.badge_list[i - 1].x + 900,
                    0, 800, self.ruler_y, item.bg_color, (150, 200, 150, 225), (200, 200, 200), (0, 0, 0, 225),
                    item.item_name, item.item_esc_char, f"Buy for {item.item_price}P", batch=self.interface
                )
                self.badge_list.append(item_badge)
        self.vr2.x = self.vr2.x2 = (self.badge_list[-1].x) + (self.badge_list[-1].width) + 100
        self.info_label = pyglet.text.Label('Shop | Sector Eight',
                                            font_name="Merriweather Sans",
                                            weight="light",
                                            font_size=70,
                                            x=11,
                                            y=580,
                                            batch=self.interface,
                                            color=(230, 230, 230, 230, 255))
        
        
        self.add_scrolllist([self.picks_label,
                             self.ruler,
                             self.vr1,
                             self.product_label])
        self.add_scrolllist(self.badge_list)
        self.add_scrolllist(self.rec_badge)    
        self.make_option_buttons()
        for index in range(len(list(self.theme_backgrounds.keys()))):
            bg = list(self.theme_backgrounds.values())[index]
            if bg == self.background:
                break
        else: # No matching color found!
            index = list(self.theme_backgrounds.keys()).index('Neon Mania')
        self.theme_dropdown = utilities.DropDownMenu(self.WINDOW, self.history_button.x - 10, 
                                                     self.pellet_label.y - 100,
                                                     400, 40, list(self.theme_backgrounds.keys()), 
                                                     batch=self.interface, 
                                                     on_select=self.change_theme, accent_color=(150, 150, 150, 255),
                                                     default_index=index)
        self.translucent_layer = pyglet.shapes.Rectangle(x=0, y=0, width=self.WINDOW.width, height=self.WINDOW.height, 
                                                         color=(0, 0, 0), batch=self.interface)
        self.translucent_layer.opacity = 0
    
    def update(self, dt):
        for obj in self.scroll_objects:
            if hasattr(obj, 'update'):
                obj.update(dt)
        self.id_label.text = f"Latest Transaction ID: {self.transaction_id}"
        self.product_names = {"Laser Boost": 'laser', 
                              "XP Speedups": 'xp', 
                              "Powerups": 'powerups', 
                              "Invisibility": 'invisibility', 
                              "Extra Life": 'extra_lives',
                              }
        self.theme_backgrounds['Neon Mania'] = (random.random(), random.random(), random.random(), 1.0)
    
    def get_batch(self):
        return self.interface
    def start(self):
        self.play()
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()
