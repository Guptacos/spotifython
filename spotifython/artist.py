""" Artist class. """

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils

# pylint: disable = pointless-string-statement, too-many-instance-attributes
# pylint: disable = too-many-branches

class Artist:
    """ Artist class

    This class represents an Artist object, tied to a Spotify artist id.
    """

    def __init__(self, session, info):
        """ Get an instance of Artist.

        This constructor should never be called by the client. To get an
        Artist by their id, use Session.get_artists(). To get an Artist from
        another object, use appropriate methods such as Track.artists(),
        Album.artists(), etc.

        Args:
            session: a Session instance
            info (dict): the artist's information. Must contain 'id'.
        """
        # TODO: add type checking for session
        if not isinstance(info, dict):
            raise TypeError('artist_info should be dict')

        if 'id' not in info:
            raise ValueError('Artist id not in info')

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
        return self.name()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return utils.spotifython_eq(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
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
        """ Get the genres Spotify has defined for this artist.

        Returns:
            A List[str] of the genres associated with the artist.
        """
        return utils.get_field(self, 'genres')

    def href(self):
        """ Get this artist's href.

        Returns:
            A str of the Web API endpoint providing full details of the artist.
        """
        return utils.get_field(self, 'href')

    def spotify_id(self):
        """ Get this artist's Spotify id.

        Returns:
            A str of the artist's Spotify ID.
        """
        return utils.get_field(self, 'id')

    def name(self):
        """ Get this artist's name.

        Returns:
            A str of the artist name.
        """
        return utils.get_field(self, 'name')

    def popularity(self):
        """ Get this artist's popularity.

        Returns:
            An int of the popularity of the artist.
        """
        return utils.get_field(self, 'popularity')

    def uri(self):
        """ Get this artist's uri.

        Returns:
            A str of the Spotify URI for the artist.
        """
        return utils.get_field(self, 'uri')

    def _update_fields(self):
        """ If field is not present, update it using the object's artist id.

        Raises:
            ValueError if artist id not present in the raw object data.

        Required token scopes:
            None

        Calls endpoints:
            GET     /v1/artists/{id}
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
        """ Get the albums associated with the current Spotify artist.

        Args:
            search_limit: (Optional) int, the maximum number of results
                to return.
            include_groups: (Optional) List[str], a list of keywords
                that will be used to filter the response. If not supplied,
                all album types will be returned.
                Valid values are: sp.ARTIST_ALBUM, sp.ARTIST_SINGLE,
                sp.ARTIST_APPEARS_ON, sp.ARTIST_COMPILATION
            market: (Optional) str, An ISO 3166-1 alpha-2 country code or the
                string sp.TOKEN_REGION.
                Supply this parameter to limit the response to one particular
                geographical market. If this value is None, results will be
                returned for all countries and you are likely to get duplicate
                results per album, one for each country in which the album
                is available!

        Returns:
            A List[Album] if the request succeeded.

        Raises:
            TypeError for invalid types in any argument.
            ValueError for invalid market.
                TODO: is this even necessary, will raise ex
            HTTPError for web request errors or partial failures.

        Required token scopes:
            None

        Calls endpoints:
            GET	/v1/artists/{id}/albums
        """

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
            market: str, an ISO 3166-1 alpha-2 country code or the string
                sp.TOKEN_REGION.
            search_limit: int, the maximum number of results to return.

        Returns:
            A List[Track] if the request succeeded.

        Raises:
            TypeError for invalid types in any argument.
            ValueError if market is None.
            ValueError for invalid market.
                TODO: is this even necessary, will raise ex
            ValueError if search_limit is > 10: this is the Spotify API's search
                limit.
            HTTPError for web request errors.

        Required token scopes:
            None

        Calls endpoints:
            GET	/v1/artists/{id}/top-tracks
        """

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
            search_limit: (Optional) int, the maximum number of results
                to return.

        Returns:
            A response object containing a List[Artist] if the request
            succeeded.

        Raises:
            TypeError for invalid types in any argument.
            ValueError if search_limit is > 20: this is the Spotify API's
                search limit.
            HTTPError for web request errors.

        Required token scopes:
            None

        Calls endpoints:
            GET	/v1/artists/{id}/related-artists
        """

        # This search limit is not part of the API, Spotify always returns up to
        # 20.

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
