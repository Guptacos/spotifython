from __future__ import annotations

from copy import deepcopy
import base64
import math
import requests
from typeguard import typechecked
from typing import List, Union, Dict, Tuple, TYPE_CHECKING

from endpoint import Endpoint
from response import Response


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


class Album:
    def __init__(self, album_info):
        self._album_type = album_info.get('album_type', '')
        self._artists = list()
        for artist in album_info.get('artists', []):
            self._artists.append(Artist(artist))

        tracks_wrapper = album_info.get('tracks', None)
        if tracks_wrapper != None:
            self._tracks = list()
            for track in tracks_wrapper.get('items', []):
                self._tracks.append(Track(track))

        self._available_markets = album_info.get('available_markets', [])
        self._id = album_info.get('id', '')
        self._images = album_info.get('images', {})
        self._name = album_info.get('name', '')
        self._popularity = album_info.get('popularity', -1)
        self._release_date = album_info.get('release_date', '')

        self._iter = 0

    def __eq__(self, other):
        return isinstance(other, Album) and self._album_id == other._album_id

    # iter and next let you loop through the tracks in the album. len gives you
    # the number of tracks in the album.
    def __iter__(self):
        self._iter = 0
        return self

    def __next__(self):
        if self._iter < len(self._tracks):
            track = self._tracks[self._iter]
            self._iter += 1
            return track
        else:
            raise StopIteration

    def __len__(self):
        return len(self._tracks)

    def artists(self):
        return self._artists

    def tracks(self):
        return self._tracks

    def album_type(self):
        return self._album_type

    def available_markets(self):
        return self._available_markets

    def id(self):
        return self._id

    # TODO: usually has three sizes, maybe take in an optional arg for size,
    # otherwise return the first one (largest).
    def image(self, size=None):
        return self._images[0] if size == None else self._images[0]

    def name(self):
        return self._name

    def popularity(self):
        return self._popularity

    def release_date(self):
        return self._release_date


