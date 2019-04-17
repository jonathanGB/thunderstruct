import matplotlib.pyplot as plt
from IPython.display import HTML, display
import matplotlib.animation as animation

# generates mp4 movie from 3d array volume, like plot3d
def movie(vol, iskwargs={}, interval=10, repeat_delay=1000, **kwargs):
    fig = plt.figure()
    plts = [[plt.imshow(A, **iskwargs)] for A in vol]
    ani = animation.ArtistAnimation(fig, plts, interval=interval, blit=True, repeat_delay=repeat_delay, **kwargs)
    ani.save("light.mp4")