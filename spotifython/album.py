from track import Track
from copy import deepcopy


TRACKS = 'GET https://api.spotify.com/v1/albums/%s/tracks'

class Album:
    def __init__(self, album_info):
        self.album_type = album_info.get('album_type', '')
        self.artists = list()
        for artist in album_info.get('artists', []):
            self.artists.append(Artist(artist))

        self._raw = album_info

    def __str__(self):
        return '%s by %s' % (self._raw['name'], self._artists[0].name())

    def __eq__(self, other):
        return (isinstance(other, Album) and self._raw == other._raw)

    # TODO: these will be getter methods to fetch things from _raw. Boilerplate,
    # so I will address in a wee bit.

    def tracks(self):
        if 'id' not in self._raw:
            return None
        album_id = self._raw.get['id']
        request = TRACKS % (album_id)
        # TODO: send the actual request
        return
