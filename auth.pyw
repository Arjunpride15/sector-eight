import pyglet
from pyglet.window import key, mouse
import auth_backend

window = pyglet.window.Window(width=950, height=900, 
                              caption="Authentication Manager | Sector 8", style="dialog")
pyglet.gl.glClearColor(0.2, 0.2, 0.35, 1)

auth_obj = auth_backend.SectorEightAuthManager(window)
auth_obj.main_init_window()
@window.event
def on_draw():
    window.clear()
    auth_obj.interface.draw()

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