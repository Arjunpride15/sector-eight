
import pyglet
from pyglet.window import key, mouse
import shop_backend
import utilities

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
    if shop_instance.main_view:
        # Calculate intended move
        move = 20 if scroll_y < 0 else -20
        
        # Check if the NEW offset would be in bounds
        if shop_instance.max_scroll >= (shop_instance.offset_x + move) >= shop_instance.min_scroll:
            shop_instance.offset_x += move
            for sprite in shop_instance.scroll_objects:
                sprite.x += move
            
@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        if shop_instance.main_view:
            for badge in shop_instance.badge_list:
                # Check if the mouse click is within the badge's button boundaries
                if badge.is_clicked(x, y):
                    #print(f"Purchasing: {badge.title.text}")
                    shop_instance.buy(badge.title.text)
            if shop_instance.rec_badge.is_clicked(x, y):
                shop_instance.buy(shop_instance.rec_badge.title.text, 
                                discount=shop_instance.item_discount)
            if shop_instance.home_button.is_clicked(x, y):
                shop_instance.home()
            if shop_instance.game_button.is_clicked(x, y):
                shop_instance.game()
            if shop_instance.query_button.is_clicked(x, y):
                shop_instance.query()
            if shop_instance.history_button.is_clicked(x, y):
                shop_instance.show_history()
        else:
            if shop_instance.cross_button.is_clicked(x, y):
                shop_instance.hide_history()
            if shop_instance.left_nav_btn.is_clicked(x, y):
                shop_instance.go_left()
            if shop_instance.right_nav_btn.is_clicked(x, y):
                shop_instance.go_right()
            if shop_instance.history_badge.is_clicked(x, y):
                _id = int(shop_instance.general_history[shop_instance.view_index][2])
                shop_instance.refund(_id)
@window.event
def on_mouse_motion(x, y, dx, dy):
    if not shop_instance.main_view:
        if shop_instance.left_nav_btn:
            if shop_instance.left_nav_btn.is_clicked(x, y):
                shop_instance.left_nav_btn.delete()
                shop_instance.left_nav_btn = utilities.Button("\U0000276E", 10, 400, 50, 50, 
                                                              shop_instance.get_batch(), (225, 225, 225, 225), 25)
            else:
                shop_instance.left_nav_btn.delete()
                shop_instance.left_nav_btn = utilities.Button("\U0000276E", 10, 400, 50, 50, shop_instance.get_batch(), 
                                                              (255, 215, 0, 255), 25)
        if shop_instance.right_nav_btn:
            if shop_instance.right_nav_btn.is_clicked(x, y):
                shop_instance.right_nav_btn.delete()
                shop_instance.right_nav_btn = utilities.Button("\U0000276F", 1540, 400, 50, 50, 
                                                      shop_instance.get_batch(), (225, 225, 225, 255), 25)
            else:
                shop_instance.right_nav_btn.delete()
                shop_instance.right_nav_btn = utilities.Button("\U0000276F", 1540, 400, 50, 50, shop_instance.get_batch(), 
                                                      (255, 215, 0, 255), 25)
        
@window.event
def on_key_press(symbol, modifiers):
    if shop_instance.main_view:
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
                    #print(".")
        
@window.event
def on_close():
    shop_instance.stop_music()
    # Safely close the shelf to save data
    if hasattr(shop_instance, 'data_storage'):
        shop_instance.data_storage.close()
    
    # Close the window
    window.close()
shop_instance.start()