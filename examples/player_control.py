""" Example on how to use the Player class to embed Spotify into another app

Note:
    This example uses tkinter to make a UI; you can do whatever is most easily
    integrated into your application.

    Actual applications should get tokens using Spotify's authentication
    pipeline, and should deal with reauthentication.

    See this link for more information:
    https://developer.spotify.com/documentation/general/guides/authorization-guide/


Running this example:
    * Install Spotifython using our quickstart: TODO
    * Install PIL (used to display cover image)
    * Get a token: https://developer.spotify.com/console/get-user-player/
    * The token must have the following scopes:
      user-read-playback-state
      user-modify-playback-state
    * Set the environment variable 'TOKEN':
      export TOKEN=__token_string__
    * Run the script:
      python3 player_control.py

TODO: add moving progress bar
TODO: add 'available devices' section to transfer playback
"""
#pylint: disable=invalid-name,import-error,not-callable

# Standard library imports
import io
import os
import tkinter as tk
import urllib

# 3rd party imports
from PIL import Image, ImageTk # Render the cover photo
import spotifython as sp

# Constants
REFRESH_RATE = 1000 # 1 second

# Spotifython variables
session = sp.Session(os.environ['TOKEN'])
user = session.get_current_user()
player = user.player()

# Tkinter setup
root = tk.Tk()

def update():
    """ Update song name and image in the GUI """
    try:
        track = player.currently_playing()

    # No active device
    except sp.SpotifyError:
        root.song_cover.configure(image=None)
        root.song_name.configure(text='Nothing playing.')
        return

    # Update the cover photo
    images = track.album().images()

    # In a normal app, may want to pick one of the images.
    # Here, use first one and resize
    url = images[0]['url']

    # Build an image object to render in tkinter
    raw_data = urllib.request.urlopen(url).read()
    im = Image.open(io.BytesIO(raw_data))
    im = im.resize((150, 150), Image.ANTIALIAS)

    # Save image, otherwise tkinter will not render properly
    root.image = ImageTk.PhotoImage(im)
    root.song_cover.configure(image=root.image)

    # Update the song name
    artists = ', '.join([art.name() for art in track.artists()])
    name = track.name() + ' by ' + artists
    root.song_name.configure(text=name)

    # Reschedule the update
    root.after(REFRESH_RATE, update)

def play_pause():
    """ Pause if the song is playing, otherwise resume """
    try:
        if player.is_paused():
            player.resume()

        else:
            player.pause()

    # No active device
    except sp.SpotifyError:
        return

def skip():
    """ Go to the next song """
    try:
        player.skip()
        update()

    # No active device
    except sp.SpotifyError:
        return

def prev():
    """ Go to the previous song """
    try:
        player.previous()
        update()

    # No active device
    except sp.SpotifyError:
        return

def main():
    """ You can mostly ignore this function.

    main() doesn't do anything with Spotifython; it just manages tkinter.
    """

    # Tkinter setup
    root.title(f'{user.name()}\'s player controller')
    root.geometry('400x250')
    root.configure(bg='darkgray')

    # Create our layout
    control_frame = tk.Frame(root)
    control_frame.pack(side='bottom')
    song_frame = tk.Frame(root)
    song_frame.pack(side='bottom')

    # Create our buttons
    # Note on macs, bg / fg colors for buttons aren't supported.
    # Use highlightbackground as a workaround.
    prev_button = tk.Button(
        control_frame,
        text='<<',
        highlightbackground='darkgray',
        command=prev)
    prev_button.pack(side='left')

    play_pause_button = tk.Button(
        control_frame,
        text='play/pause',
        highlightbackground='darkgray',
        command=play_pause)
    play_pause_button.pack(side='left')

    skip_button = tk.Button(
        control_frame,
        text='>>',
        highlightbackground='darkgray',
        command=skip)
    skip_button.pack(side='left')

    root.song_name = tk.Label(song_frame, bg='darkgray')
    root.song_name.pack(side='bottom')
    root.song_cover = tk.Label(song_frame, bg='darkgray')
    root.song_cover.pack(side='bottom')

    # Start the program loop
    update()
    root.mainloop()

if __name__ == '__main__':
    main()
