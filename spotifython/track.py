""" Track class """

# Standard library imports
import copy

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils


class Track:
    """ Represents a Spotify track / song tied to a unique Spotify id

    Use methods here to get information about a Track.

    Required token scopes:
        None: the methods in the Track class require a token, but the token
            needs no scopes.
    """


    def __init__(self, session, info):
        """ Get an instance of Track

        This constructor should never be called by the client. To get a
        Track by its id, use Session.get_tracks(). To get a Track from another
        object, use appropriate methods such as Album.tracks(),
        Playlist.tracks(), etc.

        Args:
            session: a Session instance
            info (dict): the track's information. Must contain 'id'.
        """
        # Validate inputs
        if 'id' not in info:
            raise ValueError('Track id not in info')

        self._id = info['id']

        self._raw = copy.deepcopy(info)
        self._session = session

        # Need name in order to print. 'name' should always be in info, so this
        # shouldn't ever trigger, and is here more as a precaution.
        if 'name' not in info:
            self._update_fields()

        # Cached fields
        self._album = None
        self._artists = None


    def __str__(self):
        return f'Track {self.name()}'


    def __repr__(self):
        return str(self) + f' with id <{self.spotify_id()}>'


    def __eq__(self, other):
        return utils.spotifython_eq(self, other)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return utils.spotifython_hash(self)


    def __len__(self):
        """ Get the length of the track

        Returns:
            int: the length of the track in milliseconds

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'duration_ms')


    def _update_fields(self):
        """ Update self._raw using the Track id

        Calls endpoints:
            GET     /v1/tracks/{id}
        """

        response_json, status_code = utils.request(
            session=self._session,
            request_type=const.REQUEST_GET,
            endpoint=Endpoints.TRACK_GET_DATA % self.spotify_id()
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        # Updates _raw with new values. One liner : for each key in union of
        # keys in self._raw and response_json, takes value for key from
        # response_json if present, else takes value for key from self._raw.
        # TODO: this is weird notation, make a utility function for it.
        # Especially useful since it is an action necessary for many classes.
        self._raw = {**self._raw, **response_json}


    def spotify_id(self):
        """ Get the id of this Track

        Returns:
            str: the Track's Spotify id
        """
        return self._id


    def album(self):
        """ Get the Album this Track is on

        Returns:
            Album: a Spotifython Album object

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        if self._album is None:
            album = utils.get_field(self, 'album')
            self._album = Album(self._session, album)

        return self._album


    def artists(self):
        """ Get the Artists for this Track

        Returns:
            List[Artist]: a list of Spotifython Artist objects

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        if self._artists is None:
            artists = utils.get_field(self, 'artists')
            self._artists = [Artist(self._session, art) for art in artists]

        return self._artists


    def available_markets(self):
        """ Get the country codes of the markets this Track is available in.

        Returns:
            List[str]: a list of the available country codes

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'available_markets')


    def name(self):
        """ Get the name of the Track

        Returns:
            str: the name of the Track as it appears on Spotify

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'name')


    def popularity(self):
        """ Get the popularity of the Track

        The popularity is between 0 and 100 (inclusive), with 100 being the most
        popular. This number is calculated in Spotify's backend.

        Returns:
            int: the popularity of the Track as calculated by Spotify

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'popularity')


    def disc_number(self):
        """ Get the Track's disc number (0 indexed)

        The number of the disc on which this Track appears. This is usually 0,
        unless an album has multiple discs.

        Note:
            On Spotify (and in most music software) disc number is 1-indexed.
            This method intentionally makes it 0 indexed for consistency with
            the rest of the library.

        Returns:
            int: the number of the Track's disc

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        result = utils.get_field(self, 'disc_number')
        return result - 1


    def track_number(self):
        """ Get the Track's number (0 indexed)

        This is the track's number in the album. If an album has several discs,
        the track number is the number of this Track on the disc it appears.

        Note:
            On Spotify (and in most music software) track number is 1-indexed.
            This method intentionally makes it 0 indexed for consistency with
            the rest of the library.

            This decision was made so that Track.track_number() is consistent
            with Album.__get_item__().

            Ex: for some 0 <= num < len(Album), Album[num].track_number() == num

        Returns:
            int: the Track's number on its disc

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        result = utils.get_field(self, 'track_number')
        return result - 1


    def explicit(self):
        """ Get whether the Track is explicit

        Returns:
            bool: True if the track has explicit lyrics, and False otherwise

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'explicit')


    def uri(self):
        """ Get the Track's uri

        Returns:
            str: the Spotify uri for this Track

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'uri')


    def href(self):
        """ Get the Track's href

        Returns:
            str: a link to the Web API endpoint providing full Track details.

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'href')


    # TODO: If Spotify ever freezes the audio features, may be worth making into
    #       an object.
    def audio_features(self):
        """ Get the audio features for this Track

        For more information on Track audio features, see here:
        https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/

        Returns:
            dict: a dictionary as defined at the above link, where the key is
                the audio feature, and the value is the value of that feature.

        Calls endpoints:
            GET     /v1/audio-features/{id}
        """
        response_json, status_code = utils.request(
            session=self._session,
            request_type=const.REQUEST_GET,
            endpoint=Endpoints.TRACK_FEATURES % self.spotify_id()
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        return response_json


    # TODO: If Spotify ever freezes the audio analysis, may be worth making into
    #       an object.
    def audio_analysis(self):
        """ Get the audio analysis for this Track

        The Audio Analysis describes the track’s structure and musical content,
        including rhythm, pitch, and timbre. All information is precise to the
        audio sample.

        For more information on Track audio analysis, see here:
        https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/

        Returns:
            dict: a dictionary containing the audio analysis as defined at the
                above link.

        Calls endpoints:
            GET     /v1/audio-analysis/{id}
        """
        response_json, status_code = utils.request(
            session=self._session,
            request_type=const.REQUEST_GET,
            endpoint=Endpoints.TRACK_ANALYSIS % self.spotify_id()
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        return response_json


#pylint: disable=wrong-import-position
from spotifython.album import Album
from spotifython.artist import Artist
