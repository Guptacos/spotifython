""" Album class """

# Standard library imports
import copy
import sys

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils


class Album:
    """ Represents a Spotify album tied to a unique Spotify id

    Use methods here to get information about an Album.

    Note:
        The Album class does not currently support track relinking using market
        codes. As such, ``__len__()``, ``__getitem___()``, and ``tracks()``
        are not relinked

    Required token scopes:
        None: the methods in the Album class require a token, but the token
            needs no scopes.
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
        elif info['tracks']['total'] > info['tracks']['limit']:
            self._tracks = None

        else:
            self._tracks = info['tracks']['items']

        # Defer artists until later
        self._artists = None


    def __str__(self):
        return f'Album {self.name()}'


    def __repr__(self):
        return str(self) + f' with id <{self.spotify_id()}>'


    def __eq__(self, other):
        """ 2 Albums are equal if they have the same Spotify id
        """
        return utils.spotifython_eq(self, other)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        """ 2 equivalent Albums will return the same hashcode
        """
        return utils.spotifython_hash(self)


    def __len__(self):
        """ Get the length of the album

        Returns:
            int: the number of tracks in the album

        Calls endpoints:
            GET     /v1/albums/{id}/tracks
        """
        self._update_tracks()
        return len(self._tracks)


    def __getitem__(self, key):
        """ Allows you to get a Track in an Album as if the Album were a list

        Usage:
            a = Album()
            track = a[2]

        Args:
            key (int): the index into the album. 0 <= key < len(Album)

        Returns:
            The Track at index "key"
        """
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
        """ Get the id of this Track

        Returns:
            str: the Track's Spotify id
        """
        return self._id


    def type(self):
        """ Get the type of this Album

        Returns:
            One of:

                * sp.SINGLE
                * sp.COMPILATION
                * sp.ALBUMS

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        types = {
            'single': const.SINGLE,
            'compilation': const.COMPILATION,
            'album': const.ALBUMS
        }
        return types[utils.get_field(self, 'album_type')]


    def artists(self):
        """ Get the artists who wrote this Album

        Returns:
            A list of Artist objects. Can have 1 or more Artists.

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        if self._artists is not None:
            return self._artists

        artists = utils.get_field(self, 'artists')
        self._artists = [Artist(self._session, artist) for artist in artists]

        return self._artists


    def available_markets(self):
        """ Get the country codes of the markets this Album is available in.

        The Album is considered available in a market when at least one of its
        Tracks is available in that market.

        Returns:
            List[str]: a list of the available country codes

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        return utils.get_field(self, 'available_markets')


    def copyrights(self):
        """ Get the copyrights statements for this album

        Returns:
            List[Copyright]: a list of Copyright objects

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        result = utils.get_field(self, 'copyrights')
        return [Copyright(elem) for elem in result]


    def genres(self):
        """ Get the genres for this album as categorized by Spotify

        Returns:
            List[str]: a list of genre names. Could be empty if the album is not
                yet classified.

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        return utils.get_field(self, 'genres')


    def href(self):
        """ Get the Album's href

        Returns:
            str: a link to the Web API endpoint providing full Album details.

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        return utils.get_field(self, 'href')


    def uri(self):
        """ Get the Album's uri

        Returns:
            str: the Spotify uri for this Album

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        return utils.get_field(self, 'uri')


    def images(self):
        """ Get the Album's cover art in various sizes, widest first

        Returns:
            List[dict]: a list of image objects as defined here:
                https://developer.spotify.com/documentation/web-api/reference/object-model/#image-object

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        return utils.get_field(self, 'images')


    def label(self):
        """ The label for this Album

        Returns:
            str: the name of the label

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        return utils.get_field(self, 'label')


    def name(self):
        """ Get the name of the Album

        Returns:
            str: the name of the Album as it appears on Spotify

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        return utils.get_field(self, 'name')


    def popularity(self):
        """ Get the popularity of the Album

        The popularity is between 0 and 100 (inclusive), with 100 being the most
        popular. This number is calculated using the popularity of each Track.

        Returns:
            int: the popularity of the Album as calculated by Spotify

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        return utils.get_field(self, 'popularity')


    def release_date(self):
        """ The date the Album was first released.

        Returns:
            A tuple with up to 3 ints. The tuple will be one of the following:

                * (year,)
                * (year, month)
                * (year, month, day)

        Note:
            If the album was first released in March 2010 in Europe, and
            then 2 months later (May) was released to the rest of the world,
            this function will return the March 2010 date.

            We considered instead returning a Python datetime.date object.
            However since Spotify may not return a month / day, we cannot use
            a datetime.date object.

        Calls endpoints:
            GET     /v1/albums/{id}
        """
        # Spotify returns date in format Y-M-D
        date = utils.get_field(self, 'release_date').split('-')

        # Convert to ints
        date = [int(elem) for elem in date]
        return tuple(date)


    def tracks(self):
        """ Get the Tracks in the Album

        Returns:
            List[Track]: the Album's Tracks

        Calls endpoints:
            GET     /v1/albums/{id}/tracks
        """
        self._update_tracks()
        return self._tracks


class Copyright:
    """ Represents a single copyright """


    def __init__(self, info):
        # Validate info
        if 'text' not in info or 'type' not in info:
            raise ValueError('Missing dict key in copyright response', info)

        if info['type'] not in ['C', 'P']:
            raise ValueError('Unknown copyright type <{info["text"]}>')

        self._text = info['text']

        if info['type'] == 'C':
            self._type = const.COMPOSITION
        else:
            self._type = const.SOUND_RECORDING


    def __str__(self):
        return self.text()


    def __repr__(self):
        return str(self)


    def text(self):
        """ Get the text describing the copyright """
        return self._text


    def type(self):
        """ Get the type of the copyright

        Sound recordings (performances) and musical compositions (original
        works) are considered separate things for copyright purposes.

        Returns:
            One of:

                * sp.SOUND_RECORDING
                * sp.COMPOSITION
        """
        return self._type


#pylint: disable=wrong-import-position
from spotifython.track import Track
from spotifython.artist import Artist
