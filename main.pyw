import pyglet
import tastyerrors
import grid
import time
# Load stuff.
window = pyglet.window.Window(width=1600,height=800,caption="Sector 8")

interface = pyglet.graphics.Batch()
LIST_INTERFACE = list()

# The class which plays music.
class PlayMusic:
    sound = pyglet.media.load('audio/main-music.wav', streaming=False)

    
    player = pyglet.media.Player()
    player.queue(sound)

    
    player.volume = 0.5  # Set volume (0.0 to 1.0)
    player.loop = True   # Enable looping


@window.event
def on_draw():
    # Clear the window to avoid drawing over previous frames
    window.clear()
    
    PlayMusic.player.play()
    map_ = grid.identify()
    coord_x = 0
    coord_y = 0
    for code in map_:
        if code == 'wall':
            LIST_INTERFACE.append(pyglet.sprite.Sprite(img=(pyglet.resource.image('images/tile.gif')), x=(coord_x * 40), y=(coord_y * 40), batch=interface))
            coord_x += 1
        elif code == 'blacktile':
            LIST_INTERFACE.append(pyglet.sprite.Sprite(img=(pyglet.resource.image('images/blacktile.gif')), x=(coord_x * 40), y=(coord_y * 40), batch=interface))
            coord_x += 1
        elif code == 'eater':
            player = pyglet.sprite.Sprite(img=(pyglet.resource.image('images/eater.gif')), x=(coord_x * 40), y=(coord_y * 40), batch=interface)
            LIST_INTERFACE.append(player)
        if code == 'newline':
            coord_x = 0
            coord_y += 1
            
    interface.draw()
    



pyglet.app.run()
