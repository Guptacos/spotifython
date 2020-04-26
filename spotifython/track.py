from album import Album
from artist import Artist

class Track:
    def __init__(self, track_info: dict):
        self._album = Album(track_info.get('album', None))
        self._artists = list()
        for artist in track_info.get('artists', None):
            self._artists.append(Artist(artist))
        
        self._raw = track_info

    def album(self):
        return self._album

    def artists(self):
        return self._artists

    def available_markets(self):
        return self._raw['available_markets']

    def asdict(self):
        return self._raw