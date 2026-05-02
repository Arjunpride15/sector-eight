import pyglet
import conf

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