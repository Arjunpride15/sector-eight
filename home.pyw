import pyglet
from pyglet.window import key, mouse
import home_backend


window = pyglet.window.Window(width=1600,height=850,caption="Home | Sector 8")

pyglet.gl.glClearColor(0.2, 0.2, 0.35, 1)

home_obj = home_backend.SectorEightHome(window)
home_obj.init_window()
@window.event
def on_draw():
    
    # Clear the window to avoid drawing over previous frames
    window.clear()
    home_obj.interface.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        if home_obj.side_panel_btn.is_clicked(x, y):
            home_obj.toggle_side_panel()
@window.event
def on_close():
    home_obj.stop_music()
    # Safely close the shelf to save data
    if hasattr(home_obj, 'data_storage'):
        home_obj.data_storage.close()
    
    # Close the window
    window.close()

home_obj.start()