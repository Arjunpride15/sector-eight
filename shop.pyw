
import pyglet
from pyglet.window import key, mouse
import shop_backend


window = pyglet.window.Window(width=1600,height=850,caption="Shop | Sector 8")

#                     (r, g, b, a)
pyglet.gl.glClearColor(0.5, 0.5, 0.5, 1)

shop_instance = shop_backend.SectorEightShop(window)
shop_instance.init_window()
@window.event
def on_draw():
    
    # Clear the window to avoid drawing over previous frames
    window.clear()
    shop_instance.interface.draw()
    
@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    for sprite in shop_instance.interface_objects:
        if scroll_y > 0:
            sprite.x += 10
        elif scroll_y < 0:
            sprite.x -= 10
@window.event
def on_key_press(symbol, modifiers):
    for sprite in shop_instance.interface_objects:
        if symbol == key.LEFT:
            sprite.x -= 50
        if symbol == key.RIGHT:
            sprite.x += 50
        
@window.event
def on_close():
    shop_instance.stop_music()
    # Safely close the shelf to save data
    if hasattr(shop_instance, 'data_storage'):
        shop_instance.data_storage.close()
    
    # Close the window
    window.close()
shop_instance.start()