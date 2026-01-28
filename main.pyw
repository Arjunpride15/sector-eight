import pyglet


window = pyglet.window.Window(width=1600,height=800,caption="Sector 8")
image = pyglet.resource.image('images/eater.gif')
eater = pyglet.sprite.Sprite(img=image, x=100, y=50)

# The on_draw event is triggered whenever the window needs to be redrawn
class PlayMusic:
    sound = pyglet.media.load('audio/main-music.wav', streaming=False)

    # 2. Create a player and queue the sound
    player = pyglet.media.Player()
    player.queue(sound)

    # 3. Add functionalities
    player.volume = 0.5  # Set volume (0.0 to 1.0)
    player.loop = True   # Enable looping


@window.event
def on_draw():
    # Clear the window to avoid drawing over previous frames
    window.clear()
    eater.draw()
    PlayMusic.player.play()



pyglet.app.run()
