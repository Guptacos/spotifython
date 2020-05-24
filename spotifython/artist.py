from copy import deepcopy
from typing import List, Union

from spotifython import Spotifython as sp
import spotifython.constants as const

from response import Response
from endpoint import Endpoint

class Artist:
    def __init__(self, session, artist_info):
        ''' User should never call this constructor. As a result, they should never
        have access to the artist_info structure prior to creating an Artist.
        
        Args:
            session: a Spotifython instance
            artist_info: a dictionary containing known values about the artist
        '''
        self.session = session
        self._raw = artist_info
        # Lazily loaded fields from API calls
        self.albums = None 
        self.top_tracks = None
        self.related_artists = None
        # Params used to call each previous entry - determins whether to reload
        self._albums_query_params = None
        self._top_tracks_query_params = None
        self.related_artists_query_params = None

    ##################################
    # Overloads
    ##################################

    def __str__(self):
        c = self.name()
        return c.contents() if c else 'ERROR'

    ##################################
    # Field accessors
    ##################################

    ### Unsupported objects ###
    # External url: unsupported object
    # Followers: unsupported object
    # Images: unsupported object
    # Type: is an artist. we don't need to include this.

    def genres(self):
        ''' Getter for the genre of an artist. Returns a List[str].
        '''
        if 'genres' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('genres'))

    def href(self):
        ''' Getter for the href for an artist. Returns a str.
        '''
        if 'href' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('href'))
    
    def spotify_id(self):
        ''' Getter for the spotify id for an artist. Returns a str.
        '''
        if 'id' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('id'))
    
    def name(self):
        ''' Getter for the name for an artist. Returns a str.
        '''
        if 'name' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('name'))
    
    def popularity(self):
        ''' Getter for the popularity for an artist. Returns a str.
        ''' 
        if 'popularity' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('popularity'))
    
    def uri(self):
        ''' Getter for the uri for an artist. Returns a str.
        '''
        if 'uri' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('uri'))
    
    def _update_fields(self):
        ''' If field is not present, update it using the object's artist id.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError if artist id not present in the raw object data.
        
        Calls endpoints: 
            GET     /v1/artists/{id}
        '''
        _artist_id = self.artist_id().contents()
        endpoint = f'/v1/artists/{artist_id}'
        response_json, status_code = self.session._request(
            request_type=const.REQUEST_GET,
            endpoint=endpoint, 
        )
        # Updates _raw with new values.
        # One liner : for each key in union of keys in self._raw and response_json, 
        # takes value for key from response_json if present, 
        # else takes value for key from self._raw.
        self._raw = {**self._raw, **response_json}
        return

    ##################################
    # API Calls
    ##################################
    
    def albums(self, 
        search_limit = None,
        include_groups = None,
        market = const.TOKEN_REGION,
    ):
        ''' Gets the albums associated with the current Spotify artist.
        
        Args:
            search_limit: (Optional) int, the maximum number of results to return.
            include_groups: (Optional) List[str], a list of keywords 
                that will be used to filter the response. If not supplied, 
                all album types will be returned. 
                Valid values are: const.ALBUMS, const.SINGLE, const.APPEARS_ON, const.COMPILATION 
            market: (Optional) str, An ISO 3166-1 alpha-2 country code or the string const.TOKEN_REGION.
                Supply this parameter to limit the response to one particular geographical 
                market. If this value is None, results will be returned for all countries and you 
                are likely to get duplicate results per album, one for each country in 
                which the album is available!

        Returns: 
            A List[Album] if the request succeeded.

        Raises:
            TypeError for invalid types in any argument.
            ValueError for invalid market. TODO: is this even necessary, will raise ex
            HTTPError for web request errors or partial failures.
        
        Calls endpoints:
            GET	/v1/artists/{id}/albums
        '''

        # Type validation
        if (search_limit is not None and not isinstance(search_limit, int)):
            raise TypeError(search_limit)
        if (include_groups is not None and not isinstance(include_groups, List[str])):
            raise TypeError(include_groups)
        if (market is not None and not isinstance(market, str)):
            raise TypeError(market)

        # Save params for lazy loading check
        search_query = (search_limit, include_groups, market)

        # Construct params for API call
        _artist_id = self.artist_id().contents()
        endpoint = Endpoint.ARTIST_GET_ALBUMS.format(artist_id)
        uri_params = dict()
        # TODO: when testing, double check the valid values (and if the constants exist)
        if (include_groups is not None and len(include_groups) > 0):
            uri_params['include_groups'] = ",".join()
        if (market is not None):
            uri_params['market'] = market
        
        # Each API call can take 1-50 requests as "limit", or no limit.
        api_call_limit = 50
        offset = 0
        num_requests = math.ceil(search_limit / api_call_limit) if search_limit else float("inf")

        # Initialize self.albums if different query or never previously called
        self.albums = self.albums if self.albums is not None and \
            search_query == self._albums_query_params else list()

        # Execute requests
        while (num_requests > 0):
            if (search_limit is None):
                search_limit = api_call_limit
            else:
                search_limit = min(search_limit, api_call_limit)
            uri_params['limit'] = search_limit
            uri_params['offset'] = offset
            response_json, status_code = self.session._request(
                request_type=const.REQUEST_GET, 
                endpoint=endpoint, 
                uri_params=uri_params
            )

            items = response_json['items']
            for item in items:
                self.albums.append(Album(item))

            # Last page reached
            if (response_json['next'] == 'null'):
                break

            num_requests -= 1
            offset += api_call_limit

        # Update stored params for lazy loading
        self._albums_query_params = search_query
        
        return self.albums
    
    
    def top_tracks(self,
        market = const.TOKEN_REGION,
        search_limit = 10,
    ):
        ''' Gets the top tracks associated with the current Spotify artist.
        
        Args:
            market: str, an ISO 3166-1 alpha-2 country code or the string const.TOKEN_REGION.
            search_limit: (Optional) int, the maximum number of results to return.

        Returns: 
            A List[Track] if the request succeeded.

        Raises:
            TypeError for invalid types in any argument.
            ValueError if market is None.
            ValueError for invalid market. TODO: is this even necessary, will raise ex
            ValueError if search_limit is > 10: this is the Spotify API's search limit.
            HTTPError for web request errors.
        
        Calls endpoints:
            GET	/v1/artists/{id}/top-tracks
        '''

        # Note: This search limit is not part of the API, Spotify always returns up to 10.
        # Market query param is 'country' in the API but named marked for consistency
        
        # Type validation
        if (search_limit is not None and not isinstance(search_limit, int)):
            raise TypeError(search_limit)
        if (market is not None and not isinstance(market, str)):
            raise TypeError(market)

        # Argument validation
        if (market is None):
            raise ValueError(market)
        if (search_limit > 10):
            raise ValueError(search_limit)

        # Save params for lazy loading check
        search_query = (country, search_limit)

        # Construct params for API call
        _artist_id = self.artist_id().contents()
        endpoint = Endpoint.ARTIST_TOP_TRACKS.format(_artist_id)
        uri_params = dict()
        if (market is not None):
            uri_params['country'] = market

        # Initialize self.top_tracks if different query or never previously called
        self.top_tracks = self.top_tracks if self.top_tracks is not None and \
            search_query == self._top_tracks_query_params else list()

        # Execute requests
        response_json, status_code = self.session._request(
            request_type=const.REQUEST_GET, 
            endpoint=endpoint, 
            uri_params=uri_params
        )

        items = response_json['items']
        for item in items:
            self.top_tracks.append(Track(item))

        # Update stored params for lazy loading
        self._albums_query_params = search_query
        
        return self.albums[:search_limit]
    
    def related_artists(self,
        search_limit = 20,
    ):
        '''
        Gets Spotify catalog information about artists similar to a given artist.

        Args:
            search_limit: (Optional) int, the maximum number of results to return.

        Returns: 
            A response object containing a List[Artist] if the request succeeded.

        Raises:
            TypeError for invalid types in any argument.
            ValueError if search_limit is > 20: this is the Spotify API's search limit.
            HTTPError for web request errors.
        
        Calls endpoints:
            GET	/v1/artists/{id}/related-artists
        '''

        # This search limit is not part of the API, Spotify always returns up to 20.
        
        # Type validation
        if (search_limit is not None and not isinstance(search_limit, int)):
            raise TypeError(search_limit)

        # Argument validation
        if (search_limit > 20):
            raise ValueError(search_limit)

        # Save params for lazy loading check
        search_query = (search_limit)

        # Construct params for API call
        _artist_id = self.artist_id().contents()
        endpoint = Endpoint.ARTIST_RELATED_ARTISTS.format(_artist_id)

        # Initialize self.top_tracks if different query or never previously called
        self.related_artists = self.related_artists if self.related_artists is not None and \
            search_query == self._related_artists_query_params else list()

        # Execute requests
        response_json, status_code = self.session._request(
            request_type=const.REQUEST_GET, 
            endpoint=endpoint, 
        )

        items = response_json['items']
        for item in items:
            self.related_artists.append(Artist(item))

        # Update stored params for lazy loading
        self._related_artists_query_params = search_query

        return self.related_artists[:search_limit]
