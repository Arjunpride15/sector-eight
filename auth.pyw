import pyglet
from pyglet.window import key, mouse
import auth_backend

window = pyglet.window.Window(width=950, height=900, 
                              caption="Authentication Manager | Sector 8", style="dialog")
pyglet.gl.glClearColor(0.2, 0.2, 0.35, 1)
screen = window.display.get_default_screen()
x_pos = (screen.width - window.width) // 2
y_pos = (screen.height - window.height) // 2
window.set_location(x_pos, y_pos)
#icon_16 = pyglet.image.load('images/icon-16.png')
#icon_32 = pyglet.image.load('images/icon-32.png')
#window.set_icon(icon_16, icon_32)
auth_obj = auth_backend.SectorEightAuthManager(window)
if auth_obj.configObj.toml_dict["performance"]["VSync"]:
    window.set_vsync(True)
else:
    window.set_vsync(False)  
auth_obj.init_window()
@window.event
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(*auth_obj.background)
    auth_obj.interface.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    try:
        auth_obj.text_box.handle_click(x, y)
    except AttributeError:
        ...
    auth_obj._handle_mouse_press(x, y, button, modifiers)
    
@window.event
def on_text(text):
    try:
        # Pass character keypresses to active text box
        auth_obj.text_box.handle_text_input(text)
    except AttributeError:
        ...
    

@window.event
def on_key_press(symbol, modifiers):
    try:
        # Handle deletions
        if symbol == key.BACKSPACE:
            auth_obj.text_box.handle_backspace()
    except AttributeError:
        ...

@window.event
def on_close():
    try:
        auth_obj.data_storage.close()
    except Exception:
        ...
    try:
        auth_obj.auth_db.close()
    except Exception:
        ...
    window.close()

auth_obj.start()