import pyglet, shelve, webbrowser
from pyglet.window import key, mouse
import home_backend
from utilities import convertRGBAtoGL


window = pyglet.window.Window(width=1600,height=850,caption="Home | Sector 8")

pyglet.gl.glClearColor(0.2, 0.2, 0.35, 1)
window.set_vsync(True)
screen = window.display.get_default_screen()
x_pos = (screen.width - window.width) // 2
y_pos = (screen.height - window.height) // 2
window.set_location(x_pos, y_pos)
home_obj = home_backend.SectorEightHome(window)
home_obj.init_window()
#print(home_obj.theme_backgrounds.values())
@window.event
def on_draw():
    
    # Clear the window to avoid drawing over previous frames
    window.clear()
    pyglet.gl.glClearColor(*home_obj.background)
    home_obj.interface.draw()
    home_obj.mask_interface.draw()
    home_obj.header_interface.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        try:
            home_obj.avatar_dropdown.on_mouse_press(x, y, button, modifiers)
            home_obj.theme_dropdown.on_mouse_press(x, y, button, modifiers)
        except AttributeError:
            ...
        if home_obj.side_panel_btn != None:
            if home_obj.side_panel_btn.is_clicked(x, y):
                home_obj.toggle_side_panel()
            if home_obj.side_panel_visible:
                if home_obj.settings_button.is_clicked(x, y):
                    ...
                if home_obj.shop_btn.is_clicked(x, y):
                    home_obj.shop()
                if home_obj.game_btn.is_clicked(x, y):
                    home_obj.game()
                if home_obj.query_btn.is_clicked(x, y):
                    home_obj.query()
                if home_obj.logout_btn.is_clicked(x, y):
                    ...        
        if home_obj.cyclic_badge != None:
            if home_obj.left_nav_btn:
                if home_obj.left_nav_btn.is_clicked(x, y):
                    home_obj.cyclic_badge.go_left()
            if home_obj.right_nav_btn:
                if home_obj.right_nav_btn.is_clicked(x, y):
                    home_obj.cyclic_badge.go_right()
            if home_obj.cyclic_state_list[0] and home_obj.badge_1.is_clicked(x, y):
                home_obj.shop()
            elif home_obj.cyclic_state_list[1] and home_obj.badge_2.is_clicked(x, y):
                home_obj.logout()       
            elif home_obj.cyclic_state_list[2] and home_obj.badge_3.is_clicked(x, y):
                home_obj.query()
            elif home_obj.cyclic_state_list[3] and home_obj.badge_4.is_clicked(x, y):
                home_obj.game()     
        if home_obj.reward_badge != None:
            if home_obj.reward_badge.is_clicked(x, y):
                with shelve.open(r"data\miscn") as miscn:
                    if not miscn.get("claimed", False):
                        home_obj.reward_player() 
        if home_obj.err_reporting_label:
            if home_obj.issue_reporting_btn.is_clicked(x, y):
                webbrowser.open_new_tab("https://github.com/Arjunpride15/sector-eight/issues/new?template=bug_report.md")
            if home_obj.feature_btn.is_clicked(x, y):
                webbrowser.open_new_tab("https://github.com/Arjunpride15/sector-eight/issues/new?template=feature_request.md")

@window.event
def on_mouse_motion(x, y, dx, dy):
    try:
        home_obj.avatar_dropdown.on_mouse_motion(x, y, dx, dy)
        home_obj.theme_dropdown.on_mouse_motion(x, y, dx, dy)
    except AttributeError:
        ...
    
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