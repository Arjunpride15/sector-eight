import pyglet

def coord_distance(x1, y1, x2, y2):
    num1 = (int(x2) - int(x1)) ** 2
    num2 = (int(y2) - int(y1)) ** 2
    result = (num1 + num2) ** 0.5
    return result

class Button:
    def __init__(self, text, x, y, width, height, batch, colour ,font_name='Cascadia Mono', font_size=18):
        """
        A simple reusable button for Pyglet.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # The background of the button
        self.shape = pyglet.shapes.Rectangle(
            x, y, width, height, 
            color=colour, 
            batch=batch
        )
        self.shape.opacity = 200

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
        self.shape.opacity = opacity
        self.label.color = (255, 255, 255, text_opacity)

    def delete(self):
        """
        Properly clean up the sprites from the batch.
        """
        self.shape.delete()
        self.label.delete()