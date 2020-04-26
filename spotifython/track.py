from album import Album
from artist import Artist

class Track:
    def __init__(self, track_info: dict):
        self.album = track_info.get('album', None)
        self.artists = list()
        for artist in track_info.get('artists', None):
            self.artists.append(Artist(artist))
        self.available_markets = track_info.get('available_markets', None)
        self.id = track_info.get('id', None)
        self.images = track_info.get('images', None)

        self.raw = track_info