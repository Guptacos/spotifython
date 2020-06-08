""" Example showing how to get the release dates of an artist's top albums """

#pylint: disable=import-error
import spotifython as sp

# TODO: this example makes method calls to stale methods.

# You shouldn't do this for security reasons, but we want to demonstrate that
# however the user chooses to store the token for an API session is decoupled
# from the API itself.
TOKEN = 'deadbeef'

# This function takes the name of an artist and returns a list of the top
# tracks by the top related artists.
def check_top_related_tracks(artist):
    """ Get top tracks for related artists

    Args:
        artist: an instance of sp.Artist

    Returns:
        List[Track]: top tracks for artists related to the input artist
    """
    session = sp.Session(TOKEN)
    results = session.search(artist, types=[sp.ARTISTS], limit=5)

    # artists() automatically sorts based off top results according # to Spotify
    # TODO: see issue #21: How to deal with functions that can take 1 or more
    # of an obj as an arg?
    top_artist = results.artists().contents()[0]

    top_related_tracks = []
    related_artists = top_artist.related_artists()
    for related_artist in related_artists:
        top_tracks = related_artist.top_tracks()
        for track in top_tracks:
            top_related_tracks.append(track)

    return top_related_tracks
