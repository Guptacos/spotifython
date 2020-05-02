from track import Track
from artist import Artist


class Album:
    def __init__(self, album_info):
        self._album_type = album_info.get('album_type', '')
        self._artists = list()
        for artist in album_info.get('artists', []):
            self._artists.append(Artist(artist))

        tracks_wrapper = album_info.get('tracks', None)
        if tracks_wrapper != None:
            self._tracks = list()
            for track in tracks_wrapper.get('items', []):
                self._tracks.append(Track(track))

        self._available_markets = album_info.get('available_markets', [])
        self._id = album_info.get('id', '')
        self._images = album_info.get('images', {})
        self._name = album_info.get('name', '')
        self._popularity = album_info.get('popularity', -1)
        self._release_date = album_info.get('release_date', '')

        self._iter = 0

    def __eq__(self, other):
        return isinstance(other, Album) and self._album_id == other._album_id

    # iter and next let you loop through the tracks in the album. len gives you
    # the number of tracks in the album.
    def __iter__(self):
        self._iter = 0
        return self

    def __next__(self):
        if self._iter < len(self._tracks):
            track = self._tracks[self._iter]
            self._iter += 1
            return track
        else:
            raise StopIteration

    def __len__(self):
        return len(self._tracks)

    def artists(self):
        return self._artists

    def tracks(self):
        return self._tracks

    def album_type(self):
        return self._album_type

    def available_markets(self):
        return self._available_markets

    def id(self):
        return self._id

    # TODO: usually has three sizes, maybe take in an optional arg for size,
    # otherwise return the first one (largest).
    def image(self, size=None):
        return self._images[0] if size == None else self._images[0]

    def name(self):
        return self._name

    def popularity(self):
        return self._popularity

    def release_date(self):
        return self._release_date
