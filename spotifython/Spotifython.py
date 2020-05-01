from response import *

# This object should be constructed by the user to instantiate the 
# session of Spotify Web API usage.
class Spotifython:
    
    def __init__(self, token, timeout=None):
        self.token = token
        self.timeout = timeout
    
    '''
    Updates the stored Spotify authentication token for this instance.

    Args:
        token: the new Spotify authentication token.

    Exceptions:
        TypeError for invalid types in any argument.
    '''
    def reauthenticate(self, token: str):
        self.token = token

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
                self.href = self._raw.get("href", None) # str
                self.items = self._raw.get("items", list()) # List[]
                self.limit = self._raw.get("limit", None) # int
                self.next = self._raw.get("next", None) # str
                self.offset = self._raw.get("offset", None) # int
                self.previous = self._raw.get("previous", None) # str
                self.total = self._raw.get("total", None) # int

        def __init__(self, search_info: dict):
            self._raw = search_info
            self._albums_paging = SearchPage(self._raw.get("albums", dict()))
            self._artists_paging = SearchPage(self._raw.get("artists", dict()))
            self._playlists_paging = SearchPage(self._raw.get("playlists", dict()))
            self._tracks_paging = SearchPage(self._raw.get("tracks", dict()))

        def albums(self) -> List[Album]:
            return self._albums_paging.get("items", list())

        def artists(self) -> List[Artist]:
            return self._artists_paging.get("items", list())

        def playlists(self) -> List[Playlist]:
            return self._playlists_paging.get("items", list())
        
        def tracks(self) -> List[Track]:
            return self._tracks_paging.get("items", list())
    
    ##################################
    # API Calls
    ##################################

    '''
    Searches for content with the given query.

    Args:
        query: search query keywords and optional field filters and operators.
        type: a comma-separated list of the types of results to search for.
            Valid arguments are "album", "artist", "playlist", "track".
            Note: shows and episodes are not supported in this version.
        search_limit: the maximum number of results to return.
        market: (Optional) An ISO 3166-1 alpha-2 country code or the string 
            from_token. If a country code is specified, only artists, albums,
            and tracks with content that is playable in that market is returned.
            Note:
            - Playlist results are not affected by the market parameter.
            - If market is set to from_token, and a valid access token is 
            specified in the request header, only content playable
            in the country associated with the user account, is returned.
        include_external: (Optional) Valid argument is "audio": if specified,
            the response will include any relevant audio content that is 
            hosted externally. By default external content is filtered out 
            from responses.

    Returns:
        A response object containing a SearchResult if the request succeeded.

    Exceptions:
        TypeError for invalid types in any argument.
        ValueError if query type, market, or include_external is invalid.
        ValueError if search_limit is > 2000: this is the Spotify API's search limit.

    Calls endpoints: 
        GET   /v1/search
    ''' 
    def search(self, 
        query: str, 
        type: str, # album,artist,playlist,track,show,episode (comma separated)
        search_limit: int,
        market: str = None,
        include_external: str = None # audio
    ) -> Response: # SearchResult

        # Don't forget to encode the spaces in strings!
        # See guidelines in Search -> "Writing a Query - Guidelines" 
        # for more specification details that need to be implemented.
        
        # Search limit is internally represented using API calls with params:
        #    limit: int = None,
        #    offset: int = None,
        # It is a required field due to the offset + limit being 2000, which would take 40 backend API calls.
        # Throw an error if > 2000.
        
        return Response(status=Response.OK, contents=SearchResult(dict()))

    '''
    Gets the albums with the given Spotify album ids.

    Args:
        album_ids: a string or list of strings of the Spotify album ids to search for.
        market: (Optional) An ISO 3166-1 alpha-2 country code or the string 'from_token'. 
            Provide this parameter if you want to apply Track Relinking.

    Returns:
        A response object containing an Album or List[Album] if the request succeeded.

    Exceptions:
        TypeError for invalid types in any argument.
        ValueError if market type is invalid.

    Calls endpoints: 
        GET   /v1/albums/{id}
        GET   /v1/albums
    ''' 
    def get_albums(self, 
        album_ids: Union[str, List[str]], # If list, is comma separated
        market: str = None
    ) -> Response: # Union[Album, List[Album]]
        return None

    '''
    Gets the artists with the given Spotify artists ids.

    Args:
        artist_ids: a string or list of strings of the Spotify artist ids to search for.

    Returns:
        A response object containing an Artist or List[Artists] if the request succeeded.

    Exceptions:
        TypeError for invalid types in any argument.

    Calls endpoints: 
        GET   /v1/artists/{id}
        GET   /v1/artists
    ''' 
    def get_artists(self, 
        artist_ids: Union[str, List[str]] # If list, is comma separated
    ) -> Response: # Union[Artist, List[Artist]]
        return None

    '''
    Gets the tracks with the given Spotify track ids.

    Args:
        track_ids: a string or list of strings of the Spotify track ids to search for.
        market: (Optional) An ISO 3166-1 alpha-2 country code or the string 'from_token'. 
            Provide this parameter if you want to apply Track Relinking.

    Returns:
        A response object containing a Track or List[Track] if the request succeeded.

    Exceptions:
        TypeError for invalid types in any argument.
        ValueError if market type is invalid.

    Calls endpoints: 
        GET   /v1/tracks/{id}
        GET   /v1/tracks
    ''' 
    def get_tracks(self, 
        track_ids: Union[str, List[str]], # If list, is comma separated
        market: str = None
    ) -> Response: # Union[Track, List[Track]]
        return None
    
    '''
    Gets the users with the given Spotify user ids.

    Args:
        user_ids: a string or list of strings of the Spotify user id to search for.
    
    Returns: A response object containing a User or List[User] if the request succeeded.

    Exceptions:
        TypeError for invalid types in any argument.
    
    Calls endpoints:
        GET	/v1/users/{user_id}
    '''
    def get_users(self, 
        user_ids: Union[str, List[str]]
    ) -> Response: # Union[User, List[User]]
        return None
    
    '''
    Gets the user associated with the current Spotify API authentication key.
    
    Returns: 
        A response object containing a User if the request succeeded.

    Exceptions:
        ValueError if the Spotify API key is not valid. TODO: is this ok
    
    Calls endpoints:
        GET	/v1/me
    '''
    def get_current_user(self) -> Response: # User
        return None
    
    '''
    Gets the tracks with the given Spotify playlist ids.

    Args:
        playlist_ids: a string or list of strings of the Spotify playlist ids to search for.
        fields: (Optional) Filters for the query: a comma-separated list of the fields to return. 
            If omitted, all fields are returned. A dot separator can be used to specify 
            non-reoccurring fields, while parentheses can be used to specify reoccurring 
            fields within objects. Use multiple parentheses to drill down into nested objects. 
            Fields can be excluded by prefixing them with an exclamation mark.
        market: (Optional) An ISO 3166-1 alpha-2 country code or the string 'from_token'. 
            Provide this parameter if you want to apply Track Relinking.

    Returns:
        A response object containing a Playlist or List[Playlist] if the request succeeded.

    Exceptions:
        TypeError for invalid types in any argument.
        ValueError if market type is invalid.

    Calls endpoints:
        GET	/v1/playlists/{playlist_id}
    '''
    def get_playlist(self,
        playlist_ids: Union[str, List[str]],
        fields: str = None,
        market: str = None
    ) -> Response: # Union[Playlist, List[Playlist]]

        # Note: additional_types is also a valid request param - it 
        # has been deprecated and therefore is removed from the API wrapper.

        return None