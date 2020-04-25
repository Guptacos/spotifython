import spotifython as sp

# You shouldn't do this for security reasons, but we want to demonstrate that
# however the user chooses to store the token for an API session is decoupled
# from the API itself.
TOKEN = 'woohoo'

# this function takes the name of an artist and returns a dictionary mapping the
# album name to its release year.
def get_album_releases(artist : str):
    session = sp.Spotifython(TOKEN)
    results = session.search(artist, types=[sp.ARTISTS])

    # artists() method automatically sorts based off of top results according
    # to Spotify.
    top_artist = results.artists()[0]

    release_dates = {}
    for album in top_artist.albums():
        release_dates[album.name()] = album.release_date()

    return release_dates