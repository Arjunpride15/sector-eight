import pyglet

# Create a window of size 800x600 pixels with a title
window = pyglet.window.Window(width=800, height=600, caption="Sector 8")
image = pyglet.resource.image('images/eater.gif')
eater = pyglet.sprite.Sprite(img=image, x=100, y=50)

# The on_draw event is triggered whenever the window needs to be redrawn
@window.event
def on_draw():
    # Clear the window to avoid drawing over previous frames
    window.clear()
    eater.draw()

# Start the pyglet event loop
pyglet.app.run()