from album import Album
from artist import Artist
from copy import deepcopy

class Track:
    # User should never call this constructor. As a result, they should never
    # have access to the track_info structure prior to creating a track. This 
    # assumption lets us modify the track_info object willy-nilly.
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
        return deepcopy(self._raw)