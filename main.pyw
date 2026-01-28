import pyglet


window = pyglet.window.Window(width=1200,height=800,caption="Sector 8")
image = pyglet.resource.image('images/eater.gif')
eater = pyglet.sprite.Sprite(img=image, x=100, y=50)


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
    eater.draw()
    PlayMusic.player.play()



pyglet.app.run()