class Artist:
    # User should never call this constructor. As a result, they should never
    # have access to the artist_info structure prior to creating an Artist.
    def __init__(self, artist_info: dict):
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

    def genres(self) -> List[str]:
        if 'genres' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('genres'))

    def href(self) -> str:
        if 'href' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('href'))
    
    def artist_id(self) -> str: 
        if 'id' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('id'))
    
    def name(self) -> str: 
        if 'name' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('name'))
    
    def popularity(self) -> int: 
        if 'popularity' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('popularity'))
    
    def uri(self) -> str:
        if 'uri' not in self._raw: self._update_fields()
        return Response(status=Response.OK, contents=self._raw.get('uri'))
    
    # If field is not present, update it using the object's artist id
    # Raise ValueError if artist id not present in the raw object data.
    # Uses endpoint: GET https://api.spotify.com/v1/artists/{id}
    def _update_fields(self): # None
        _artist_id = self.artist_id().contents()
        endpoint = f'/v1/artists/{artist_id}'
        response_json, status_code = self._top._request(
            request_type=Spotifython.REQUEST_GET, 
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
        search_limit: int = None,
        include_groups: List[str] = None,
        market: str = Spotifython.TOKEN_REGION,
    ) -> List[Album]: 
        '''
        Gets the albums associated with the current Spotify artist.
        
        Args:
            search_limit: (Optional) the maximum number of results to return.
            include_groups: (Optional) A list of keywords 
                that will be used to filter the response. If not supplied, 
                all album types will be returned. 
                Valid values are: Spotifython.ALBUM, Spotifython.SINGLE, Spotifython.APPEARS_ON, Spotifython.COMPILATION 
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string Spotifython.TOKEN_REGION.
                Supply this parameter to limit the response to one particular geographical 
                market. If this value is None, results will be returned for all countries and you 
                are likely to get duplicate results per album, one for each country in 
                which the album is available!

        Returns: 
            A response object containing a list of Albums if the request succeeded.

        Exceptions:
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
            response_json, status_code = self._top._request(
                request_type=Spotifython.REQUEST_GET, 
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
        market: str = Spotifython.TOKEN_REGION,
        search_limit: int = 10,
    ) -> List[Track]:
        '''
        Gets the top tracks associated with the current Spotify artist.
        
        Args:
            market: An ISO 3166-1 alpha-2 country code or the string Spotifython.TOKEN_REGION.
            search_limit: (Optional) the maximum number of results to return.

        Returns: 
            A response object containing a list of Tracks if the request succeeded.

        Exceptions:
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
        response_json, status_code = self._top._request(
            request_type=Spotifython.REQUEST_GET, 
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
        search_limit: int = 20,
    ) -> List[Artist]:
        '''
        Gets Spotify catalog information about artists similar to a given artist.

        Args:
            search_limit: (Optional) the maximum number of results to return.

        Returns: 
            A response object containing a list of Artist objects 
            if the request succeeded.

        Exceptions:
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
        response_json, status_code = self._top._request(
            request_type=Spotifython.REQUEST_GET, 
            endpoint=endpoint, 
        )

        items = response_json['items']
        for item in items:
            self.related_artists.append(Artist(item))

        # Update stored params for lazy loading
        self._related_artists_query_params = search_query

        return self.related_artists[:search_limit]


class Player():
    ''' Interact with a user's playback, such as pausing / playing the current
        song, modifying the queue, etc.

    Getting an instance of Player should only be done using User.player()

    Shared keyword arguments:
        device_id: the device the command should target.
            The given id must be a device listed in player.available_devices().
            If the id is invalid, response.content() will be set to None, and
            response.status() will contain an error code.

            Defaults to using the currently active device, which is what you
            will want most of the time.

        position: always an integer that represents milliseconds.

    Errors:
        Many of these methods will fail and set response.content() to None if
        there is no active or available device. You should check
        response.status() to see if that was the case.

    Exceptions:
        TypeError:  if incorrectly typed parameters are given.
        ValueError: if parameters with illegal values are given.

    Note:
        Due to the asynchronous nature of many Player commands, you should use
        the Player's getter methods to check that your issued command was
        handled correctly by the player.
    '''

    
    def __init__(self,
                 user: User
    ) -> Player:
        ''' Should only be called from within the User class
        
        Keyword arguments:
            user: the User object that created the Player. For example, User can
                say self._player = Player(self)

        Return:
            An instance of Player.
        '''
        pass


    # Format should be 'Player for user <%s>' with user_id
    def __str__(self) -> str:
        return ''

    
    def next(self,
             device_id: str=None
    ) -> Response: # None
        ''' Skip the current song in the playback

        response.contents():
            None
        '''
        # POST /v1/me/player/next
        pass


    def previous(self,
                 device_id: str=None
    ) -> Response: # None
        ''' Skip to the previous song in the playback, regardless of where in
            the current song playback is.

        response.contents():
            None
        '''
        # POST /v1/me/player/previous


    # Note for me: if nothing playing and pause, raises 403 restriction violated
    def pause(self,
              device_id: str=None
    ) -> Response: # None
        ''' Pause the current playback

        response.contents():
            None
        '''
        # PUT /v1/me/player/pause
        pass


    # Note for me: if playing and resume, raises 403 restriction violated
    def resume(self,
               device_id: str=None
    ) -> Response: # None
        ''' Resume the current playback

        response.contents():
            None
        '''
        # PUT /v1/me/player/play
        pass


    # Future support: inputing a context object
    # Future support: offsetting into context
    # Future support: position in track
    def play(self,
             item: Union[Track, Album, Playlist, Artist],
             device_id: str=None
    ) -> Response: # None
        ''' Change the current track and context for the player

        Uses the currently active device, if one exists.

        Keyword arguments:
            item: an instance of Spotifython.Track, Spotifython.Album, Spotifython.Playlist, or Spotifython.Artist.
                to begin playing.

        Note: Does not currently support playing a specific context, or an
            offset into a playlist, album, or artist. Also does not support
            starting playback at a position in the track, playback will start at
            the beginning of the track.

        response.contents():
            None
        '''
        # PUT /v1/me/player/play
        pass


    def is_paused(self) -> Response: # bool
        ''' Check if the current playback is paused

        Uses the currently active device, if one exists.

        response.contents():
            Success: True if paused, else False
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def is_playing(self) -> Response: # bool
        ''' Check if the current playback is playing (not paused)

        Uses the currently active device, if one exists.

        response.contents():
            Success: True if playing, else False
            Failure: None
        '''
        # GET /v1/me/player
        pass


    # TODO: This method name is not final. Here are alternatives we considered:
    # get_currently_playing
    # now_playing
    # get_active_audio
    # Note for me: in the future, add 'additional_types' to support episodes.
    # Note for me: in the future support returning a context object
    def get_currently_playing(self,
                              market: str=Spotifython.TOKEN_REGION
    ) -> Response: # Track
        ''' Get the currently playing track in the playback

        Uses the currently active device, if one exists.

        Keyword arguments:
            market: (required) a 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                if Spotifython.TOKEN_REGION (default) is given, will use appropriate
                country code for user based on their auth token and location.

        response.contents():
            Success: a Track object
            Failure: None
        '''
        # GET /v1/me/player/currently-playing
        pass


    # Note for me: in the future add a separate device abstraction
    def available_devices(self) -> Response: # List[str]
        ''' Get all devices currently available

        response.contents():
            Success: A list of strings, where each is a device id.
            Failure: None
        '''
        # GET /v1/me/player/devices
        pass


    def get_active_device(self) -> Response: # str
        ''' Get the currently active device

        response.contents():
            Success: The device id of the active device, if a device is active.
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_active_device(self,
                          device_id: str,
                          force_play: str=Spotifython.KEEP_PLAY_STATE
    ) -> Response: # None
        ''' Transfer playback to a different available device

        Keyword arguments:
            force_play: (optional) one of:
                        Spotifython.FORCE_PLAY: resume playback after transfering to new
                            device
                        Spotifython.KEEP_PLAY_STATE: keep the current playback state.

        response.contents():
            None
        '''
        # PUT /v1/me/player
        pass


    def get_shuffle(self) -> Response: # bool
        ''' Get the current shuffle state of the playback

        Uses the currently active device, if one exists.

        response.contents():
            Success: True if shuffle is enabled else False
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_shuffle(self,
                    shuffle_state: bool,
                    device_id: str=None
    ) -> Response: # None
        ''' Set the shuffle state of the active device

        Keyword arguments:
            shuffle_state: True to set shuffle to on, False to set it to off.

        response.contents():
            None
        '''
        # PUT /v1/me/player/shuffle
        pass


    def get_playback_position(self) -> Response: # int
        ''' Get the current position in the currently playing track in ms

        Uses the currently active device, if one exists.

        response.contents():
            Success: the position (in ms) as an int
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_playback_position(self,
                 position: int,
                 device_id: str=None
    ) -> Response: # None
        ''' Set the current position in the currently playing track in ms

        Keyword arguments:
            position: the position (in ms) as an int. Must be non-negative.
                If greater than the len of the track, will play the next song.

        response.contents():
            None
        '''
        # PUT /v1/me/player/seek
        pass


    def get_volume(self) -> Response: # int
        ''' Get the current volume for the playback

        Uses the currently active device, if one exists.

        response.contents():
            Success: the volume (in percent) as an int from 0 to 100 inclusive
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_volume(self,
                   volume: int,
                   device_id: str=None
    ) -> Response: # None
        ''' Set the current volume for the playback

        Keyword arguments:
            volume: the volume (in percent) as an int from 0 to 100 inclusive

        response.contents():
            None
        '''
        # PUT /v1/me/player/volume
        pass


    def get_repeat(self) -> Response: # Union[Spotifython.TRACK, Spotifython.CONTEXT, Spotifython.OFF]
        ''' Get the repeat state for the current playback

        Uses the currently active device, if one exists.

        response.contents():
            Success: one of Spotifython.TRACK, Spotifython.CONTEXT, Spotifython.OFF
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_repeat(self,
                   mode: str,
                   device_id: str=None
    ) -> Response: # None
        ''' Set the repeat state for the current playback

        Keyword arguments:
            mode: one of
                Spotifython.TRACK: repeat the current track
                Spotifython.CONTEXT: repeat the current context (playlist, album, etc.)
                Spotifython.OFF: turn repeat off

        response.contents():
            None
        '''
        # PUT /v1/me/player/repeat
        pass


    # Note for me: add episodes at some point
    def enqueue(self,
                item: Union[Album, Track],
                device_id: str=None
    ) -> Response: # None
        ''' Add an item to the end of the queue
        
        Keyword arguments:
            item: the item to add to the queue. Must be an instance of Spotifython.Album
                or Spotifython.Track. Adding playlists to the queue is not currently
                supported.

        response.contents():
            None
        '''
        # POST /v1/me/player/queue
        pass


# objects created in this constructor
class Playlist:
    """
    A Playlist object.

    Raises TypeError for incorrect types and ValueError for inappropriate
    values.
    """

    def __init__(self, playlist_info: dict, top: Spotifython):
        """
        Playlist constructor that should never be called directly.
        """
        self._raw = deepcopy(playlist_info)
        self._top = top
        self._owner = User(playlist_info.get('owner', {}))
        self._tracks = []
        tracks = playlist_info.get('tracks', {})
        if tracks:
            for item in tracks.get('items', []):
                self._tracks.append(Track(item.get('track', {})))


    def owner(self):
        """
        Returns the owner of the playlist.

        Returns:
        A User object.
        """
        return deepcopy(self._owner)


    def uri(self):
        """
        Returns the URI of the playlist.

        Returns:
        A String URI.
        """
        return self._raw['uri']
        

    def add_tracks(self, tracks: Union[Track, List[Track]], position: int=None):
        """
        Add one or more tracks to the playlist.

        Parameters:
        tracks:   A Track object or list of Track objects to be added.

        Optional Parameters:
        position: An integer specifying the 0-indexed position in the playlist
                  to insert tracks. Position can be omitted to append to the
                  playlist instead.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        body = {}
        uris = []
        if isinstance(tracks, list):
            for track in tracks:
                uris.append(track.uri())
        else:
            uris.append(tracks.uri())
        body['uris'] = uris
        if position:
            body['position'] = position
        response_json, status_code = self._top._request('POST', endpoint, body=body)


    def update_name(self, name: str):
        """
        Update the playlist name.

        Parameters:
        name: A string containing the new name of this playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['name'] = name
        response_json, status_code = self._top._request('PUT', endpoint, body=body)


    def update_description(self, description: str):
        """
        Update the playlist description.

        Parameters:
        description: A string containing the new description of this playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['description'] = name
        response_json, status_code = self._top._request('PUT', endpoint, body=body)


    def update_visibility(self, visibility: str):
        """
        Update the playlist public/private visibility and collaborative access.

        Parameters:
        visibility: One of [Spotifython.PUBLIC, Spotifython.PRIVATE, Spotifython.PRIVATE_COLLAB]
                    containing the new visibility of this playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        if visibility == Spotifython.PUBLIC:
            body['public'] = true
        elif visibility == Spotifython.PRIVATE:
            body['public'] = false
        elif visibility == s.PRIVATE_COLLAB:
            body['public'] = false
            body['collaborative'] = true
        else:
            raise ValueError("Invalid visibility, must be one of [Spotifython.PUBLIC, Spotifython.PRIVATE, Spotifython.PRIVATE_COLLAB]")
        response_json, status_code = self._top._request('PUT', endpoint, body=body)


    # TODO test the response from this endpoint and clarify usage
    def image(self):
        """
        Return the playlist cover image.

        Returns:
        The String URL of the cover image.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_IMAGES.replace('{playlist_id}', self._raw['id'])
        response_json, status_code = self._top._request('GET', endpoint)
        return response_json['url']


    def tracks(self, start: int=0, num_tracks: int=None):
        """
        Return one or more tracks in the playlist.

        Returns the specified number of tracks in the playlist starting at the
        given position. Returns all of the tracks in the playlist when given no
        parameters.

        Optional Parameters:
        start:      An integer specifying the 0-indexed position of the first
                    track to return. Can be omitted to return tracks starting
                    from the first song in the playlist.

        num_tracks: An integer specifying the number of tracks to return. Can
                    be omitted to return as many tracks as are present at
                    start.

        Returns:
        A List of Track objects.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['offset'] = start
        # TODO repeat queries if greater than 100
        if num_tracks:
            body['limit'] = num_tracks
        response_json, status_code = self._top._request('GET', endpoint, body=body)
        tracks = []
        for track in response_json['items']:
            tracks.append(Track(track))
        return tracks

    # TODO test this in practice, what does it actually mean? Nobody knows.
    def remove_tracks(self, tracks: Union[Track, List[Track]]=None, positions:
                      Union[int, List[int]]=None):
        """
        Remove one or more tracks from the playlist.

        When provided with a list of tracks, all occurrences of those tracks in
        the playlist will be removed. Providing a list of track positions will
        only remove the tracks in those positions from the playlist. No tracks
        will be removed if neither of the parameters are provided. If both
        parameters are provided, positions takes precedence.

        Optional Parameters:
        tracks:    A list of Track objects to be removed from the playlist. All
                   occurrences of these tracks will be removed.

        positions: A list of integers specifying the 0-indexed positions of
                   tracks to be removed from the playlist. Only tracks in these
                   positions will be removed.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['tracks'] = []
        if tracks and not positions:
            if not isinstance(tracks, list):
                tracks = [tracks]
            for track in tracks:
                track_info = {}
                track_info['uri'] = track.uri()
                body['tracks'].append(track_info)
        elif positions:
            if not isinstance(positions, list):
                positions = [positions]
            if not tracks:
                all_tracks = self._raw['tracks']['items']
                tracks = [all_tracks[i] for i in range(len(all_tracks)) if i in positions]
            for i in range(len(tracks)):
                if i in positions:
                    track = tracks[i]
                    track_info = {}
                    track_info['uri'] = track['uri']
                    track_info['positions'] = [i]
                    body['tracks'].append(track_info)
        else:
            return
        response_json, status_code = self._top._request('DELETE', endpoint, body=body)

    def reorder_tracks(self, source_index, destination_index, number=1):
        """
        Move one or more tracks to another position in the playlist.

        Moves the specified number of tracks starting at source_index to before
        the track currently at destination_index. If number is unspecified,
        only one track is moved.

        Parameters:
        source_index:      An integer specifying the 0-indexed position of the first
                           track to be moved. A negative integer will be evaluated 
                           from the end of the playlist as negative indices behave in
                           lists. This must be a valid index into a list of length
                           len(playlist).

        destination_index: An integer specifying the 0-indexed position of the track
                           before which the other tracks will be moved. A negative
                           integer will be evaluated from the end of the playlist as
                           negative indices behave in lists. This must be a valid
                           index into a list of length len(playlist).

        Optional Parameters:
        number:            A nonnegative integer specifying the number of tracks to
                           be moved. Specifying 0 will result in no change to the
                           playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        if source_index < 0:
            source_index += len(self._raw['tracks']['items'])
        if destination_index < 0:
            destination_index += len(self._raw['tracks']['items'])
        if source_index < 0 or source_index >= len(self._raw['tracks']['items']):
            raise ValueError
        if destination_index < 0 or destination_index >= len(self._raw['tracks']['items']):
            raise ValueError
        body = {}
        body['range_start'] = source_index
        body['range_length'] = number
        body['insert_before'] = destination_index
        response_json, status_code = self._top._request('PUT', endpoint, body=body)

    def replace_all_tracks(self, tracks):
        """
        Replace all of the tracks in the playlist.

        Parameters:
        tracks: A list of Track objects to populate the playlist. These will
                be the only tracks in the playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['uris'] = []
        for track in tracks:
            body['uris'].append(track.uri())
        response_json, status_code = self._top._request('PUT', endpoint, body=body)

    # TODO test this, no example in web api reference
    def replace_image(self, image):
        """
        Replace the playlist cover image.

        The image must be a JPEG and can be at most 256 KB in size.

        Parameters:
        image: A string containing the filename of the image to use as the
               playlist cover image. The image must be a JPEG up to 256 KB.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_IMAGES.replace('{playlist_id}', self._raw['id'])
        body = []
        with open(image, "rb") as f:
            body.append(base64.b64encode(f.read()))
        response_json, status_code = self._top._request('GET', endpoint, body=body)

    def __str__(self):
        """Return a printable representation of the playlist."""
        return self._raw['name']

    def __len__(self):
        """Return the number of tracks in the playlist."""
        return len(self._raw['tracks']['items'])


AUDIO_FEATURES = 'GET https://api.spotify.com/v1/audio-features/%s'
AUDIO_ANALYSIS = 'GET https://api.spotify.com/v1/audio-features/%s'


class Track:
    # User should never call this constructor. As a result, they should never
    # have access to the track_info structure prior to creating a track. This
    # assumption lets us modify the track_info object willy-nilly.
    def __init__(self, track_info: dict):
        self._raw = deepcopy(track_info)

        self._album = Album(track_info.get('album', None))
        self._artists = list()
        for artist in track_info.get('artists', None):
            self._artists.append(Artist(artist))


    def __str__(self):
        return '%s by %s' % (self._raw['name'], self._artists[0].name())

    def __eq__(self, other):
        return isinstance(other, Track) and self._id == other._id

    # the following are getter methods to fetch relevant information.
    def album(self):
        # TODO: it might be worth caching ids to objects so we can easily
        # reference pre-existing data.
        return self._album

    def artists(self):
        # TODO: it might be worth caching ids to objects so we can easily
        # reference pre-existing data.
        return self._artists

    def available_markets(self):
        return self._raw['available_markets']

    def name(self):
        return self._raw['name']

    def popularity(self):
        return self._raw['popularity']

    def track_number(self):
        return self._raw['track_number']

    # TODO: for debugging implementation purposes only, user should not call.
    def _asdict(self):
        return deepcopy(self._raw)

    # These are the API wrapper calls that track objects should be concerned
    # with.
    def audio_features(self):
        if 'id' not in self._raw:
            return None
        track_id = self._raw.get['id']
        request = AUDIO_FEATURES % (track_id)
        # TODO: send the actual request
        return

    def audio_analysis(self):
        if 'id' not in self._raw:
            return None
        track_id = self._raw.get['id']
        request = AUDIO_ANALYSIS % (track_id)
        # TODO: send the actual request
        return


# TODO: remove these after integrating.
# TODO: feels like TypeError and ValueError used interchangeably
# TODO: have to implement equality methods
# TODO: market as input?
# TODO: what to do about partial success?


class User:
    ''' Define behaviors related to a user, such as reading / modifying the
        library and following artists.

    Getting an instance of User should be done using spotifython.get_users()

    Exceptions:
        TypeError:  if incorrectly typed parameters are given.
        ValueError: if parameters with illegal values are given.
    '''


    @typechecked
    def __init__(self,
                 sp_obj: Spotifython,
                 user_info: Dict=None
    ):
        self._sp_obj = sp_obj
        self._raw = user_info
        self._player = Player(self._sp_obj, self)


    def __str__(self) -> str:
        uid = self._raw.get('id', None)
        # TODO:
        if uid is None:
            return super().__str__()
        return 'User <%s>' % uid


    def _paginate_get(self,
                      limit: int,
                      return_class: Any,
                      endpoint: str,
                      uri_params: Dict = None,
                      body: Dict = None
    ) -> List[Any]:
        ''' Helper function to make many requests to Spotify

        Keyword arguments:
            limit: the maximum number of items to return
            return_type: the class to construct for the list contents
            endpoint: the endpoint to call.
                Must accept 'limit' and 'offset' in uri_params
                Return json must contain key 'items'
            uri_params: the uri parameters for the request
            body: the body of the call

        Return:
            a list of objects of type return_class
        '''
        # Execute requests
        results = []
        offset = 0
        uri_params['limit'] = Spotifython.SPOTIFY_PAGE_SIZE

        # Loop until we get 'limit' many items or run out
        round = lambda num, multiple: math.ceil(num / multiple) * multiple

        num_to_request = round(limit, Spotifython.SPOTIFY_PAGE_SIZE)
        while offset < num_to_request:

            uri_params['offset'] = offset

            response_json, status_code = self._sp_obj._request(
                request_type = Spotifython.REQUEST_GET,
                endpoint     = endpoint,
                body         = body,
                uri_params   = uri_params
            )

            if status_code != 200:
                raise Exception('Oh no TODO!')

            # No more results to grab from spotify
            if len(response_json['items']) == 0:
                break

            for elem in response_json['items']:
                results.append(return_class(self._sp_obj, elem))

            offset += Spotifython.SPOTIFY_PAGE_SIZE

        return results[:limit]


    # TODO: partial failure?
    def _batch_get(self,
                   elements: List[Any],
                   endpoint: str,
                   uri_params: Dict={}
    ) -> List[Tuple[Any, bool]]:
        ''' Helper to break a large request into many smaller requests so that
            Spotify doesn't complain.

        Keyword arguments:
            elements: the list of things to be sent to Spotify
            endpoint: the Spotify endpoint to send a GET request
            uri_params: any uri params besides 'id' to be sent

        Returns:
            A list of tuples, where each tuple contains an object and the
            boolean value Spotify returned for that object.
        '''
        def create_batches(elems, chunk_size = Spotifython.SPOTIFY_PAGE_SIZE):
            ''' Helper function to break elems into batches
            E.g.
                elems = [1, 2, 3, 4, 5, 6, 7]
                _batch(elems, 2)
                >>> [[1,2], [3,4], [5,6], [7]]
            '''
            results = []
            for i in range(0, len(elems), chunk_size):
                if i >= len(elems):
                    results += [elems[i:]]
                else:
                    results += [elems[i:i + chunk_size]]

            return results

        # Break into manageable batches for Spotify
        batches = create_batches(elements, Spotifython.SPOTIFY_PAGE_SIZE)
        results = []
        for batch in batches:
            uri_params['ids'] = [elem.spotify_id() for elem in batch]

            response_json, status_code = self._sp_obj._request(
                request_type = Spotifython.REQUEST_GET,
                endpoint     = endpoint,
                body         = None,
                uri_params   = uri_params
            )

            if status_code != 200:
                raise Exception('Oh no TODO!')

            results += list(zip(batch, response_json))

        return results


    def _update_internal(self,
                         new_vals: Dict
    ) -> None:
        ''' Used internally to keep cached data up to date

        Keyword arguments:
            new_vals: a dictionary with fields that should be added to or
                updated in the internal cache. Any values in the dictionary will
                become the new value for that key.
        '''
        # {**A, **B} returns (A - B) U B
        self._raw = {**self._raw, **new_vals}
        pass


    def spotify_id(self) -> str:
        ''' Get the id of this user

        Return:
            The same id that this user was created with
        '''
        result = self._raw.get('id', None)
        if result is None:
            raise Exception('Uh oh! TODO!')

        return result


    def player(self) -> Player:
        ''' Get the player object for this user

        This is how client code should access a player. For example:
            u = Spotifython.get_user(user_id)
            u.player().pause()

        Return:
            A Player object.
        '''
        return self._player


    # TODO: can this return more than 50?
    @typechecked
    def top(self,
            top_type: str,
            limit: int,
            time_range: str=Spotifython.MEDIUM
    ) -> Union[List[Artist], List[Track]]:
        ''' Get the top artists or tracks for the user over a time range.

        Keyword arguments:
            top_type: only get items of this type. One of:
                Spotifython.ARTIST
                Spotifython.TRACK
            limit: max number of items to return. Must be positive.
            time_range: (optional) only get items for this time range. One of:
                Spotifython.LONG (several years)
                Spotifython.MEDIUM (about 6 months)
                Spotifython.SHORT (about 4 weeks)

        Return:
            A list of artists or a list of tracks, depending on top_type. Could
            be empty.

        Auth token requirements:
            user-top-read

        Calls endpoints:
            GET     /v1/me/top/{type}

        Note: Spotify defines "top items" using internal metrics.
        '''
        # Validate arguments
        if top_type not in [Spotifython.ARTIST, Spotifython.TRACK]:
            raise TypeError(top_type)
        if time_range not in [Spotifython.LONG, Spotifython.MEDIUM, Spotifython.SHORT]:
            raise TypeError(time_range)
        if limit <= 0:
            raise ValueError(limit)

        # Parse arguments
        time_ranges = {
            Spotifython.LONG: 'long_term',
            Spotifython.MEDIUM: 'medium_term',
            Spotifython.SHORT: 'short_term',
        }

        uri_params = {'time_range': time_ranges[time_range]}
        endpoint_type = 'artists' if top_type == Spotifython.ARTIST else 'tracks'
        return_class = Artist if top_type == Spotifython.ARTIST else Track

        # Execute requests
        return self._paginate_get(
                        limit = limit,
                        return_class = return_class,
                        endpoint = Endpoint.USER_TOP % endpoint_type,
                        uri_params = uri_params,
                        body = None)


    @typechecked
    def recently_played(self,
                        limit: int=50
    ) -> List[Track]:
        ''' Get the user's recently played tracks

        Keyword arguments:
            limit: (optional) max number of items to return. Must be between
                1 and 50, inclusive.

        Return:
            Success: a list of tracks. Could be empty.
            Failure: None

        Auth token requirements:
            user-read-recently-played

        Calls endpoints:
            GET     /v1/me/player/recently-played

        Note: the 'before' and 'after' functionalities are not supported.
        Note: does not return the time the tracks were played
        Note: a track must be played for >30s to be included in the history.
              Tracks played while in a 'private session' not recorded.
        '''
        # Validate arguments
        if limit <= 0 or limit > 50:
            raise ValueError(limit)

        # Execute requests
        response_json, status_code = self._sp_obj._request(
            request_type = Spotifython.REQUEST_GET,
            endpoint     = Endpoint.USER_RECENTLY_PLAYED,
            body         = None,
            uri_params   = {'limit': limit}
        )

        if status_code != 200:
            raise Exception('Oh no TODO!')

        results = []
        for elem in response_json['items']:
            results.append(Track(self._sp_obj, elem))

        return results


    @typechecked
    def get_playlists(self,
                      limit: int=None
    ) -> List[Playlist]:
        ''' Get all playlists that this user has in their library

        Keyword arguments:
            limit: (optional) the max number of items to return. If None, will
                return all. Must be between 1 and 100000 inclusive

        Return:
            Success: a list of playlists. Could be empty.
            Failure: None

        Note: this includes both playlists owned by this user and playlists
            that this user follows but are owned by others.

        Auth token requirements:
            playlist-read-private
            playlist-read-collaborative

        Calls endpoints:
            GET     /v1/users/{user_id}/playlists

        To get only playlists this user follows, use get_following(Spotifython.PLAYLISTS)
        '''
        # Validate inputs
        if limit is None:
            limit = Spotifython.SPOTIFY_MAX_PLAYLISTS

        if limit <= 0 or limit > Spotifython.SPOTIFY_MAX_PLAYLISTS:
            raise ValueError(limit)

        return self._paginate_get(
                        limit = limit,
                        return_class = Playlist,
                        endpoint = Endpoint.USER_GET_PLAYLISTS
                                   % self.spotify_id(),
                        uri_params = {},
                        body = None)


    @typechecked
    def create_playlist(self,
                        name: str,
                        visibility: str=Spotifython.PUBLIC,
                        description: str=None
    ) -> Playlist:
        ''' Create a new playlist owned by the current user

        Keyword arguments:
            name: The name for the new playlist. Does not need to be unique;
                a user may have several playlists with the same name.
            visibility: (optional) describes how other users can interact with
                this playlist. One of:
                    Spotifython.PUBLIC: publicly viewable, not collaborative
                    Spotifython.PRIVATE: not publicly viewable, not collaborative
                    Spotifython.PRIVATE_COLLAB: not publicly viewable, collaborative
            description: (optional) viewable description of the playlist.

        Return:
            The newly created Playlist object. Note that this modifies the
            user's library.

        Auth token requirements:
            playlist-modify-public
            playlist-modify-private

        Calls endpoints:
            POST    /v1/users/{user_id}/playlists
        '''
        # Validate inputs
        if visibility not in [Spotifython.PUBLIC, Spotifython.PRIVATE, Spotifython.PRIVATE_COLLAB]:
            raise TypeError(visibility)

        # Make the request
        body = {
            'name': name,
        }

        response_json, status_code = self._sp_obj._request(
            request_type = Spotifython.REQUEST_POST,
            endpoint     = Endpoint.USER_CREATE_PLAYLIST
                           % self.spotify_id(),
            body         = body,
            uri_params   = None
        )

        if status_code != 201:
            raise Exception('Oh no TODO!')

        return Playlist(self._sp_obj, response_json)


    @typechecked
    def is_following(self,
                     other: Union[Artist, User, Playlist,
                                  List[Union[Artist, User, Playlist]]]
    ) -> List[Tuple[Union[Artist, User, Playlist], bool]]:
        ''' Check if the current user is following something

        Keyword arguments:
            other: check if current user is following 'other'. Other must be
                either a single object or a list of objects.
                If other is a list, it can conatin multiple types.

                Can only check for Artist, User, and Playlist.

        Auth token requirements:
            user-follow-read
            playlist-read-private
            playlist-read-collaborative

        Calls endpoints:
            GET     /v1/me/following/contains
            GET     /v1/users/{user_id}/playlists

        Return:
            List of tuples. Each tuple has an input object and whether the user
            follows the object.
        '''
        # Validate and sort input
        if not isinstance(other, List):
            other = [other]

        artists = list(filter(lambda elem: isinstance(elem, Artist), other))
        users = list(filter(lambda elem: isinstance(elem, User), other))
        playlists = list(filter(lambda elem: isinstance(elem, Playlist), other))

        endpoint = Endpoint.USER_FOLLOWING_CONTAINS
        results = self._batch_get(artists, endpoint, {'type': 'artist'})
        results += self._batch_get(users, endpoint, {'type': 'user'})

        # For each playlist in other, check if in the User's followed playlists
        followed_playlists = self.get_following(Spotifython.PLAYLIST)
        results += list(map(lambda p: (p, p in followed_playlists), playlists))

        return results


    @typechecked
    def get_following(self,
                      follow_type: str,
                      limit: int=None
    ) -> Union[List[Artist], List[Playlist]]:
        ''' Get all follow_type objects the current user is following

        Keyword arguments:
            follow_type: one of Spotifython.ARTIST or Spotifython.PLAYLIST
            limit: (optional) the max number of items to return. If None, will
                return all. Must be between 1 and 100000 inclusive.

        Return:
            Success: List of follow_type objects. Could be empty.
            Failure: None

        Auth token requirements:
            user-follow-read
            playlist-read-private
            playlist-read-collaborative

        Calls endpoints:
            GET     /v1/me/following
            GET     /v1/users/{user_id}/playlists

        Exceptions:
            ValueError: if Spotifython.USER is passed in. The Spotify web api does not
                currently allow you to access this information.
                For more info: https://github.com/spotify/web-api/issues/4
        '''
        # Validate inputs
        if follow_type not in [Spotifython.ARTIST, Spotifython.PLAYLIST]:
            raise TypeError(follow_type)
        if limit is None:
            limit = Spotifython.SPOTIFY_MAX_LIB_SIZE
        if limit <= 0 or limit > Spotifython.SPOTIFY_MAX_LIB_SIZE:
            raise ValueError(limit)

        if follow_type == Spotifython.PLAYLIST:
            my_playlists = self.get_playlists()
            my_id = self.spotify_id()
            results = []
            for playlist in my_playlists:
                # TODO: shouldn't access _raw
                if playlist._raw['owner']['id'] != my_id:
                    results.append(playlist)

            return results[:limit]

        # assert(follow_type == Spotifython.ARTIST)
        uri_params = {
            'type': 'artist',
            'limit': Spotifython.SPOTIFY_PAGE_SIZE
        }
        results = []

        # Loop until we get 'limit' many items or run out
        # Can't use _paginate because the artist endpoint does it differently...
        while len(results) < limit:

            # Paginate
            if len(results) != 0:
                # TODO: shouldn't access _raw
                uri_params['after'] = results[-1]._raw['id']

            response_json, status_code = self._sp_obj._request(
                request_type = Spotifython.REQUEST_GET,
                endpoint     = Endpoint.USER_GET_ARTISTS,
                body         = None,
                uri_params   = uri_params
            )

            if status_code != 200:
                raise Exception('Oh no TODO!')

            # No more results to grab from spotify
            if len(response_json['artists']['items']) == 0:
                break

            for elem in response_json['artists']['items']:
                results.append(Artist(self._sp_obj, elem))

        return results[:limit]


    @typechecked
    def follow(self,
               other: Union[Artist, User, Playlist,
                            List[Union[Artist, User, Playlist]]]
    ) -> None:
        ''' Follow one or more things

        Keyword arguments:
            other: the object(s) to follow. Other must be either a single object
                or a list of objects.
                If other is a list, it can conatin multiple types.

                Can only follow Artist, User, and Playlist.

        Note: if user is already following other, will do nothing and return
            a success code in response.status()

        Return:
            None

        Auth token requirements:
            user-follow-modify
            playlist-modify-public
            playlist-modify-private

        Endpoints called:
            PUT     /v1/me/following
            PUT     /v1/playlists/{playlist_id}/followers
        '''
        # playlist 200 success
        # user/artist 204 success
        # note: calls are completely different :(
        pass


    @typechecked
    def unfollow(self,
                 other: Union[Artist, User, Playlist,
                              List[Union[Artist, User, Playlist]]]
    ) -> None:
        ''' Unfollow one or more things

        Keyword arguments:
            other: the object(s) to unfollow. Other must be either a single
                object or a list of objects.
                If other is a list, it can conatin multiple types.

                Can only unfollow Artist, User, and Playlist.

        Note: if user is already not following other, will do nothing and return
            a success code in response.status()

        Return:
            None

        Auth token requirements:
            user-follow-modify
            playlist-modify-public
            playlist-modify-private

        Endpoints called:
            DELETE  /v1/me/following
            DELETE  /v1/playlists/{playlist_id}/followers
        '''
        # playlist 200 success
        # user/artist 204 success
        # note: calls are completely different :(
        pass


    @typechecked
    def has_saved(self,
                  other: Union[Track, Album,
                               List[Union[Track, Album]]]
    ) -> List[Tuple[Union[Track, Album], bool]]:
        ''' Check if the user has one or more things saved to their library

        Keyword arguments:
            other: check if current user has 'other' saved to the library.
                Other must be either a single object or a list of objects.
                If other is a list, it can conatin multiple types.

                Can only check for Track and Album.

        Return:
            Success: List of tuples. Each tuple has an input object and whether
                     the user has that object saved.
            Failure: None

        Auth token requirements:
            user-library-read

        Calls endpoints:
            GET     /v1/me/albums/contains
            GET     /v1/me/tracks/contains
        '''
        # Sort input
        if not isinstance(other, List):
            other = [other]

        tracks = list(filter(lambda elem: isinstance(elem, Track), other))
        albums = list(filter(lambda elem: isinstance(elem, Album), other))

        endpoint = Endpoint.USER_HAS_SAVED
        results = self._batch_get(tracks, endpoint % 'tracks')
        results += self._batch_get(albums, endpoint % 'albums')

        return results


    #TODO: input arg order / labeling of required vs. optional?
    @typechecked
    def get_saved(self,
                  saved_type: str,
                  limit: int=None,
                  market: str=Spotifython.TOKEN_REGION
    ) -> Union[List[Album], List[Track]]:
        ''' Get all saved_type objects the user has saved to their library

        Keyword arguments:
            saved_type: one of Spotifython.ALBUM or Spotifython.TRACK
            limit: (optional) the max number of items to return. If None, will
                return all. Must be positive.
            market: (required) a 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                if Spotifython.TOKEN_REGION (default) is given, will use appropriate
                country code for user based on their auth token and location.

        Return:
            List of saved_type objects. Could be empty.

        Auth token requirements:
            user-library-read

        Calls endpoints:
            GET     /v1/me/albums
            GET     /v1/me/tracks

    ) -> List[Any]:
        '''
        # Validate inputs
        if saved_type not in [Spotifython.ALBUM, Spotifython.TRACK]:
            raise TypeError(saved_type)
        if limit is None:
            limit = Spotifython.SPOTIFY_MAX_LIB_SIZE
        if limit <= 0 or limit > Spotifython.SPOTIFY_MAX_LIB_SIZE:
            raise ValueError(limit)

        # TODO: should I validate the market?

        endpoint_type = 'albums' if saved_type == Spotifython.ALBUM else 'tracks'
        return_class = Album if saved_type == Spotifython.ALBUM else Track
        uri_params = {'market': market}

        return self._paginate_get(
                        limit = limit,
                        return_class = return_class,
                        endpoint = Endpoint.USER_GET_SAVED % endpoint_type,
                        uri_params = uri_params,
                        body = None)


    @typechecked
    def save(self,
             other: Union[Track, Album,
                          List[Union[Track, Album]]]
    ) -> None:
        ''' Save one or more things to the user's library

        Keyword arguments:
            other: the object(s) to save. Other must be either a single object
                or a list of objects.
                If other is a list, it can conatin multiple types.

                Can only save Track or Album.

        Note: if user already has other saved, will do nothing and return
            a success code in response.status()

        Return:
            None

        Auth token requirements:
            user-library-modify

        Endpoints called:
            PUT     /v1/me/albums
            PUT     /v1/me/tracks
        '''
        # Note: ids can go in body or uri
        # 201 on success
        pass


    @typechecked
    def remove(self,
               other: Union[Track, Album,
                            List[Union[Track, Album]]]
    ) -> None:
        ''' Remove one or more things from the user's library

        Keyword arguments:
            other: the object(s) to remove. Other must be either a single object
                or a list of objects.
                If other is a list, it can conatin multiple types.

                Can only remove Track or Album.

        Note: if user already does not have other saved, will do nothing and
            return a success code in response.status()

        Return:
            None

        Auth token requirements:
            user-library-modify

        Endpoints called:
            DELETE  /v1/me/albums
            DELETE  /v1/me/tracks
        '''
        # Note: ids can go in body or uri
        # 200 on success
        pass
