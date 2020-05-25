""" Artist class

This class represents an Artist object, tied to a Spotify user id.
"""

# Standard library imports
from typing import List, Any
import math

# Aliases to avoid circular dependencies
Album = Any  # album.py imports this module.
# Artist = Any  # artist.py imports this module.
# Playlist = Any  # playlist.py imports this module.
Track = Any  # track.py imports this module.
# User = Any  # user.py imports this module.
Session = Any # session.py imports this module

# pylint: disable = pointless-string-statement, too-many-instance-attributes
# pylint: disable = too-many-branches, wrong-import-position

class Artist:
    """ Artist class

    This class represents an Artist object, tied to a Spotify user id.
    """

    def __init__(self, session, artist_info):
        """ User should never call this constructor. As a result, they should
        never have access to the artist_info structure prior to creating an
        Artist.

        Args:
            session: a Spotifython session instance
            artist_info: a dictionary containing known values about the artist
        """
        # TODO: add type checking for session
        if not isinstance(artist_info, dict):
            raise TypeError(artist_info)

        self.session = session
        self._raw = artist_info
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

    ##################################
    # Field accessors
    ##################################

    ### Unsupported objects ###
    # External url: unsupported object
    # Followers: unsupported object
    # Images: unsupported object
    # Type: is an artist. we don't need to include this.

    def genres(self):
        """ Getter for the genre of an artist. Returns a List[str].
        """
        return utils.get_field(self, 'genres')

    def href(self):
        """ Getter for the href for an artist. Returns a str.
        """
        return utils.get_field(self, 'href')

    def spotify_id(self):
        """ Getter for the spotify id for an artist. Returns a str.
        """
        return utils.get_field(self, 'id')

    def name(self):
        """ Getter for the name for an artist. Returns a str.
        """
        return utils.get_field(self, 'name')

    def popularity(self):
        """ Getter for the popularity for an artist. Returns a str.
        """
        return utils.get_field(self, 'popularity')

    def uri(self):
        """ Getter for the uri for an artist. Returns a str.
        """
        return utils.get_field(self, 'uri')

    def _update_fields(self):
        """ If field is not present, update it using the object's artist id.

        Raises:
            ValueError if artist id not present in the raw object data.

        Required token scopes:
            N/A

        Calls endpoints:
            GET     /v1/artists/{id}
        """
        _artist_id = self.spotify_id()
        endpoint = f'/v1/artists/{_artist_id}'
        response_json, _ = utils.request(
            session=self.session,
            request_type=const.REQUEST_GET,
            endpoint=endpoint,
        )
        # Updates _raw with new values. One liner : for each key in union of
        # keys in self._raw and response_json, takes value for key from
        # response_json if present, else takes value for key from self._raw.
        self._raw = {**self._raw, **response_json}

    ##################################
    # API Calls
    ##################################

    def albums(self,
               search_limit=None,
               include_groups=None,
               market=const.TOKEN_REGION
               ):
        """ Gets the albums associated with the current Spotify artist.

        Args:
            search_limit: (Optional) int, the maximum number of results
                to return.
            include_groups: (Optional) List[str], a list of keywords
                that will be used to filter the response. If not supplied,
                all album types will be returned.
                Valid values are: const.ARTIST_ALBUM, const.ARTIST_SINGLE,
                const.ARTIST_APPEARS_ON, const.ARTIST_COMPILATION
            market: (Optional) str, An ISO 3166-1 alpha-2 country code or the
                string const.TOKEN_REGION.
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
            N/A

        Calls endpoints:
            GET	/v1/artists/{id}/albums
        """

        # Type validation
        if search_limit is not None and not isinstance(search_limit, int):
            raise TypeError(search_limit)
        if include_groups is not None and \
            not isinstance(include_groups, List[str]):
            raise TypeError(include_groups)
        if market is not None and not isinstance(market, str):
            raise TypeError(market)

        # Save params for lazy loading check
        search_query = (search_limit, include_groups, market)

        # Construct params for API call
        _artist_id = self.spotify_id()
        endpoint = Endpoints.ARTIST_GET_ALBUMS.format(_artist_id)
        uri_params = dict()
        # TODO: when testing, double check the valid values (and if the
        # constants exist)
        if include_groups is not None and len(include_groups) > 0:
            uri_params['include_groups'] = ','.join(include_groups)
        if market is not None:
            uri_params['market'] = market

        # Each API call can take 1-50 requests as "limit", or no limit.
        api_call_limit = 50
        offset = 0
        if search_limit:
            num_requests = math.ceil(search_limit / api_call_limit)
        else:
            num_requests = float('inf')

        # Initialize self.albums if different query or never previously called
        if self._albums is None or search_query != self._albums_query_params:
            self._albums = list()

        # Execute requests
        while num_requests > 0:
            if search_limit is None:
                search_limit = api_call_limit
            else:
                search_limit = min(search_limit, api_call_limit)
            uri_params['limit'] = search_limit
            uri_params['offset'] = offset
            response_json, _ = utils.request(
                session=self.session,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            items = response_json['items']
            for item in items:
                self._albums.append(Album(item))

            # Last page reached
            if response_json['next'] == 'null':
                break

            num_requests -= 1
            offset += api_call_limit

        # Update stored params for lazy loading
        self._albums_query_params = search_query

        return self._albums


    def top_tracks(self,
                   market=const.TOKEN_REGION,
                   search_limit=10,
                   ):
        """ Gets the top tracks associated with the current Spotify artist.

        Args:
            market: str, an ISO 3166-1 alpha-2 country code or the string
                const.TOKEN_REGION.
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
            N/A

        Calls endpoints:
            GET	/v1/artists/{id}/top-tracks
        """

        # Note: This search limit is not part of the API, Spotify always returns
        # up to 10. Market query param is 'country' in the API but named marked
        # for consistency

        # Type validation
        if not isinstance(market, str):
            raise TypeError(market)
        if not isinstance(search_limit, int):
            raise TypeError(search_limit)

        # Argument validation
        if market is None:
            raise ValueError(market)
        if search_limit > 10:
            raise ValueError(search_limit)

        # Save params for lazy loading check
        search_query = (market, search_limit)

        # Construct params for API call
        _artist_id = self.spotify_id()
        endpoint = Endpoints.ARTIST_TOP_TRACKS.format(_artist_id)
        uri_params = dict()
        uri_params['country'] = market

        # Initialize self.top_tracks if different query or never previously
        # called
        if self._top_tracks is None or \
            self._top_tracks != self._top_tracks_query_params:
            self._top_tracks = list()

        # Execute requests
        response_json, _ = utils.request(
            session=self.session,
            request_type=const.REQUEST_GET,
            endpoint=endpoint,
            uri_params=uri_params
        )

        items = response_json['items']
        for item in items:
            self._top_tracks.append(Track(item))

        # Update stored params for lazy loading
        self._albums_query_params = search_query

        return self._albums[:search_limit]

    def related_artists(self,
                        search_limit=20,
                        ):
        """ Gets Spotify catalog information about artists similar to a
        given artist.

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
            N/A

        Calls endpoints:
            GET	/v1/artists/{id}/related-artists
        """

        # This search limit is not part of the API, Spotify always returns up to
        # 20.

        # Type validation
        if search_limit is not None and not isinstance(search_limit, int):
            raise TypeError(search_limit)

        # Argument validation
        if search_limit > 20:
            raise ValueError(search_limit)

        # Save params for lazy loading check
        search_query = (search_limit)

        # Construct params for API call
        _artist_id = self.spotify_id()
        endpoint = Endpoints.ARTIST_RELATED_ARTISTS.format(_artist_id)

        # Initialize self.top_tracks if different query or never previously
        # called
        self._related_artists = self._related_artists \
            if self._related_artists is not None \
                and search_query == self._related_artists_query_params \
                else list()

        # Execute requests
        response_json, _ = utils.request(
            session=self.session,
            request_type=const.REQUEST_GET,
            endpoint=endpoint,
        )

        items = response_json['items']
        for item in items:
            self._related_artists.append(Artist(self, item))

        # Update stored params for lazy loading
        self._related_artists_query_params = search_query

        return self._related_artists[:search_limit]

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils
