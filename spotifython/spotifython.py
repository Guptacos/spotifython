from typing import Union, List
import requests
import math

from endpoint import Endpoint

# from album import Album
# from artist import Artist
# from playlist import Playlist
# from track import Track
# from user import User

##################################
# Stub Classes
##################################

class Album:
    def __init__(self, raw):
        self._raw = raw

class Artist:
    def __init__(self, raw):
        self._raw = raw

class Player:
    def __init__(self, raw):
        self._raw = raw

class Playlist:
    def __init__(self, raw):
        self._raw = raw

class Spotifython:
    def __init__(self, raw):
        self._raw = raw

class Track:
    def __init__(self, raw):
        self._raw = raw

class User:
    def __init__(self, raw):
        self._raw = raw

##################################
# End Stub Classes
##################################

# This object should be constructed by the user to instantiate the 
# session of Spotify Web API usage.
class Spotifython:
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
    SPOTIFY_PAGE_SIZE = 50
    SPOTIFY_MAX_PLAYLISTS = 100000
    SPOTIFY_MAX_LIB_SIZE = 10000
    SEARCH_RESPONSE_TYPE_ALBUM = 'albums'
    SEARCH_RESPONSE_TYPE_ARTIST = 'artists'
    SEARCH_RESPONSE_TYPE_PLAYLIST = 'playlists'
    SEARCH_RESPONSE_TYPE_TRACK = 'tracks'
    
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
    def _request(self,
                 request_type: str,
                 endpoint: str,
                 body: dict=None,
                 uri_params: dict=None
    ):
        '''
            Does request with retry. This method should return a tuple (response_json, status_code) if
            the request is executed, and raises an Exception if the request type is invalid.
   
            Args:
                request_type: one of REQUEST_GET, REQUEST_POST, REQUEST_PUT, REQUEST_DELETE.
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
        headers = {
            'Authorization': 'Bearer ' + self._token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.request(request_type,
                             request_uri,
                             json=body,
                             params=uri_params,
                             headers=headers,
                             timeout=self._timeout)
        
        # Extract the information from response. No exception should be present
        # in the event of a successful response, but the response json may or
        # may not be present.

        # r.raise_for_status() raises HTTPError if request unsuccessful - this
        #is a real error
        r.raise_for_status() 
    
        try: # content = Union[json, bytes]
            # r.json() raises ValueError if no content - this is not an error
            # and no exception should be returned
            content = r.json()
        except (ValueError):
            content = None # May be malformed or no 

        return content, r.status_code

    # User should never call this constructor. As a result, they should never
    # have access to the search_info structure prior to creating an SearchResult.
    # Internally, the search result will perform all necessary API calls to get the
    # desired number of search results (up to search limit).
    class SearchResult:

        def __init__(self, search_info: dict = dict()):
            self._raw = search_info
            self._albums_paging = self._raw.get('albums', dict()).get('items', list())
            self._artists_paging = self._raw.get('artists', dict()).get('items', list())
            self._playlists_paging = self._raw.get('playlists', dict()).get('items', list())
            self._tracks_paging = self._raw.get('tracks', dict()).get('items', list())

        # Internal: Update search results via paginated searches
        def _add_albums(self, albums: List[Album]):
            self._albums_paging += albums
        
        def _add_artists(self, artists: List[Artist]):
            self._artists_paging += artists
        
        def _add_playlists(self, playlists: List[Playlist]):
            self._playlists_paging += playlists
        
        def _add_tracks(self, tracks: List[Track]):
            self._tracks_paging += tracks

        # Field accessors
        def albums(self) -> List[Album]:
            return self._albums_paging.get('items', list())

        def artists(self) -> List[Artist]: 
            return self._artists_paging.get('items', list())

        def playlists(self) -> List[Playlist]:
            return self._playlists_paging.get('items', list())
        
        def tracks(self) -> List[Track]: 
            return self._tracks_paging.get('items', list())
    
    ##################################
    # API Calls
    ##################################

    def search(self, 
        query: str, 
        types: Union[str, List[str]],
        limit: int,
        market: str = TOKEN_REGION,
        include_external_audio: bool = False
    ) -> SearchResult:
        '''
        Searches for content with the given query.

        Args:
            query: search query keywords and optional field filters and operators.
            types: singular search type or a list of the types of results to search for.
                Valid arguments are ALBUM, ARTIST, PLAYLIST, and TRACK.
                Note: shows and episodes are not supported in this version.
            limit: the maximum number of results to return.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string 
                TOKEN_REGION. If a country code is specified, only artists, albums,
                and tracks with content that is playable in that market is returned.
                Note:
                - Playlist results are not affected by the market parameter.
                - If market is set to TOKEN_REGION, and a valid access token is 
                specified in the request header, only content playable
                in the country associated with the user account, is returned.
                - If market is set to None, no market is passed to Spotify's Web API, 
                and its default behavior is invoked.
            include_external_audio: (Optional) If true,
                the response will include any relevant audio content that is 
                hosted externally. By default external content is filtered out 
                from responses.

        Returns:
            Returns a SearchResult if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if query type or market is invalid. TODO: how to validate?
            ValueError if limit is > 2000: this is the Spotify API's search limit.
            HTTPError if failure or partial failure.

        Calls endpoints: 
            GET   /v1/search
        ''' 
        
        # Search limit is internally represented using API calls with params:
        #    limit: int = None,
        #    offset: int = None,
        # It is a required field due to the offset + limit being 2000, which would take
        # 40 backend API calls.
        # Throw an error if > 2000.

        # Internally, include_external='audio' is the only valid argument.

        # Type validation
        if (not isinstance(query, str)):
            raise TypeError(query)
        if (not isinstance(types, str) and not isinstance(types, List[str])):
            raise TypeError(types)
        if (not isinstance(limit, int)):
            raise TypeError(limit)
        if (market is not None and not isinstance(market, str)):
            raise TypeError(market)
        if (not isinstance(include_external_audio, bool)):
            raise TypeError(include_external_audio)

        # Encode the spaces in strings! See 'Search -> Writing a Query - Guidelines'
        # in the Spotify Web API reference for more details.
        encoded_query = query.replace(' ', '+')

        # Argument validation
        types = types if isinstance(types, List[str]) else list(types)
        valid_types = [ALBUM, ARTIST, PLAYLIST, TRACK]
        for search_type_filter in types:
            if (search_type_filter not in valid_types):
                raise ValueError(types)
        if (limit > 2000):
            raise ValueError("Spotify only supports up to 2000 search results.")

        # Construct params for API call
        endpoint = Endpoint.SEARCH
        uri_params = dict()
        uri_params['q'] = encoded_query
        if (market is not None):
            uri_params['market'] = market
        if (include_external_audio):
            uri_params['include_external'] = 'audio'

        # A maximum 50 search results per search type can be returned per API call
        api_call_limit = 50
        total_search_limit = 2000
        num_requests = math.ceil(len(limit) / api_call_limit) if limit is not None else float('inf')
        limit = min(total_search_limit, limit)
        offset = 0
        
        # Initialize SearchResult object
        result = self.SearchResult()
        
        # We want the plural search types, while our constants are singular search types.
        remaining_types = [s + 's' for s in types]

        while (num_requests > 0):
            uri_params['type'] = ','.join(remaining_types)
            uri_params['limit'] = limit
            uri_params['offset'] = offset

            # Execute requests
            response_json, status_code = self._request(
                request_type=REQUEST_GET, 
                endpoint=endpoint, 
                uri_params=uri_params
            )

            # Extract data per search type
            for t in remaining_types:
                items = response_json[t]['items']
                acc = list()

                # Add items to accumulator
                for item in items:
                    if (t is SEARCH_RESPONSE_TYPE_ALBUM):
                        acc.append(Album(item))
                    elif (t is SEARCH_RESPONSE_TYPE_ARTIST):
                        acc.append(Artist(item))
                    elif (t is SEARCH_RESPONSE_TYPE_PLAYLIST):
                        acc.append(Playlist(item))
                    elif (t is SEARCH_RESPONSE_TYPE_TRACK):
                        acc.append(Track(item))

                # Update accumulated results into search result
                if (t is SEARCH_RESPONSE_TYPE_ALBUM):
                    result._add_albums(acc)
                elif (t is SEARCH_RESPONSE_TYPE_ARTIST):
                    result._add_artists(acc)
                elif (t is SEARCH_RESPONSE_TYPE_PLAYLIST):
                    result._add_playlists(acc)
                elif (t is SEARCH_RESPONSE_TYPE_TRACK):
                    result._add_tracks(acc)

            offset += api_call_limit
            num_requests -= 1
            
            # Only make necessary search queries
            new_remaining_types = list()
            for t in remaining_types:
                if (response_json[t]['next'] != 'null'):
                    new_remaining_types.append(t)
            remaining_types = new_remaining_types
            
        return result

    def get_albums(self, 
        album_ids: Union[str, List[str]],
        market: str = TOKEN_REGION
    ) -> Union[Album, List[Album]]: 
        '''
        Gets the albums with the given Spotify album ids.

        Args:
            album_ids: a string or list of strings of the Spotify album ids to search for.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string TOKEN_REGION. 
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web API, and its default
                behavior is invoked.

        Returns:
            Returns an Album or List[Album] if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

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
                request_type=REQUEST_GET, 
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
    ) -> Union[Artist, List[Artist]]:
        '''
        Gets the artists with the given Spotify artists ids.

        Args:
            artist_ids: a string or list of strings of the Spotify artist ids to search for.

        Returns:
            Returns an Artist or List[Artists] if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            HTTPError if failure or partial failure.

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
                request_type=REQUEST_GET, 
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
        market: str = TOKEN_REGION
    ) -> Union[Track, List[Track]]:
        '''
        Gets the tracks with the given Spotify track ids.

        Args:
            track_ids: a string or list of strings of the Spotify track ids to search for.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string TOKEN_REGION. 
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web API, and its default
                behavior is invoked.

        Returns:
            Returns a Track or List[Track] if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

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
                request_type=REQUEST_GET, 
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
    ) -> Union[User, List[User]]:
        '''
        Gets the users with the given Spotify user ids.

        Args:
            user_ids: a string or list of strings of the Spotify user id to search for.
        
        Returns: 
            Returns a User or List[User] if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            HTTPError if failure or partial failure.
        
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
            # TODO: Partial failure - if user with user_id does not exist, status_code is 404
            response_json, status_code = self._request(
                request_type=REQUEST_GET, 
                endpoint=endpoint, 
                uri_params=uri_params
            )
            result.append(User(response_json))

        return result if len(result) != 1 else result[0]
    
    def get_current_user(self) -> User:
        '''
        Gets the user associated with the current Spotify API authentication key.
        
        Returns: 
            A response object containing a User if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            ValueError if the Spotify API key is not valid.
            ValueError if the response is empty.
            HTTPError if failure or partial failure.
        
        Calls endpoints:
            GET	/v1/me
        '''

        # Construct params for API call
        endpoint = Endpoint.SEARCH_GET_CURRENT_USER

        # Execute requests
        try:
            response_json, status_code = self._request(
                request_type=REQUEST_GET, 
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
        market: str = TOKEN_REGION
    ) -> Union[Playlist, List[Playlist]]:
        '''
        Gets the tracks with the given Spotify playlist ids.

        Args:
            playlist_ids: a string or list of strings of the Spotify playlist ids to search for.
            fields: (Optional) Filters for the query: a comma-separated list of the fields to return. 
                If omitted, all fields are returned. A dot separator can be used to specify 
                non-reoccurring fields, while parentheses can be used to specify reoccurring 
                fields within objects. Use multiple parentheses to drill down into nested objects. 
                Fields can be excluded by prefixing them with an exclamation mark.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string TOKEN_REGION. 
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web API.

        Returns:
            A response object containing a Playlist or List[Playlist] if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

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
                request_type=REQUEST_GET, 
                endpoint=endpoint, 
                uri_params=uri_params
            )

            result.append(Playlist(item))

        return result if len(result) != 1 else result[0]
