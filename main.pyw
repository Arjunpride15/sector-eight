 
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
# Load stuff.
window = pyglet.window.Window(width=1600,height=800,caption="Sector 8")

main_batch = pyglet.graphics.Batch()
LIST_INTERFACE = list()
se = canvas.SectorEight(main_batch, LIST_INTERFACE)
    

threading.Thread(target=se.play_main_music_file, daemon=True).start()
@window.event
def on_draw():
    # Clear the window to avoid drawing over previous frames
    window.clear()
    se.canvas_init()
    main_batch.draw()


   
se.start_()
