import pyglet
import settings_backend
from pyglet.window import key

window = pyglet.window.Window(width=1600,height=850,caption="Sector 8 Settings")
screen = window.display.get_default_screen()
x_pos = (screen.width - window.width) // 2
y_pos = (screen.height - window.height) // 2
window.set_location(x_pos, y_pos)

settings_obj = settings_backend.SectorEightSettings(window)
if settings_obj.configObj.toml_dict["performance"]["VSync"]:
    window.set_vsync(True)    
settings_obj.init_window() 
@window.event
def on_draw():
    pyglet.gl.glClearColor(*settings_obj.background)
    # Clear the window to avoid drawing over previous frames
    window.clear()
    
    settings_obj.interface.draw()
    settings_obj.mask_interface.draw()
    settings_obj.header_interface.draw()

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    if settings_obj.main_view:
        # Calculate intended move
        move = 20 if scroll_y < 0 else -20
        
        # Check if the NEW offset would be in bounds
        if settings_obj.min_scroll <= (settings_obj.offset_y + move) <= settings_obj.max_scroll:
            settings_obj.offset_y += move
            for sprite in settings_obj.scroll_objects:
                sprite.y += move

@window.event
def on_mouse_press(x, y, button, modifiers):
    settings_obj.handle_mouse_click(x, y, button, modifiers)

@window.event
def on_mouse_motion(x, y, dx, dy):
    if settings_obj.fps_dropdown:
        settings_obj.fps_dropdown.on_mouse_motion(x, y, dx, dy)
@window.event
def on_close():
    settings_obj.stop_music()
    # Safely close the shelf to save data
    if hasattr(settings_obj, 'data_storage'):
        settings_obj.data_storage.close()
    
    # Close the window
    window.close()

settings_obj.start()