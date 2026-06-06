import pyglet
import conf
import math
import random

confObj = conf.Config()
font_list = confObj.toml_dict['font']['fontList']
def coord_distance(x1, y1, x2, y2):
    num1 = (int(x2) - int(x1)) ** 2
    num2 = (int(y2) - int(y1)) ** 2
    result = (num1 + num2) ** 0.5
    return result


class RoundedRectangle:
    def __init__(self, x, y, width, height, radius, color, batch):
        """
        A class for creating rounded rectangles.
        """
        self.shapes = []
        
        # 1. The core "cross" (two overlapping rectangles)
        # Horizontal piece
        self.shapes.append(pyglet.shapes.Rectangle(
            x + radius, y, width - 2*radius, height, color=color, batch=batch))
        # Vertical piece
        self.shapes.append(pyglet.shapes.Rectangle(
            x, y + radius, width, height - 2*radius, color=color, batch=batch))
        
        # 2. The four corner sectors to round it off
        # Bottom-Left
        self.shapes.append(pyglet.shapes.Sector(
            x + radius, y + radius, radius, angle=90, start_angle=180, color=color, batch=batch))
        # Bottom-Right
        self.shapes.append(pyglet.shapes.Sector(
            x + width - radius, y + radius, radius, angle=90, start_angle=270, color=color, batch=batch))
        # Top-Left
        self.shapes.append(pyglet.shapes.Sector(
            x + radius, y + height - radius, radius, angle=90, start_angle=90, color=color, batch=batch))
        # Top-Right
        self.shapes.append(pyglet.shapes.Sector(
            x + width - radius, y + height - radius, radius, angle=90, start_angle=0, color=color, batch=batch))

    def set_opacity(self, opacity):
        for shape in self.shapes:
            shape.opacity = opacity

    def delete(self):
        for shape in self.shapes:
            shape.delete()

class Button:
    def __init__(self, text, x, y, width, height, batch, colour 
                 ,radius=15, font_name=font_list, font_size=18, text_color=(255, 255, 255, 255)):
        """
        A simple reusable button for Pyglet.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # The background of the button
        self.shape = RoundedRectangle(
            x, y, width, height, radius, color=colour, batch=batch
        )
        try:
            if colour[3]:
                pass
            else:
                self.shape.set_opacity(200)
        except IndexError:
            pass

        # The text label centered on the button
        self.label = pyglet.text.Label(
            text,
            font_name=font_name,
            font_size=font_size,
            x=x + (width // 2),
            y=y + (height // 2),
            anchor_x='center',
            anchor_y='center',
            color=text_color,
            batch=batch
        )

    def is_clicked(self, mouse_x, mouse_y):
        """
        Checks if a mouse click coordinate falls within the button's rectangle.
        """
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)

    def set_visible(self, visible):
        """
        Quickly toggle the button's visibility.
        """
        opacity = 200 if visible else 0
        text_opacity = 255 if visible else 0
        self.shape.set_opacity(opacity)
        self.label.color = (255, 255, 255, text_opacity)

    def delete(self):
        """
        Properly clean up the sprites from the batch.
        """
        self.shape.delete()
        self.label.delete()

class Badge:
    def __init__(self, x, y, width, height,
                 bg_color, btn_color, emoji_color, main_text_color,
                 main_text, emoji, btn_text, 
                 description=None, bob=False, batch=None, emoji_font=confObj.toml_dict['font']['emojiFont']):
        
        self._x = x
        self._y = y
        self.base_y = y  # Stored for the bobbing animation
        self.width = width
        self.height = height
        self.bob = bob
        self.time = 0
        
        # 1. Background Rectangle
        self.bg = pyglet.shapes.Rectangle(x, y, width, height, color=bg_color, batch=batch)
        
        # 2. Main Title (Top Centered)
        self.title = pyglet.text.Label(main_text,
                                       font_name=confObj.toml_dict['font']['fontList'], font_size=25, weight="ultrabold",
                                       color=main_text_color,
                                       x=x + width // 2, y=y + height - 20,
                                       anchor_x='center', anchor_y='top',
                                       batch=batch)
        
        # 3. Big Emoji (Center)
        self.emoji_label = pyglet.text.Label(emoji,
                                             font_name=emoji_font, font_size=40,
                                             color=emoji_color,
                                             x=x + width // 2, y=y + height // 2 + 10,
                                             anchor_x='center', anchor_y='center',
                                             batch=batch)

        # 4. Description (Optional)
        self.desc = None
        if description:
            self.desc = pyglet.text.Label(description,
                                          font_name=confObj.toml_dict['font']['fontList'], font_size=20,
                                          color=(255, 255, 255, 180), # Dimmer white
                                          x=x + width // 2, y=y + 130,
                                          anchor_x='center', anchor_y='center',
                                          multiline=True, width=width-20,
                                          batch=batch)

        # 5. Button (Visual representation)
        btn_h = 35
        self.btn_bg = pyglet.shapes.Rectangle(x + 20, y + 15, width - 40, btn_h, 
                                              color=btn_color, batch=batch)
        self.btn_text = pyglet.text.Label(btn_text,
                                           font_name=confObj.toml_dict['font']['fontList'], font_size=20, 
                                           color=(255, 255, 255, 255),
                                           x=x + width // 2, y=y + 15 + (btn_h // 2),
                                           anchor_x='center', anchor_y='center',
                                           batch=batch)

    # Property for X: Moves ALL sub-elements when badge.x is changed
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        dx = value - self._x
        self._x = value
        self.bg.x += dx
        self.title.x += dx
        self.emoji_label.x += dx
        self.btn_bg.x += dx
        self.btn_text.x += dx
        if self.desc:
            self.desc.x += dx

    # Property for Y: Used for the bobbing animation
    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        dy = value - self._y
        self._y = value
        self.bg.y += dy
        self.title.y += dy
        self.emoji_label.y += dy
        self.btn_bg.y += dy
        self.btn_text.y += dy
        if self.desc:
            self.desc.y += dy

    def update(self, dt):
        """Call this in your shop's update loop if bob=True"""
        if self.bob:
            self.time += dt
            # Calculate a smooth sine wave for the hover effect
            new_y = self.base_y + math.sin(self.time * 3) * 8
            self.y = new_y

    def is_clicked(self, mouse_x, mouse_y):
        """Detects if the mouse clicked the BUTTON area specifically"""
        return (self.btn_bg.x <= mouse_x <= self.btn_bg.x + self.btn_bg.width and
                self.btn_bg.y <= mouse_y <= self.btn_bg.y + self.btn_bg.height)

