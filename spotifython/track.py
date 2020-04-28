from album import Album
from artist import Artist
from copy import deepcopy

AUDIO_FEATURES = 'GET https://api.spotify.com/v1/audio-features/%s'
AUDIO_ANALYSIS = 'GET https://api.spotify.com/v1/audio-features/%s'


class Track:
    # User should never call this constructor. As a result, they should never
    # have access to the track_info structure prior to creating a track. This
    # assumption lets us modify the track_info object willy-nilly.
    def __init__(self, track_info: dict):
        self._raw = deepcopy(track_info)

        self._album = Album(track_info.get('album', None))
        self._artists = list()
        for artist in track_info.get('artists', None):
            self._artists.append(Artist(artist))


    def __str__(self):
        return '%s by %s' % (self._raw['name'], self._artists[0].name())

    def __eq__(self, other):
        return (isinstance(other, Track) and self._raw == other._raw)

    # the following are getter methods to fetch relevant information.
    def album(self):
        # TODO: it might be worth caching ids to objects so we can easily
        # reference pre-existing data.
        return self._album

    def artists(self):
        # TODO: it might be worth caching ids to objects so we can easily
        # reference pre-existing data.
        return self._artists

    def available_markets(self):
        return self._raw['available_markets']

    def name(self):
        return self._raw['name']

    def popularity(self):
        return self._raw['popularity']

    def track_number(self):
        return self._raw['track_number']

    # TODO: for debugging implementation purposes only, user should not call.
    def _asdict(self):
        return deepcopy(self._raw)

    # These are the API wrapper calls that track objects should be concerned
    # with.
    def audio_features(self):
        if 'id' not in self._raw:
            return None
        track_id = self._raw.get['id']
        request = AUDIO_FEATURES % (track_id)
        # TODO: send the actual request
        return

    def audio_analysis(self):
        if 'id' not in self._raw:
            return None
        track_id = self._raw.get['id']
        request = AUDIO_ANALYSIS % (track_id)
        # TODO: send the actual request
        return
