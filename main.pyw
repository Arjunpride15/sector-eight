import pyglet
import canvas
# Load stuff.
window = pyglet.window.Window(width=1600,height=800,caption="Sector 8")

main_batch = pyglet.graphics.Batch()
LIST_INTERFACE = list()

    


@window.event
def on_draw():
    # Clear the window to avoid drawing over previous frames
    window.clear()
    
    PlayMusic.player.play()

            
    main_batch.draw()
    



pyglet.app.run()
