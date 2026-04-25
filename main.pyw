 
# Copyright 2026 Arjun Singh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pyglet
import canvas
import threading
from pyglet.window import key
import sys
import time

# Load stuff.
window = pyglet.window.Window(width=1600,height=850,caption="Sector 8")


se = canvas.SectorEight(window)
    


se.canvas_init()
pyglet.clock.schedule_interval(se.play_main_music_file, 43)  
@window.event
def on_draw():
    
    # Clear the window to avoid drawing over previous frames
    window.clear()
    se.interface.draw()

    
@window.event
def on_close():
    se.stop_music()
    # Safely close the shelf to save data
    if hasattr(se, 'data_store'):
        se.data_store.close()
    
    # Close the window
    window.close()
    
@window.event
def on_key_press(symbol, modifiers):
    if se.eater_sprite:
        if symbol == key.UP or symbol == key.W:
            se.direction = (0, 1)
        elif symbol == key.DOWN or symbol == key.S:
            se.direction = (0, -1)
        elif symbol == key.LEFT or symbol == key.A:
            se.direction = (-1, 0)
        elif symbol == key.RIGHT or symbol == key.D:
            se.direction = (1, 0)
        elif symbol == key.SPACE:
            se.laser()
        elif symbol == key.TAB:
            se.xp_speed()
        elif symbol == key.RETURN:
            se.powerup()
        elif symbol == key.LSHIFT or symbol == key.RSHIFT:
            se.invisible_power()
@window.event
def on_key_release(symbol, modifiers):
    if se.eater_sprite:
        if symbol == key.SPACE:
            se.laser_obj = None
@window.event
def on_mouse_press(x, y, button, modifiers):
    if not se.game_active and se.restart_button.is_clicked(x, y):
        se.restart_game()    


   
se.start_()
