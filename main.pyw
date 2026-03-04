 
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
# Load stuff.
pyglet.options['audio_buffer_size'] = 8192
window = pyglet.window.Window(width=1600,height=800,caption="Sector 8")

main_batch = pyglet.graphics.Batch()
se = canvas.SectorEight(main_batch)
    

se.play_main_music_file()
@window.event
def on_draw():
    
    # Clear the window to avoid drawing over previous frames
    window.clear()
    se.canvas_init()    
    main_batch.draw()
eater = se.return_eater()
    
@window.event
def on_close():
    se.stop_music()
@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.UP:
        game.direction = (0, 1)
    elif symbol == key.DOWN:
        game.direction = (0, -1)
    elif symbol == key.LEFT:
        game.direction = (-1, 0)
    elif symbol == key.RIGHT:
        game.direction = (1, 0)
    


   
se.start_()
