Quickstart
==========

Installation:
*************
This package is installable using pip:
``pip install spotifython``

Usage:
******
Here is a simple example demonstrating some of the functionality of the library:
    .. code-block:: python

        import spotifython as sp
        import os

        TOKEN = os.environ['TOKEN']
        session = sp.Session(TOKEN)

        user = session.get_users('my_user_id')
        player = user.player()
        player.next()
        player.set_playback_position(300) # ms
        player.pause()

        for track in user.get_saved(sp.TRACKS, limit=5):
            print(track)
            print(track.audio_features())

        top = user.top(sp.TRACKS, limit=5)[0]
        album = top.album()
        print(len(album)) # Number of tracks in the album
