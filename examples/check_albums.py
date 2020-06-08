""" Example showing how to get the release dates of an artist's top albums """

#pylint: disable=import-error
import spotifython as sp

# TODO: this example makes method calls to stale methods.

# You shouldn't do this for security reasons, but we want to demonstrate that
# however the user chooses to store the token for an API session is decoupled
# from the API itself.
TOKEN = 'deadbeef'

def get_album_releases(artist):
    """ Get release dates for an artists top albums

    Args:
        artist: an instance of sp.Artist

    Returns:
        dict: dictionary mapping the album name to its release year.
    """
    session = sp.Session(TOKEN)
    results = session.search(artist, types=[sp.ARTISTS], limit=5)

    # artists() automatically sorts based off top results according to Spotify.
    top_artist = results.artists()[0]

    release_dates = {}
    for album in top_artist.albums():
        release_dates[album.name()] = album.release_date()

    return release_dates