class MiamiGlitchLabel:
    """
    A class for making absolute glitchy text using Chromatic Aberration. :-)
    If `coords` argument isn't provided, the text defaults to center.
    This class is primarily used in the glitchy 'No History' label.
    """
    def __init__(self, window, text, batch,subtitle_text=None, 
                 subtitle=False, coords=None, frag_text_list=None,font_name=font_list, font_size=36):
        self.text = text
        self.subtitle_text = subtitle_text
        self.bool_subtitle = subtitle
        self.window = window
        self.font_name = font_name
        self.font_size = font_size
        self.interface = batch
        if frag_text_list:
            self.frag_text_list = frag_text_list
            self.fragments = True
        else:
            self.frag_text_list = []
            self.fragments = False
        try:
            self.x = coords[0]
            self.y = coords[1]
        except Exception:
            self.x = self.window.width // 2
            self.y = self.window.height // 2
        self.setup_miami_glitch_ui()
        pyglet.clock.schedule_interval(func=self.update_glitch, interval=1/60)
    def setup_miami_glitch_ui(self):
        """Creates a high-fidelity 5-layer chromatic aberration text stack for empty states."""
        center_x = self.x
        center_y = self.y
        
        glitch_text = self.text
        font_size = self.font_size
        f_name = self.font_name
        
        # 1. DEEP BLACK SHADOW LAYER (For maximum readability against game backgrounds)
        self.glitch_shadow = pyglet.text.Label(
            glitch_text, font_name=f_name, font_size=font_size, weight="bold",
            x=center_x + 2, y=center_y - 2, anchor_x='center', anchor_y='center',
            color=(15, 15, 25, 255), batch=self.interface
        )
        
        # 2. CYAN LAYER (Far Left Offset)
        self.glitch_cyan = pyglet.text.Label(
            glitch_text, font_name=f_name, font_size=font_size, weight="bold",
            x=center_x - 6, y=center_y + 2, anchor_x='center', anchor_y='center',
            color=(0, 240, 255, 200), batch=self.interface
        )
        
        # 3. LIME GREEN LAYER (Mid Left Offset)
        self.glitch_green = pyglet.text.Label(
            glitch_text, font_name=f_name, font_size=font_size, weight="bold",
            x=center_x - 3, y=center_y - 1, anchor_x='center', anchor_y='center',
            color=(57, 255, 20, 180), batch=self.interface
        )
        
        # 4. ELECTRIC PURPLE LAYER (Mid Right Offset)
        self.glitch_purple = pyglet.text.Label(
            glitch_text, font_name=f_name, font_size=font_size, weight="bold",
            x=center_x + 3, y=center_y + 1, anchor_x='center', anchor_y='center',
            color=(186, 85, 211, 180), batch=self.interface
        )
        
        # 5. NEON MAGENTA LAYER (Far Right Offset)
        self.glitch_magenta = pyglet.text.Label(
            glitch_text, font_name=f_name, font_size=font_size, weight="bold",
            x=center_x + 6, y=center_y - 2, anchor_x='center', anchor_y='center',
            color=(255, 0, 127, 200), batch=self.interface
        )
        
        # 6. FOREGROUND CORE LAYER (Stable Center)
        self.glitch_white = pyglet.text.Label(
            glitch_text, font_name=f_name, font_size=font_size, weight="bold",
            x=center_x, y=center_y, anchor_x='center', anchor_y='center',
            color=(255, 255, 255, 255), batch=self.interface
        )
        
        # --- THE RANDOM FRAGMENT SPLIT LABELS ---
        # These start completely transparent (opacity=0) and hidden off-screen!
        if self.fragments:
            self.fragment_left = pyglet.text.Label(
                random.choice(self.frag_text_list), font_name=f_name, font_size=font_size, weight="bold",
                x=center_x, y=center_y, anchor_x='center', anchor_y='center',
                color=(0, 240, 255, 0), batch=self.interface
            )
            self.fragment_right = pyglet.text.Label(
                random.choice(self.frag_text_list), font_name=f_name, font_size=font_size, weight="bold",
                x=center_x, y=center_y, anchor_x='center', anchor_y='center',
                color=(255, 0, 127, 0), batch=self.interface
            )
        if self.bool_subtitle:
            # Instruction Subtitle
            self.glitch_sub = pyglet.text.Label(
                self.subtitle_text,
                font_name=f_name, font_size=16, x=center_x, y=center_y - 100,
                anchor_x='center', anchor_y='center', color=(255, 215, 0, 150),
                batch=self.interface
            )
        
    def update_glitch(self, dt):
        if hasattr(self, 'glitch_white') and self.glitch_white is not None:
            center_x = self.window.width // 2
            center_y = self.window.height // 2
            
            dice_roll = random.random()
            
            # CONDITION A: The Ultimate Tear/Split Event (3% chance per frame)
            if dice_roll < 0.03:
                # Hide the clean center white label completely to simulate hardware failure!
                self.glitch_white.color = (255, 255, 255, 0)
                
                # Snap the 5 aberration layers into extreme wild tracking offsets
                self.glitch_cyan.x = center_x - random.randint(20, 40)
                self.glitch_magenta.x = center_x + random.randint(20, 40)
                self.glitch_green.y = center_y + random.randint(10, 20)
                self.glitch_purple.y = center_y - random.randint(10, 20)
                if self.fragments:
                    # REVEAL THE TWO FRAGMENT LABELS flying apart!
                    self.fragment_left.x = center_x - random.randint(50, 120)
                    self.fragment_left.y = center_y + random.randint(-15, 15)
                    self.fragment_left.color = (0, 240, 255, 255) # High opacity Cyan text fragment
                    
                    self.fragment_right.x = center_x + random.randint(50, 120)
                    self.fragment_right.y = center_y + random.randint(-15, 15)
                    self.fragment_right.color = (255, 0, 127, 255) # High opacity Magenta text fragment
                
            # CONDITION B: Standard Micro-Jitter (15% chance if not splitting)
            elif dice_roll < 0.18:
                # Keep fragments completely hidden/invisible
                if self.fragments:
                    self.fragment_left.color = (0, 240, 255, 0)
                    self.fragment_right.color = (255, 0, 127, 0)
                self.glitch_white.color = (255, 255, 255, 255) # Foreground visible
                
                # Standard tight aberrations twitching
                t_x = random.randint(-8, 8)
                t_y = random.randint(-4, 4)
                
                self.glitch_cyan.x = (center_x - 6) + t_x
                self.glitch_magenta.x = (center_x + 6) - t_x
                self.glitch_green.x = (center_x - 3) + (t_x // 2)
                self.glitch_purple.x = (center_x + 3) - (t_x // 2)
                self.glitch_cyan.y = (center_y + 2) + t_y
                
            # CONDITION C: Return to beautiful stable resting Chromatic Aberration
            else:
                if self.fragments:
                    self.fragment_left.color = (0, 240, 255, 0)
                    self.fragment_right.color = (255, 0, 127, 0)
                self.glitch_white.color = (255, 255, 255, 255)
                self.glitch_cyan.x = center_x - 6
                self.glitch_cyan.y = center_y + 2
                self.glitch_green.x = center_x - 3
                self.glitch_green.y = center_y - 1
                self.glitch_purple.x = center_x + 3
                self.glitch_purple.y = center_y + 1
                self.glitch_magenta.x = center_x + 6
                self.glitch_magenta.y = center_y - 2        
        
    def clear(self):
        if hasattr(self, 'glitch_white') and self.glitch_white is not None:
            pyglet.clock.unschedule(func=self.update_glitch)
            if self.fragments:
                if self.bool_subtitle:
                    del_list = [self.glitch_shadow, self.glitch_cyan, self.glitch_green, 
                            self.glitch_purple, self.glitch_magenta, self.glitch_white, 
                            self.fragment_left, self.fragment_right, self.glitch_sub]
                else:
                    del_list = [self.glitch_shadow, self.glitch_cyan, self.glitch_green, 
                            self.glitch_purple, self.glitch_magenta, self.glitch_white, 
                            self.fragment_left, self.fragment_right]
            else:
                if self.bool_subtitle:
                    del_list = [self.glitch_shadow, self.glitch_cyan, self.glitch_green, 
                            self.glitch_purple, self.glitch_magenta, self.glitch_white, 
                            self.glitch_sub]
                else:
                    del_list = [self.glitch_shadow, self.glitch_cyan, self.glitch_green, 
                        self.glitch_purple, self.glitch_magenta, self.glitch_white]
                
            # Delete every single element safely
            for index, label in enumerate(del_list):
                if label is not None:
                    label.delete()
                    del del_list[index]
                    
            # Wipe variables
            self.glitch_white = None            