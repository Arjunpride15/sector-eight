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
    home_obj.mask_interface.draw()
    home_obj.header_interface.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        if home_obj.side_panel_btn != None:
            if home_obj.side_panel_btn.is_clicked(x, y):
                home_obj.toggle_side_panel()
        if home_obj.cyclic_badge != None:
            if home_obj.left_nav_btn:
                if home_obj.left_nav_btn.is_clicked(x, y):
                    home_obj.cyclic_badge.go_left()
            if home_obj.right_nav_btn:
                if home_obj.right_nav_btn.is_clicked(x, y):
                    home_obj.cyclic_badge.go_right()

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    if home_obj.main_view:
        # Calculate intended move
        move = 20 if scroll_y < 0 else -20
        
        # Check if the NEW offset would be in bounds
        if home_obj.min_scroll <= (home_obj.offset_y + move) <= home_obj.max_scroll:
            home_obj.offset_y += move
            for sprite in home_obj.scroll_objects:
                sprite.y += move
@window.event
def on_close():
    home_obj.stop_music()
    # Safely close the shelf to save data
    if hasattr(home_obj, 'data_storage'):
        home_obj.data_storage.close()
    if hasattr(home_obj, "log_file"):
        home_obj.log_file.close()
    
    # Close the window
    window.close()
    

home_obj.start()