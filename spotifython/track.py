""" Track class

This class represents a Track object, which represents a Spotify track / song.
"""

# Standard library imports
import copy

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils


class Track:
    """ The Track class. Use methods here to get information about a Track.

    Required token scopes:
        None: the methods in the Track class require a token, but the token
            needs no scopes.
    """


    # TODO: should init call self._update_fields()?
    def __init__(self, session, info):
        """ Get an instance of Track

        This constructor should never be called by the client. To get an
        instance of Track, use Session.get_tracks()

        Args:
            session: a Spotifython instance
            info: the track's information
        """
        # Validate inputs
        if 'id' not in info:
            raise ValueError('Track id not in info')

        self._id = info['id']

        # TODO: name this _raw or _info?
        self._raw = copy.deepcopy(info)
        self._session = session


    # TODO: test this
    # TODO: is it bad for print to make api calls?
    # TODO: should include artists?
    def __str__(self):
        name = self.name()
        return f'Track {name}'


    # Too long print?
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
        album = utils.get_field(self, 'album')
        return Album(self._session, album)


    def artists(self):
        """ Get the Artists for this Track

        Returns:
            List[Artist]: a list of Spotifython Artist objects

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        artists = utils.get_field(self, 'artists')
        return [Artist(self._session, art) for art in artists]


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
        popular. This number is calculated by a Spotify algorithm.

        Returns:
            int: the popularity of the Track as calculated by Spotify

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'popularity')


    def disc_number(self):
        """ Get the Track's disc number (1 indexed)

        The number of the disc on which this Track appears. This is usually 1,
        unless an album has multiple discs.

        Returns:
            int: the number of the Track's disc

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'disc_number')


    def track_number(self):
        """ Get the Track's number

        This is the track's number in the album. If an album has several discs,
        the track number is the number of this Track on the disc it appears.

        Returns:
            int: the Track's number on it's disc

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'track_number')


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
            str: a link to the Web API endpoint providing full track details.

        Calls endpoints:
            GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'href')


    # TODO: maybe change this to a feature object?
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


    # TODO: this is a fat response json... should we make an analysis object?
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
