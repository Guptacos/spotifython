import spotifython as sp

# You shouldn't do this for security reasons, but we want to demonstrate that
# however the user chooses to store the token for an API session is decoupled
# from the API itself.
TOKEN = 'woohoo'

# This function takes the name of an artist and returns a list of the top 
# tracks by the top related artists.
def check_top_related_tracks(artist : str):
    session = sp.Spotifython(TOKEN)
    results = session.search(artist, types=[sp.ARTISTS])

    # artists() method automatically sorts based off of top results according
    # to Spotify.
    top_artist = results.artists()[0]

    top_related_tracks = []
    related_artists = top_artist.related_artists()
    for related_artist in related_artists:
        top_tracks = related_artist.top_tracks()
        for track in top_tracks:
            top_related_tracks.append(track)
    
    return top_related_tracks