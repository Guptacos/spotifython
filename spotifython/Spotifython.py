from typing import Union
import requests
import math

from response import Response
from endpoint import Endpoint

from album import Album
from artist import Artist
from playlist import Playlist
from track import Track
from user import User

# This object should be constructed by the user to instantiate the 
# session of Spotify Web API usage.
class Spotifython:

    # Constants
    TOKEN_REGION = 'from_token'
    ALBUM = 'album'
    ARTIST = 'artist'
    PLAYLIST = 'playlist'
    TRACK = 'track'
    SHOW = 'show'
    EPISODE = 'episode'
    REQUEST_GET = 'GET'
    REQUEST_PUT = 'PUT'
    REQUEST_DELETE = 'DELETE'
    REQUEST_POST = 'POST'
    USER = 'user'
    LONG = 'long'
    MEDIUM = 'medium'
    SHORT = 'short'
    CONTEXT = 'context'
    OFF = 'off'
    KEEP_PLAY_STATE = 'keep_play_state'
    FORCE_PLAY = 'force_play'
    PUBLIC = 'public'
    PRIVATE = 'private'
    PRIVATE_COLLAB = 'private_collab'
    DEFAULT_REQUEST_TIMEOUT = 10 # in seconds
    
    def __init__(self, token: str, timeout: int = DEFAULT_REQUEST_TIMEOUT):
        self._token = token
        self._timeout = timeout
    
    def reauthenticate(self, token: str):
        '''
        Updates the stored Spotify authentication token for this instance.

        Args:
            token: the new Spotify authentication token.

        Exceptions:
            TypeError for invalid types in any argument.
        '''
        self._token = token
    
    ##################################
    # HTTP REQUEST 
    ##################################
    # https://stackoverflow.com/questions/23267409/how-to-implement-retry-mechanism-into-python-requests-library
    
    # request_type: REQUEST_GET, REQUEST_POST, REQUEST_PUT, REQUEST_DELETE
    def _request(request_type: str, endpoint: str, body: dict=None, uri_params: dict=None):
        '''
            Does request with retry. This method should return a tuple (response_json, status_code) if
            the request is executed, and raises an Exception if the request type is invalid.
   
            Args:
                request_type: one of sp.REQUEST_GET, sp.REQUEST_POST, sp.REQUEST_PUT, sp.REQUEST_DELETE.
                endpoint: an endpoint string defined in the Endpoint class.
                body: (Optional) dictionary of values for the request body.
                uri_params: (Optional) params to encode into the uri.

            Returns:
                Only returns when successful. Returns the request JSON and the request's status code.
                If the response contains invalid JSON or no content, response_json=None.

            Exceptions:      
                Raises an HTTPError object in the event of an unsuccessful web request.
                All exceptions are as according to requests.Request.

            Usage:
                response_json, status_code = _request(...)
        '''
        request_uri = Endpoint.BASE_URI + endpoint
        headers = {"Authorization": "Bearer " + self._token}
        r = requests.request(request_type, request_uri, data=body, params=uri_params, headers=headers, timeout=self._timeout)
        
        # Extract the information from response. No exception should be present in the event of a successful 
        # response, but the response json may or may not be present.

        # r.raise_for_status() raises HTTPError if request unsuccessful - this is a real error
        r.raise_for_status() 
    
        try: # content = Union[json, bytes]
            # r.json() raises ValueError if no content - this is not an error and no exception should be returned
            content = r.json()
        except (ValueError):
            content = None # May be malformed or no 

        return content, r.status_code

    # User should never call this constructor. As a result, they should never
    # have access to the search_info structure prior to creating an SearchResult.
    # Internally, the search result will perform all necessary API calls to get the
    # desired number of search results (up to search_limit).
    class SearchResult:

        # Each category of search result from a query is kept within a paging object
        # User should never call this constructor. As a result, they should never
        # have access to the paging_info structure prior to creating an SearchPage.
        # This class is for internal representation of sesarch results used to execute 
        # API calls and aggregate data.
        class SearchPage:
            def __init__(self, paging_info: dict):
                self._raw = paging_info
                self.href = self._raw.get('href', None) # str
                self.items = self._raw.get('items', list()) # List[]
                self.limit = self._raw.get('limit', None) # int
                self.next = self._raw.get('next', None) # str
                self.offset = self._raw.get('offset', None) # int
                self.previous = self._raw.get('previous', None) # str
                self.total = self._raw.get('total', None) # int

        def __init__(self, search_info: dict):
            self._raw = search_info
            self._albums_paging = SearchPage(self._raw.get('albums', dict()))
            self._artists_paging = SearchPage(self._raw.get('artists', dict()))
            self._playlists_paging = SearchPage(self._raw.get('playlists', dict()))
            self._tracks_paging = SearchPage(self._raw.get('tracks', dict()))

        def albums(self) -> Response: # List[Album]
            return self._albums_paging.get('items', list())

        def artists(self) -> Response: # List[Artist]
            return self._artists_paging.get('items', list())

        def playlists(self) -> Response: # List[Playlist]
            return self._playlists_paging.get('items', list())
        
        def tracks(self) -> Response: # List[Track]
            return self._tracks_paging.get('items', list())
    
    ##################################
    # API Calls
    ##################################

    def search(self, 
        query: str, 
        type: Union[str, List[str]],
        search_limit: int,
        market: str = self.TOKEN_REGION,
        include_external_audio: bool = False
    ) -> Response: # SearchResult
        '''
        Searches for content with the given query.

        Args:
            query: search query keywords and optional field filters and operators.
            type: singular type or a list of the types of results to search for.
                Valid arguments are sp.ALBUM, sp.ARTIST, sp.PLAYLIST, and sp.TRACK.
                Note: shows and episodes are not supported in this version.
            search_limit: the maximum number of results to return.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string 
                sp.TOKEN_REGION. If a country code is specified, only artists, albums,
                and tracks with content that is playable in that market is returned.
                Note:
                - Playlist results are not affected by the market parameter.
                - If market is set to sp.TOKEN_REGION, and a valid access token is 
                specified in the request header, only content playable
                in the country associated with the user account, is returned.
                - If market is set to None, no market is passed to Spotify's Web API, 
                and its default behavior is invoked.
            include_external_audio: (Optional) If true,
                the response will include any relevant audio content that is 
                hosted externally. By default external content is filtered out 
                from responses.

        Returns:
            A response object containing a SearchResult if the request succeeded.
            TODO: update failure behavior including for partial failures
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if query type, market, or include_external is invalid.
            ValueError if search_limit is > 2000: this is the Spotify API's search limit.

        Calls endpoints: 
            GET   /v1/search
        ''' 

        # Don't forget to encode the spaces in strings!
        # See guidelines in Search -> 'Writing a Query - Guidelines' 
        # for more specification details that need to be implemented.
        
        # Search limit is internally represented using API calls with params:
        #    limit: int = None,
        #    offset: int = None,
        # It is a required field due to the offset + limit being 2000, which would take
        # 40 backend API calls.
        # Throw an error if > 2000.

        # Internally, include_external='audio' is the only valid argument.
        
        # TODO

        return Response(status=Response.OK, contents=SearchResult(dict()))

    def get_albums(self, 
        album_ids: Union[str, List[str]],
        market: str = self.TOKEN_REGION
    ) -> Response: # Union[Album, List[Album]]
        '''
        Gets the albums with the given Spotify album ids.

        Args:
            album_ids: a string or list of strings of the Spotify album ids to search for.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string sp.TOKEN_REGION. 
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web API, and its default
                behavior is invoked.

        Returns:
            A response object containing an Album or List[Album] if the request succeeded.
            TODO: update failure behavior including for partial failures
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO

        Calls endpoints: 
            GET   /v1/albums

        Note: the following endpoint is not used.
            GET   /v1/albums/{id} 
        ''' 

        # Type validation
        if (not isinstance(album_ids, str) and not isinstance(album_ids, List[str])):
            raise TypeError(album_ids)
        if (market is not None and not isinstance(market, str)):
            raise TypeError(market)

        # Argument validation
        if (market is None):
            raise ValueError(market)
        
        album_ids = album_ids if isinstance(album_ids, List[str]) else list(album_ids)

        # Construct params for API call
        endpoint = Endpoint.SEARCH_GET_ALBUMS
        uri_params = dict()
        if (market is not None):
            uri_params['market'] = market

        # A maximum 20 albums can be returned per API call
        api_call_limit = 20
        num_requests = math.ceil(len(album_ids) / api_call_limit)
        remaining_album_ids = album_ids
        
        result = list()

        while (num_requests > 0):
            uri_params['ids'] = ','.join(remaining_album_ids[:api_call_limit])

            # Execute requests
            response_json, status_code = self._request(
                request_type=Spotifython.REQUEST_GET, 
                endpoint=endpoint, 
                uri_params=uri_params
            )

            items = response_json['albums']
            
            for item in items:
                result.append(Album(item))
            
            num_requests -= 1
            remaining_album_ids = remaining_album_ids[api_call_limit:]

        return result if len(result) != 1 else result[0]

    def get_artists(self, 
        artist_ids: Union[str, List[str]]
    ) -> Response: # Union[Artist, List[Artist]]
        '''
        Gets the artists with the given Spotify artists ids.

        Args:
            artist_ids: a string or list of strings of the Spotify artist ids to search for.

        Returns:
            A response object containing an Artist or List[Artists] if the request succeeded.
            TODO: update failure behavior including for partial failures
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.

        Calls endpoints: 
            GET   /v1/artists

        Note: the following endpoint is not used.
            GET   /v1/artists/{id}
        ''' 
        
        # Type validation
        if (not isinstance(artist_ids, str) and not isinstance(artist_ids, List[str])):
            raise TypeError(artist_ids)

        artist_ids = artist_ids if isinstance(artist_ids, List[str]) else list(artist_ids)

        # Construct params for API call
        endpoint = Endpoint.SEARCH_GET_ALBUMS
        uri_params = dict()

        # A maximum of 50 artists can be returned per API call
        api_call_limit = 50
        num_requests = math.ceil(len(album_ids) / api_call_limit)
        remaining_artist_ids = artist_ids
        
        result = list()
        
        while (num_requests > 0):
            uri_params['ids'] = ','.join(remaining_artist_ids[:api_call_limit])

            # Execute requests
            response_json, status_code = self._request(
                request_type=Spotifython.REQUEST_GET, 
                endpoint=endpoint, 
                uri_params=uri_params
            )

            items = response_json['artists']
            
            for item in items:
                result.append(Artist(item))
            
            num_requests -= 1
            remaining_artist_ids = remaining_artist_ids[api_call_limit:]

        return result if len(result) != 1 else result[0]

    def get_tracks(self, 
        track_ids: Union[str, List[str]], 
        market: str = self.TOKEN_REGION
    ) -> Response: # Union[Track, List[Track]]
        '''
        Gets the tracks with the given Spotify track ids.

        Args:
            track_ids: a string or list of strings of the Spotify track ids to search for.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string sp.TOKEN_REGION. 
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web API, and its default
                behavior is invoked.

        Returns:
            A response object containing a Track or List[Track] if the request succeeded.
            TODO: update failure behavior including for partial failures
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO

        Calls endpoints: 
            GET   /v1/tracks

        Note: the following endpoint is not used.
            GET   /v1/tracks/{id}
        ''' 

        # Type validation
        if (not isinstance(track_ids, str) and not isinstance(track_ids, List[str])):
            raise TypeError(track_ids)
        if (market is not None and not isinstance(market, str)):
            raise TypeError(market)

        # Argument validation
        if (market is None):
            raise ValueError(market)

        track_ids = track_ids if isinstance(track_ids, List[str]) else list(track_ids)

        # Construct params for API call
        endpoint = Endpoint.SEARCH_GET_TRACKS
        uri_params = dict()
        if (market is not None):
            uri_params['market'] = market

        # A maximum of 50 tracks can be returned per API call
        api_call_limit = 50
        num_requests = math.ceil(len(track_ids) / api_call_limit)
        remaining_track_ids = track_ids
        
        result = list()

        while (num_requests > 0):
            uri_params['ids'] = ','.join(remaining_track_ids[:api_call_limit])

            # Execute requests
            response_json, status_code = self._request(
                request_type=Spotifython.REQUEST_GET, 
                endpoint=endpoint, 
                uri_params=uri_params
            )

            items = response_json['tracks']

            for item in items:
                result.append(Track(item))

            num_requests -= 1
            remaining_track_ids = remaining_track_ids[api_call_limit:]

        return result if len(result) != 1 else result[0]
    
    def get_users(self, 
        user_ids: Union[str, List[str]]
    ) -> Response: # Union[User, List[User]]
        '''
        Gets the users with the given Spotify user ids.

        Args:
            user_ids: a string or list of strings of the Spotify user id to search for.
        
        Returns: A response object containing a User or List[User] if the request succeeded.
            TODO: update failure behavior including for partial failures
            TODO: document partial failure means corresponding object is None in the result
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
        
        Calls endpoints:
            GET	/v1/users/{user_id}
        '''

        # Type validation
        if (not isinstance(user_ids, str) and not isinstance(user_ids, List[str])):
            raise TypeError(user_ids)
        
        user_ids = user_ids if isinstance(user_ids, List[str]) else list(user_ids)

        # Construct params for API call
        endpoint = Endpoint.SEARCH_GET_USER
        uri_params = dict()

        # Each API call can return at most 1 user.
        result = list()
        for user_id in user_ids:
            uri_params['ids'] = user_id

            # Execute requests
            # API behavior: if user with user_id does not exist, status_code is 404
            try:
                response_json, status_code = self._request(
                    request_type=Spotifython.REQUEST_GET, 
                    endpoint=endpoint, 
                    uri_params=uri_params
                )
                result.append(User(response_json))
            except requests.exceptions.HTTPError as e:
                if (e.response.status_code is 404):
                    result.append(None)
                else:
                    raise e

        return result if len(result) != 1 else result[0]
    
    def get_current_user(self) -> Response: # User
        '''
        Gets the user associated with the current Spotify API authentication key.
        
        Returns: 
            A response object containing a User if the request succeeded.
            TODO: update failure behavior
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            ValueError if the Spotify API key is not valid.
            ValueError if the response is empty.
        
        Calls endpoints:
            GET	/v1/me
        '''

        # Construct params for API call
        endpoint = Endpoint.SEARCH_GET_CURRENT_USER

        # Execute requests
        try:
            response_json, status_code = self._request(
                request_type=Spotifython.REQUEST_GET, 
                endpoint=endpoint
            )
        except requests.exceptions.HTTPError as e:
            if (e.request.status_code is 403):
                raise ValueError("Spotify API key is not valid")
            else:
                raise e

        # Impossible to initialize a user with no response_json
        if (response_json is None):
            raise ValueError(response_json)

        return User(response_json)
    
    def get_playlists(self,
        playlist_ids: Union[str, List[str]],
        fields: str = None,
        market: str = self.TOKEN_REGION
    ) -> Response: # Union[Playlist, List[Playlist]]
        '''
        Gets the tracks with the given Spotify playlist ids.

        Args:
            playlist_ids: a string or list of strings of the Spotify playlist ids to search for.
            fields: (Optional) Filters for the query: a comma-separated list of the fields to return. 
                If omitted, all fields are returned. A dot separator can be used to specify 
                non-reoccurring fields, while parentheses can be used to specify reoccurring 
                fields within objects. Use multiple parentheses to drill down into nested objects. 
                Fields can be excluded by prefixing them with an exclamation mark.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string sp.TOKEN_REGION. 
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web API.

        Returns:
            A response object containing a Playlist or List[Playlist] if the request succeeded.
            TODO: update failure behavior
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO

        Calls endpoints:
            GET	/v1/playlists/{playlist_id}
        '''

        # Note: additional_types is also a valid request param - it 
        # has been deprecated and therefore is removed from the API wrapper.

        # Type validation
        if (not isinstance(playlist_ids, str) and not isinstance(playlist_ids, List[str])):
            raise TypeError(playlist_ids)
        if (fields is not None and not isinstance(fields, str)):
            raise TypeError(fields)
        if (market is not None and not isinstance(market, str)):
            raise TypeError(market)

        # Argument validation
        if (market is None):
            raise ValueError(market)

        playlist_ids = playlist_ids if isinstance(playlist_ids, List[str]) else list(playlist_ids)

        # Construct params for API call
        uri_params = dict()
        if (market is not None):
            uri_params['market'] = market
        if (fields is not None):
            uri_params['fields'] = fields

        results = list()
        for playlist_id in playlist_ids:
            endpoint = Endpoint.SEARCH_GET_PLAYLIST.format(playlist_id)

            # Execute requests
            response_json, status_code = self._request(
                request_type=Spotifython.REQUEST_GET, 
                endpoint=endpoint, 
                uri_params=uri_params
            )

            result.append(Playlist(item))

        return result if len(result) != 1 else result[0]