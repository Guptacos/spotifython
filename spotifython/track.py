""" Track class. """

# Standard library imports
import copy

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils


class Track:
    """ Represents a Spotify track / song tied to a unique Spotify id.

    Do not use the constructor. To get a track by its id, use
    :meth:`Session.get_tracks() <spotifython.session.Session.get_tracks>`. To
    get a track from another object, use appropriate methods such as
    :meth:`Album.tracks() <spotifython.album.Album.tracks>`,
    :meth:`Playlist.tracks() <spotifython.playlist.Playlist.tracks>`, etc.

    Required token scopes:
        - None: the methods in the Track class require a token, but the token
          needs no scopes.
    """


    def __init__(self, session, info):
        """ Get an instance of Track. Client should not use the constructor!

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
        """ Returns the track name. """
        return f'Track {self.name()}'


    def __repr__(self):
        """ Returns the track name and Spotify id. """
        return str(self) + f' with id <{self.spotify_id()}>'


    def __eq__(self, other):
        """ Two tracks are equal if they have the same Spotify id. """
        return utils.spotifython_eq(self, other)


    def __ne__(self, other):
        """ Two tracks are not equal if they have different Spotify ids. """
        return not self.__eq__(other)


    def __hash__(self):
        """ Two equivalent tracks will return the same hashcode. """
        return utils.spotifython_hash(self)


    def __len__(self):
        """
        Returns:
            int: The length of the track in milliseconds

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'duration_ms')


    def _update_fields(self):
        """ Update self._raw using the track id.

        Calls endpoints:
            - GET     /v1/tracks/{id}
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
        """
        Returns:
            str: the Spotify id of this track.
        """
        return self._id


    def album(self):
        """
        Returns:
            Album: The album this track is on:

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        if self._album is None:
            album = utils.get_field(self, 'album')
            self._album = Album(self._session, album)

        return self._album


    def artists(self):
        """
        Returns:
            List[Artist]: a list of the artist(s) on this track.

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        if self._artists is None:
            artists = utils.get_field(self, 'artists')
            self._artists = [Artist(self._session, art) for art in artists]

        return self._artists


    def available_markets(self):
        """
        Returns:
            List[str]: A list of the country codes this track is available in.

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'available_markets')


    def name(self):
        """
        Returns:
            str: The name of the track as it appears on Spotify.

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'name')


    def popularity(self):
        """ Get the popularity of the track as calculated by Spotify.

        Returns:
            int: The popularity is between 0 and 100 (inclusive), with 100 being
            the most popular. This number is calculated in Spotify's backend.

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'popularity')


    def disc_number(self):
        """ Get the track's disc number (0 indexed).

        Note:
            On Spotify (and in most music software) disc number is 1-indexed.
            This method intentionally makes it 0 indexed for consistency with
            the rest of the library.

        Returns:
            int: The number of the disc on which this track appears. This is
            usually 0, unless an album has multiple discs.

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        result = utils.get_field(self, 'disc_number')
        return result - 1


    def track_number(self):
        """ Get the track's number (0 indexed).

        Note:
            On Spotify (and in most music software) track number is 1-indexed.
            This method intentionally makes it 0 indexed for consistency with
            the rest of the library.

            This decision was made so that Track.track_number() is consistent
            with Album.__get_item__().

            Ex: for some 0 <= num < len(Album), Album[num].track_number() == num

        Returns:
            int: The track's number in the album. If an album has several discs,
            the track number is the number of this track on the disc it appears.


        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        result = utils.get_field(self, 'track_number')
        return result - 1


    def explicit(self):
        """
        Returns:
            bool: True if the track has explicit lyrics, and False otherwise.

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'explicit')


    def uri(self):
        """
        Returns:
            str: the track's Spotify uri.

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'uri')


    def href(self):
        """ Get the track's href.

        Returns:
            str: A link to the Web API endpoint providing full track details.

        Calls endpoints:
            - GET     /v1/tracks/{id}
        """
        return utils.get_field(self, 'href')


    # TODO: If Spotify ever freezes the audio features, may be worth making into
    #       an object.
    def audio_features(self):
        #pylint: disable=line-too-long
        """ Get the audio features for this track.

        For more information on track audio features, see Spotify's
        `documentation <https://developer.spotify.com/documentation/web-api/reference/object-model/#audio-features-object>`__

        Returns:
            dict: a dictionary as defined at the above link, where the key is
            the audio feature, and the value is the value of that feature.

        Calls endpoints:
            - GET     /v1/audio-features/{id}
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
        #pylint: disable=line-too-long
        """ Get the audio analysis for this track.

        The Audio Analysis describes the track’s structure and musical content,
        including rhythm, pitch, and timbre. All information is precise to the
        audio sample.

        For more information on track audio analysis, see Spotify's
        `documentation <https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/>`__

        Returns:
            dict: a dictionary containing the audio analysis as defined at the
            above link.

        Calls endpoints:
            - GET     /v1/audio-analysis/{id}
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
