
import pyglet
from pyglet.window import key, mouse
import shop_backend


window = pyglet.window.Window(width=1600,height=850,caption="Shop | Sector 8")

#                     (r, g, b, a)
pyglet.gl.glClearColor(0.2, 0.2, 0.35, 1)

shop_instance = shop_backend.SectorEightShop(window)
shop_instance.init_window()
@window.event
def on_draw():
    
    # Clear the window to avoid drawing over previous frames
    window.clear()
    shop_instance.interface.draw()
    
@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    # Calculate intended move
    move = 20 if scroll_y < 0 else -20
    
    # Check if the NEW offset would be in bounds
    if shop_instance.max_scroll >= (shop_instance.offset_x + move) >= shop_instance.min_scroll:
        shop_instance.offset_x += move
        for sprite in shop_instance.scroll_objects:
            sprite.x += move

@window.event
def on_key_press(symbol, modifiers):
    move = 0
    if symbol == key.LEFT:
        move = 50
    elif symbol == key.RIGHT:
        move = -50
        
    if move != 0:
        if shop_instance.max_scroll >= (shop_instance.offset_x + move) >= shop_instance.min_scroll:
            shop_instance.offset_x += move
            for sprite in shop_instance.scroll_objects:
                sprite.x += move
        
@window.event
def on_close():
    shop_instance.stop_music()
    # Safely close the shelf to save data
    if hasattr(shop_instance, 'data_storage'):
        shop_instance.data_storage.close()
    
    # Close the window
    window.close()
shop_instance.start()