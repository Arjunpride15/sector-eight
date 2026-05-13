import pyglet
import conf
import math

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
    def __init__(self, text, x, y, width, height, batch, colour ,radius=15, font_name=font_list, font_size=18):
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
            color=(255, 255, 255, 255),
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
                                          font_name=confObj.toml_dict['font']['fontList'], font_size=9,
                                          color=(255, 255, 255, 180), # Dimmer white
                                          x=x + width // 2, y=y + 75,
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