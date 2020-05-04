from typing import Union
from response import Response
from endpoint import Endpoint
import requests

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
    REQUEST_TIMEOUT = 10 # timeout in seconds
    
    def __init__(self, token):
        self._token = token
    
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
            Does request with retry. This method should return a tuple ((response_json, status_code), Exception) if
            the request is executed, and (None, TypeError) if the request type is invalid.
            
            TODO: how to most effectively return informative information? There are several edge case scenarios:
                1) 204 No content - leads to return with no content, but successful status and no exception.
                2) An actual failure (HTTP 400+) - leads to return with potential content, failed status code, and 
                an exception present.
                3) Regardless of what the scenarios are, do we want to try avoiding the inclusion of the response obj?
                Otherwise we can easily return the response object and a corresponding exception as the error.

            The reasoning behind providing an Exception instead of the return status code is that the Requests module
            provides an HTTPError object in the event of an unsuccessful web request.
            
            Args:
                request_type: one of sp.REQUEST_GET, sp.REQUEST_POST, sp.REQUEST_PUT, sp.REQUEST_DELETE.
                endpoint: an endpoint string defined in the Endpoint class.
                body: (Optional) dictionary of values for the request body.
                uri_params: (Optional) params to encode into the uri.

            Returns:
                On success, returns the request JSON and Exception=None.
                On failure, returns
                    (None, TypeError) if the request type is invalid.
                    On request failure, returns the response contents as text and one of several exceptions:    
                        requests.exceptions.HTTPError if there is an error with the HTTP request.
                        ValueError if there is an error extracting valid JSON.
                Note: response text is provided using the encoding provided by requests.Response.encoding.
                    
            Usage:
                response, err = _request.(...)
        '''
        request_uri = Endpoint.BASE_URI + endpoint
        headers = {"Authorization: Bearer ": self._token}

        if (request_type is self.REQUEST_GET):
            r = requests.get(request_uri, params=uri_params, headers=headers, timeout=)
        else if (request_type is self.REQUEST_POST):
            r = requests.post(request_uri, data=body, headers=headers)
        else if (request_type is self.REQUEST_PUT):
            r = requests.put(request_uri, data=body, headers=headers)
        else if (request_type is self.REQUEST_DELETE):
            r = requests.delete(request_uri, headers=headers)
        else:
            return None, TypeError(request_type)
        
        # Extract the information from response. No exception should be present in the event of a successful 
        # response, but the response json may or may not be present.

        try:
            # r.raise_for_status() returns HTTPError if request unsuccessful - this is a real error
            r.raise_for_status() 
        except (requests.exceptions.HTTPError) as err:
            error = err
    
        try:
            # r.json() throws ValueError if no content - this is not an error and no exception should be returned
            content = r.json()
        except (ValueError):
            content = r.content 

        return (content, r.status_code), error

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
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid.

        Calls endpoints: 
            GET   /v1/albums/{id}
            GET   /v1/albums
        ''' 
        return None

    def get_artists(self, 
        artist_ids: Union[str, List[str]]
    ) -> Response: # Union[Artist, List[Artist]]
        '''
        Gets the artists with the given Spotify artists ids.

        Args:
            artist_ids: a string or list of strings of the Spotify artist ids to search for.

        Returns:
            A response object containing an Artist or List[Artists] if the request succeeded.
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.

        Calls endpoints: 
            GET   /v1/artists/{id}
            GET   /v1/artists
        ''' 
        return None

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
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid.

        Calls endpoints: 
            GET   /v1/tracks/{id}
            GET   /v1/tracks
        ''' 
        return None
    
    def get_users(self, 
        user_ids: Union[str, List[str]]
    ) -> Response: # Union[User, List[User]]
        '''
        Gets the users with the given Spotify user ids.

        Args:
            user_ids: a string or list of strings of the Spotify user id to search for.
        
        Returns: A response object containing a User or List[User] if the request succeeded.
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
        
        Calls endpoints:
            GET	/v1/users/{user_id}
        '''
        return None
    
    def get_current_user(self) -> Response: # User
        '''
        Gets the user associated with the current Spotify API authentication key.
        
        Returns: 
            A response object containing a User if the request succeeded.
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            ValueError if the Spotify API key is not valid. TODO: is this ok
        
        Calls endpoints:
            GET	/v1/me
        '''
        return None
    
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
            On failure, returns a response object containing the raw Spotify Web API
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid.

        Calls endpoints:
            GET	/v1/playlists/{playlist_id}
        '''

        # Note: additional_types is also a valid request param - it 
        # has been deprecated and therefore is removed from the API wrapper.

        return None