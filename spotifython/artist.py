""" Artist class. """

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils

# pylint: disable = pointless-string-statement, too-many-instance-attributes
# pylint: disable = too-many-branches

class Artist:
    """ Represents an Artist object, tied to a Spotify artist id.

    Do not use the constructor. To get an Artist by their id, use
    :meth:`Session.get_artists() <spotifython.session.Session.get_artists>`. To
    get an Artist from another object, use appropriate methods such as
    :meth:`Track.artists() <spotifython.track.Track.artists>`,
    :meth:`Album.artists() <spotifython.album.Album.artists>`, etc.

    Raises:
        TypeError: for invalid argument types.
        ValueError: for arguments that violate stated requirements.
        HTTPError: for web request errors or partial failures.

    Required token scopes:
        - None: the methods in the Artist class require a token, but the token
          needs no scopes.
    """

    def __init__(self, session, info):
        """ Get an instance of Artist. Client should not use the constructor!

        Args:
            session: a Session instance
            info (dict): the artist's information. Must contain 'id'.
        """
        # TODO: add type checking for session
        if not isinstance(info, dict):
            raise TypeError('artist_info should be dict')

        if 'id' not in info:
            raise ValueError('Artist id not in info')

        # TODO: need to make sure user is here.

        self._session = session
        self._raw = info
        # Lazily loaded fields from API calls
        self._albums = None
        self._top_tracks = None
        self._related_artists = None
        # Params used to call each previous entry - determins whether to reload
        self._albums_query_params = None
        self._top_tracks_query_params = None
        self._related_artists_query_params = None

    ##################################
    # Overloads
    ##################################

    def __str__(self):
        """ Returns the artist name. """
        return self.name()

    def __repr__(self):
        """ Returns the artist name and Spotify id. """
        return str(self) + f' with id <{self.spotify_id()}>'

    def __eq__(self, other):
        """ Two artists are equal if they have the same Spotify id. """
        return utils.spotifython_eq(self, other)

    def __ne__(self, other):
        """ Two artists are not equal if they have different Spotify ids. """
        return not self.__eq__(other)

    def __hash__(self):
        """ Two equivalent artists wll return the same hashcode. """
        return utils.spotifython_hash(self)

    ##################################
    # Field accessors
    ##################################

    ### Unsupported objects ###
    # External url: unsupported object
    # Followers: unsupported object
    # Images: unsupported object
    # Type: is an artist. we don't need to include this.

    def genres(self):
        """ Get the genres for this artist as categorized by Spotify.

        Returns:
            List[str]: A list of genre names. Could be empty if the artist is
            not yet classified.

        Calls endpoints:
            - GET     /v1/artists/{id}
        """
        return utils.get_field(self, 'genres')

    def href(self):
        """ Get the artist's href.

        Returns:
            str: A link to the Web API endpoint providing full artist details.

        Calls endpoints:
            - GET     /v1/artists/{id}
        """
        return utils.get_field(self, 'href')

    def spotify_id(self):
        """
        Returns:
            str: The Spotify id of this artist.
        """
        return utils.get_field(self, 'id')

    def name(self):
        """
        Returns:
            str: The name of the artist as it appears on Spotify.

        Calls endpoints:
            - GET     /v1/artists/{id}
        """
        return utils.get_field(self, 'name')

    def popularity(self):
        """ Get the popularity of the artist as calculated by Spotify.

        Returns:
            int: The popularity between 0 and 100 (inclusive), with 100 being
            the most popular. This number is calculated using the popularity of
            all the artist's tracks.

        Calls endpoints:
            - GET     /v1/artists/{id}
        """
        return utils.get_field(self, 'popularity')

    def uri(self):
        """
        Returns:
            str: The artist's Spotify uri.

        Calls endpoints:
            - GET     /v1/artists/{id}
        """
        return utils.get_field(self, 'uri')

    def _update_fields(self):
        """ If field is not present, update it using the object's artist id.

        Raises:
            ValueError if artist id not present in the raw object data.

        Calls endpoints:
            - GET     /v1/artists/{id}
        """
        endpoint = Endpoints.ARTIST_GET_BY_ID % self.spotify_id()
        response_json, status_code = utils.request(
            session=self._session,
            request_type=const.REQUEST_GET,
            endpoint=endpoint,
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        # Updates _raw with new values. One liner : for each key in union of
        # keys in self._raw and response_json, takes value for key from
        # response_json if present, else takes value for key from self._raw.
        # TODO: this is weird notation, make a utility function for it.
        # Especially useful since it is an action necessary for many classes.
        self._raw = {**self._raw, **response_json}

    ##################################
    # API Calls
    ##################################

    def albums(self,
               search_limit=None,
               include_groups=None,
               market=const.TOKEN_REGION):
        """ Get the albums associated with the artist.

        Args:
            search_limit (int): the maximum number of results to return.
            include_groups (List[]): a list of keywords that will be used to
                filter the response. If not supplied, all album types will be
                returned. Valid values are:

                - sp.ARTIST_ALBUM
                - sp.ARTIST_SINGLE
                - sp.ARTIST_APPEARS_ON
                - sp.ARTIST_COMPILATION

            market (str): a :term:`market code <Market>` or sp.TOKEN_REGION,
                used for :term:`track relinking <Track Relinking>`.

        Note:
            If market is None, results will be returned for all countries and
            you are likely to get duplicate results per album, one for each
            country in which the album is available!

        Returns:
            List[Album]: The artist's albums.

        Calls endpoints:
            - GET	/v1/artists/{id}/albums
        """

        # TODO: limit can't be None, see paginate_get. These params need
        # validation
        # Type validation
        if search_limit is not None and not isinstance(search_limit, int):
            raise TypeError('search_limit should be None or int')
        if include_groups is not None and \
            not all(isinstance(x, str) for x in include_groups):
            raise TypeError('include_groups should be None or str')
        if market is not None and not isinstance(market, str):
            raise TypeError('market should be None or str')

        # Lazy loading check
        search_query = (search_limit, include_groups, market)
        if search_query == self._albums_query_params:
            return self._albums

        # Construct params for API call
        endpoint = Endpoints.ARTIST_GET_ALBUMS % self.spotify_id()
        uri_params = dict()
        if include_groups is not None and len(include_groups) > 0:
            uri_params['include_groups'] = ','.join(include_groups)
        if market is not None:
            uri_params['market'] = market

        # Update stored params for lazy loading
        self._albums = utils.paginate_get(session=self._session,
                                          limit=search_limit,
                                          return_class=Album,
                                          endpoint=endpoint,
                                          uri_params=uri_params
                                          )
        self._albums_query_params = search_query

        return self._albums

    def top_tracks(self,
                   market=const.TOKEN_REGION,
                   search_limit=10):
        """ Get the top tracks associated with the current Spotify artist.

        Args:
            market (str): a :term:`market code <Market>` or sp.TOKEN_REGION,
                used for :term:`track relinking <Track Relinking>`.
            search_limit (int): the maximum number of results to return. Must be
                between 1 and 10, inclusive (this is Spotify's limit).

        Returns:
            List[Track]: The artist's top tracks.

        Calls endpoints:
            - GET	/v1/artists/{id}/top-tracks
        """

        # TODO: need to fix market requirements. Can be None.
        # Note: This search limit is not part of the API, Spotify always returns
        # up to 10. Market query param is 'country' in the API but named marked
        # for consistency

        # Type validation
        if not isinstance(market, str):
            raise TypeError('market should bes tr')
        if not isinstance(search_limit, int):
            raise TypeError('search_limit should be int')

        # Argument validation
        if market is None:
            raise ValueError('market is a required argument')
        if search_limit < 0 or search_limit > 10:
            raise ValueError('search_limit should be >= 0 and <= 10')

        # Save params for lazy loading check
        search_query = (market, search_limit)

        # Construct params for API call
        endpoint = Endpoints.ARTIST_TOP_TRACKS % self.spotify_id()
        uri_params = dict()
        uri_params['country'] = market

        # Lazy loading check
        if search_query == self._top_tracks_query_params:
            return self._top_tracks

        # Update stored params for lazy loading
        self._top_tracks = utils.paginate_get(session=self._session,
                                              limit=search_limit,
                                              return_class=Track,
                                              endpoint=endpoint,
                                              uri_params=uri_params
                                              )
        self._top_tracks_query_params = search_query

        return self._top_tracks

    def related_artists(self, search_limit=20):
        """ Get artists similar to this artist, as defined by Spotify.

        Args:
            search_limit (int): the maximum number of results to return. Must be
                between 1 and 20, inclusive (this is Spotify's limit).

        Returns:
            List[Artist]: The artists related to this artist.

        Calls endpoints:
            - GET	/v1/artists/{id}/related-artists
        """

        # This search limit is not part of the API, Spotify always returns up to
        # 20.

        # TODO: limit can't be None...

        # Type validation
        if search_limit is not None and not isinstance(search_limit, int):
            raise TypeError('search_limit should be None or int')

        # Argument validation
        if search_limit < 0 or search_limit > 20:
            raise ValueError('search_limit should be >= 0 and <= 20')

        # Save params for lazy loading check
        search_query = (search_limit)

        # Construct params for API call
        endpoint = Endpoints.ARTIST_RELATED_ARTISTS % self.spotify_id()

        # Lazy loading check
        if search_query == self._related_artists_query_params:
            return self._related_artists

        # Update stored params for lazy loading
        self._related_artists = utils.paginate_get(session=self._session,
                                                   limit=search_limit,
                                                   return_class=Artist,
                                                   endpoint=endpoint
                                                   )
        self._related_artists_query_params = search_query

        return self._related_artists


#pylint: disable=wrong-import-position
from spotifython.album import Album
from spotifython.track import Track
