""" Album class

This class represents an Album object, which represents a Spotify album.
"""

# Standard library imports
import copy
import sys

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils


class Album:
    """ The Album class. Use methods here to get information about an Album.

    Required token scopes:
        None: the methods in the Album class require a token, but the token
            needs no scopes.
    TODO: is this true?
    """


    def __init__(self, session, info):
        """ Get an instance of Album

        This constructor should never be called by the client. To get an
        instance of Album, use Session.get_albums()

        Args:
            session: a Session instance
            info: the album's information
        """
        # Validate inputs
        if 'id' not in info:
            raise ValueError('Album id not in info')

        # Defensively copy
        info = copy.deepcopy(info)

        self._id = info['id']
        self._raw = info
        self._session = session

        # If tracks / paging objects malformed, defer manual track fetching.
        if 'tracks' not in info or \
            'total' not in info['tracks'] or \
            'limit' not in info['tracks'] or \
            'items' not in info['tracks']:
            self._tracks = None

        # If too many tracks, defer fetching them until needed.
        if info['tracks']['total'] > info['tracks']['limit']:
            self._tracks = None

        self._tracks = info['tracks']['items']

        # Defer artists until later
        self._artists = None


    def __str__(self):
        return f'Album {self.name()}'


    def __repr__(self):
        return str(self) + f' with id <{self.spotify_id()}'


    def __eq__(self, other):
        return utils.spotifython_eq(self, other)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return utils.spotifython_hash(self)


    def __len__(self):
        self._update_tracks()
        return len(self._tracks)


    def __getitem__(self, key):
        # Make sure we have tracks to get items from
        self._update_tracks()

        # Since self._tracks is a list, accepts negative keys and slices
        return self._tracks[key]


    def _update_fields(self):
        """ Update self._raw using the Album id

        Calls endpoints:
            GET     /v1/albums/{id}
        """

        response_json, status_code = utils.request(
            session=self._session,
            request_type=const.REQUEST_GET,
            endpoint=Endpoints.ALBUM_GET_DATA % self.spotify_id()
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        # Updates _raw with new values. One liner : for each key in union of
        # keys in self._raw and response_json, takes value for key from
        # response_json if present, else takes value for key from self._raw.
        # TODO: this is weird notation, make a utility function for it.
        # Especially useful since it is an action necessary for many classes.
        self._raw = {**self._raw, **response_json}


    def _update_tracks(self):
        """ Update self._tracks using the Album id

        Calls endpoints:
            GET     /v1/albums/{id}/tracks
        """

        # Only populate tracks if necessary
        if self._tracks is not None:
            return

        self._tracks = utils.paginate_get(
            session=self._session,
            limit=sys.maxsize,
            return_class=Track,
            endpoint=Endpoints.ALBUM_GET_DATA % self.spotify_id()
        )


    def spotify_id(self):
        return self._id


    def type(self):
        types = {
            'single': const.SINGLE,
            'compilation': const.COMPILATION,
            'album': const.ALBUMS
        }
        return types[utils.get_field(self, 'album_type')]


    def artists(self):
        if self._artists is not None:
            return self._artists

        artists = utils.get_field(self, 'artists')
        self._artists = [Artist(self._session, art) for art in artists]

        return self._artists


    def available_markets(self):
        return utils.get_field(self, 'available_markets')


    def copyrights(self):
        return utils.get_field(self, 'copyrights')


    def genres(self):
        return utils.get_field(self, 'genres')


    def href(self):
        return utils.get_field(self, 'href')


    def uri(self):
        return utils.get_field(self, 'uri')


    def images(self):
        return utils.get_field(self, 'images')


    def label(self):
        return utils.get_field(self, 'label')


    def name(self):
        return utils.get_field(self, 'name')


    def popularity(self):
        return utils.get_field(self, 'popularity')


    def release_date(self):
        # Spotify returns date in format Y-M-D
        date = utils.get_field(self, 'release_date').split('-')

        # Convert to ints
        date = [int(elem) for elem in date]
        return tuple(date)


    def tracks(self):
        self._update_tracks()
        return self._tracks


#pylint: disable=wrong-import-position
from spotifython.track import Track
from spotifython.artist import Artist
