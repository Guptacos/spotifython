""" Session class. """

# Standard library imports
import math

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils

class Session:
    """ Represents an interactive Spotify session, tied to a Spotify API token.

    Use methods here to deal with authentication, searching for objects, and
    getting objects by their ids.
    """

    def __init__(self, token, timeout=const.DEFAULT_REQUEST_TIMEOUT):
        """ Create a new Spotify Session.

        This is the only constructor that should be explicitly called by the
        client. Use it to start a Session with the Spotify web API.

        Args:
            token (str): Spotify API authentication token
            timeout (int): timeout value for each request made to Spotify's API.
                Default 10. This library uses exponential backoff with a
                timeout; this parameter is the hard timeout.

        Raises:
            TypeError:  if incorrectly typed parameters are given.
            ValueError: if parameters with illegal values are given.
        """
        if not isinstance(token, str):
            raise TypeError('token should be str')
        if not isinstance(timeout, int):
            raise TypeError('timeout should be int')
        if timeout < 0:
            raise ValueError(f'timeout {timeout} is < 0')

        self._token = token
        self._timeout = timeout


    def reauthenticate(self, token):
        """ Updates the stored Spotify authentication token for this instance.

        Args:
            token (str): the new Spotify authentication token.
        """
        if not isinstance(token, str):
            raise TypeError('token should be string')

        self._token = token


    def token(self):
        """
        Returns:
            str: The token associated with this session.
        """
        return self._token


    def timeout(self):
        """
        Returns:
            int: The timeout associated with this session.
        """
        return self._timeout


    def __str__(self):
        """ Returns the Session's id.

        Note:
            This is NOT the token, but the unique Python identifier for this
            object.
        """
        # Guarantee that the IDs of different objects in memory are different
        # Avoids exposing the token as plaintext for no reason, since that is
        # the other possible indicator of object identity.
        return f'Session <${id(self)}>'


    def __repr__(self):
        """ Returns the Session's id.

        Note:
            This is NOT the token, but the unique Python identifier for this
            object.
        """
        return self.__str__()


    class SearchResult:
        """ Represents the results of a Spotify API search call.

        Do not use the constructor. To get a SearchResult, use
        :meth:`Session.search() <spotifython.session.Session.search>`
        """

        def __init__(self, search_result):
            """ Get an instance of SearchResult. Client should not use this!

            Internally, the search result will perform all necessary API calls
            to get the desired number of search results (up to search limit).

            Args:
                search_result: dict containing keys 'album', 'artist',
                    'playlist', 'track', each mapped to a list of the
                    corresponding object type. For example, the key 'artist'
                    maps to a list of Artist objects.
            """
            self._albums = search_result.get('album', list())
            self._artists = search_result.get('artist', list())
            self._playlists = search_result.get('playlist', list())
            self._tracks = search_result.get('track', list())


        # Field accessors
        def albums(self):
            """
            Returns:
                List[Album]: Any albums returned by the Spotify search. Could be
                empty.
            """
            return self._albums


        def artists(self):
            """
            Returns:
                List[Artist]: Any artists returned by the Spotify search. Could
                be empty.
            """
            return self._artists


        def playlists(self):
            """
            Returns:
                List[Playlist]: Any playlists returned by the Spotify search.
                Could be empty.
            """
            return self._playlists


        def tracks(self):
            """
            Returns:
                List[Track]: Any tracks returned by the Spotify search.  Could
                be empty.
            """
            return self._tracks

    ##################################
    # API Calls
    ##################################

    # pylint: disable=too-many-arguments, too-many-locals, too-many-branches
    # pylint: disable=too-many-statements
    # TODO: unfortunately this function has to be kind of long to accomodate the
    # logic required. Refactor this in the future.
    # TODO: 'optional field filters and operators' What are these? Provide
    #       a link and / or example.
    def search(self,
               query,
               types,
               limit,
               market=const.TOKEN_REGION,
               include_external_audio=False):
        """ Searches Spotify for content with the given query.

        Args:
            query (str): search query keywords and optional field filters and
                operators.

            types: type(s) of results to search for. One of:

                - sp.ALBUMS
                - sp.ARTISTS
                - sp.PLAYLISTS
                - sp.TRACKS
                - List: can contain multiple of the above.

            limit (int): the maximum number of results to return. If the limit
                is None, will return up to the API-supported limit of 2000
                results. Use this with caution as it will result in a very long
                chain of queries!

                Note: The limit is applied within each type, not on the total
                response. For example, if the limit value is 3 and the search
                is for both artists & albums, the response contains 3 artists
                and 3 albums.

            market (str): a :term:`market code <Market>` or sp.TOKEN_REGION,
                used for :term:`track relinking <Track Relinking>`. If None, no
                market is passed to Spotify's Web API, and its default behavior
                is invoked.

            include_external_audio (bool): If true, the response will include
                any relevant audio content that is hosted externally. By default
                external content is filtered out from responses.

        Note:
            - Shows and Episodes will be supported in a future release.
            - Playlist search results are not affected by the market parameter.
                Playlists queried from session.search() can't have
                :term:`track relinking <Track Relinking>` applied,
                while getting an individual playlist with
                session.get_playlist() can. This is a limitation of the
                Spotify API.
            - If market is not None, only content playable in the specified
              is returned.

        Returns:
            SearchResult: The results from the Spotify search.

        Raises:
            TypeError: for invalid types in any argument.
            ValueError: if query type or market is invalid. TODO: validate?
            ValueError: if limit is > 2000: this is the Spotify API's search
                limit.
            HTTPError: if failure or partial failure.

        Required token scopes:
            - user-read-private

        Calls endpoints:
            - GET   /v1/search
        """

        # Search limit is a required field due to the offset + limit being 2000,
        # which would take 40 backend API calls. Throw an error if > the limit
        # is 2000.

        # Internally, include_external='audio' is the only valid argument.

        # Type validation
        if not all(isinstance(x, str) for x in query):
            raise TypeError('query should be str')
        if not isinstance(types, str) and \
            not all(isinstance(x, str) for x in types):
            raise TypeError('types should be str or a list of str')
        if (limit is not None and not isinstance(limit, int)) or \
            (isinstance(limit, int) and limit < 1):
            raise TypeError('limit should be None or int > 0')
        if market is not None and not isinstance(market, str):
            raise TypeError('market should be None or str')
        if include_external_audio is not None and \
            not isinstance(include_external_audio, bool):
            raise TypeError('include_external_audio should be None or bool')

        # Argument validation
        if isinstance(types, str):
            types = list(types)
        valid_types = [
            const.ALBUMS,
            const.ARTISTS,
            const.PLAYLISTS,
            const.TRACKS
        ]
        for search_type_filter in types:
            if search_type_filter not in valid_types:
                raise ValueError(f'search type {search_type_filter} invalid')
        if limit is None:
            limit = 2000
        if limit > 2000:
            raise ValueError('Spotify only supports up to 2000 search results.')

        # Construct params for API call
        uri_params = dict()
        # Encode the spaces in strings! See the following link for more details.
        # https://developer.spotify.com/documentation/web-api/reference/search/search/
        uri_params['q'] = query.replace(' ', '+')
        if market is not None:
            uri_params['market'] = market
        if include_external_audio:
            uri_params['include_external'] = 'audio'

        # A maximum of 50 search results per search type can be returned per API
        # call to the search backend
        next_multiple = lambda num, mult: math.ceil(num / mult) * mult
        num_to_request = next_multiple(limit, const.SPOTIFY_PAGE_SIZE)

        # We want the singular search types, while our constants are plural
        # search types in the argument for uniformity. The pagination objects
        # use the plural types again, so a two way mapping is required.
        map_args_to_api_call = {
            const.ALBUMS: 'album',
            const.ARTISTS: 'artist',
            const.PLAYLISTS: 'playlist',
            const.TRACKS: 'track',
            const.SHOWS: 'show',
            const.EPISODES: 'episode',
        }
        map_args_to_api_result = {
            'album': const.ALBUMS,
            'artist': const.ARTISTS,
            'playlist': const.PLAYLISTS,
            'track': const.TRACKS,
            'show': const.SHOWS,
            'episode': const.EPISODES,
        }
        remaining_types = [map_args_to_api_call.get(s) for s in types]

        # Initialize SearchResult object
        result = {
            map_args_to_api_call[const.ALBUMS]: list(),
            map_args_to_api_call[const.ARTISTS]: list(),
            map_args_to_api_call[const.PLAYLISTS]: list(),
            map_args_to_api_call[const.TRACKS]: list(),
        }

        # Unfortunately because each type can have a different amount of return
        # values, utils.paginate_get() is not suited for this call.
        for offset in range(0, num_to_request, const.SPOTIFY_PAGE_SIZE):
            # This line simplifies the logic for cases where an extra request
            # would otherwise be needed to hit the empty list check in the
            # search responses.
            if len(remaining_types) == 0:
                break

            uri_params['type'] = ','.join(remaining_types)
            uri_params['limit'] = limit
            uri_params['offset'] = offset

            # Execute requests
            response_json, status_code = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=Endpoints.SEARCH,
                uri_params=uri_params
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            # Extract data per search type
            # TODO: test what happens if unnecessary types are specified for
            # the given offsets against live api
            for curr_type in remaining_types:
                api_result_type = map_args_to_api_result[curr_type]
                items = response_json[api_result_type]['items']

                # Add items to accumulator
                for item in items:
                    if curr_type is map_args_to_api_call[const.ALBUMS]:
                        result.get(curr_type).append(Album(self, item))
                    elif curr_type is map_args_to_api_call[const.ARTISTS]:
                        result.get(curr_type).append(Artist(self, item))
                    elif curr_type is map_args_to_api_call[const.PLAYLISTS]:
                        result.get(curr_type).append(Playlist(self, item))
                    elif curr_type is map_args_to_api_call[const.TRACKS]:
                        result.get(curr_type).append(Track(self, item))
                    else:
                        # Should never reach here, but here for safety!
                        raise ValueError('Invalid type when building search')

            # Only make necessary search queries
            new_remaining_types = list()
            for curr_type in remaining_types:
                api_result_type = map_args_to_api_result[curr_type]
                if response_json[api_result_type]['next'] is not None:
                    new_remaining_types.append(curr_type)
            remaining_types = new_remaining_types

        return self.SearchResult(result)


    def get_albums(self,
                   album_ids,
                   market=const.TOKEN_REGION):
        """ Gets the albums with the given Spotify ids.

        Args:
            album_ids (str, List[str]): The Spotify album id(s) to get.
            market (str): a :term:`market code <Market>` or sp.TOKEN_REGION,
                used for :term:`track relinking <Track Relinking>`. If None, no
                market is passed to Spotify's Web API, and its default behavior
                is invoked.

        Returns:
            Union[Album, List[Album]]: The requested album(s).

        Raises:
            TypeError: for invalid types in any argument.
            ValueError: if market type is invalid. TODO
            HTTPError: if failure or partial failure.

        Calls endpoints:
            - GET   /v1/albums

        Note: the following endpoint is not used.
            - GET   /v1/albums/{id}
        """

        # Type/Argument validation
        if not isinstance(album_ids, str) and\
            not all(isinstance(x, str) for x in album_ids):
            raise TypeError('album_ids should be str or list of str')
        if market is None:
            raise ValueError('market is a required argument')
        if not isinstance(market, str):
            raise TypeError('market should be str')

        if isinstance(album_ids, str):
            album_ids = list(album_ids)

        # Construct params for API call
        endpoint = Endpoints.SEARCH_ALBUMS
        uri_params = dict()
        if market is not None:
            uri_params['market'] = market

        # A maximum 20 albums can be returned per API call
        batches = utils.create_batches(album_ids, 20)

        result = list()
        for batch in batches:
            uri_params['ids'] = ','.join(batch)

            # Execute requests
            response_json, status_code = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            items = response_json['albums']
            for item in items:
                result.append(Album(self, item))

        return result if len(result) != 1 else result[0]


    def get_artists(self, artist_ids):
        """ Gets the artists with the given Spotify ids.

        Args:
            artist_ids (str, List[str): The Spotify artist id(s) to get.

        Returns:
            Union[Album, List[Album]]: The requested artist(s).

        Raises:
            TypeError: for invalid types in any argument.
            HTTPError: if failure or partial failure.

        Calls endpoints:
            - GET   /v1/artists

        Note: the following endpoint is not used.
            - GET   /v1/artists/{id}
        """

        # Type validation
        if not isinstance(artist_ids, str) and\
            not all(isinstance(x, str) for x in artist_ids):
            raise TypeError('artist_ids should be str or list of str')

        if isinstance(artist_ids, str):
            artist_ids = list(artist_ids)

        # Construct params for API call
        endpoint = Endpoints.SEARCH_ALBUMS
        uri_params = dict()

        # A maximum of 50 artists can be returned per API call
        batches = utils.create_batches(artist_ids, 50)

        result = list()
        for batch in batches:
            uri_params['ids'] = batch

            # Execute requests
            response_json, status_code = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            items = response_json['artists']
            for item in items:
                result.append(Artist(self, item))

        return result if len(result) != 1 else result[0]


    def get_tracks(self,
                   track_ids,
                   market=const.TOKEN_REGION):
        """ Gets the tracks with the given Spotify ids.

        Args:
            track_ids (str, List[str]): The Spotify track id(s) to get.
            market (str): a :term:`market code <Market>` or sp.TOKEN_REGION,
                used for :term:`track relinking <Track Relinking>`. If None, no
                market is passed to Spotify's Web API, and its default behavior
                is invoked.

        Returns:
            Union[Track, List[Track]]: The requested track(s).

        Raises:
            TypeError: for invalid types in any argument.
            ValueError: if market type is invalid. TODO
            HTTPError: if failure or partial failure.

        Calls endpoints:
            - GET   /v1/tracks

        Note: the following endpoint is not used.
            - GET   /v1/tracks/{id}
        """

        # Type validation
        if not isinstance(track_ids, str) and\
            not all(isinstance(x, str) for x in track_ids):
            raise TypeError('track_ids should be str or list of str')
        if market is not None and not isinstance(market, str):
            raise TypeError('market should be None or str')

        # Argument validation
        if isinstance(track_ids, str):
            track_ids = list(track_ids)

        # Construct params for API call
        endpoint = Endpoints.SEARCH_TRACKS
        uri_params = dict()
        if market is not None:
            uri_params['market'] = market

        # A maximum of 50 tracks can be returned per API call
        batches = utils.create_batches(track_ids, 50)

        result = list()
        for batch in batches:
            uri_params['ids'] = ','.join(batch)

            # Execute requests
            response_json, status_code = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            items = response_json['tracks']
            for item in items:
                result.append(Track(self, item))

        return result if len(result) != 1 else result[0]


    # TODO: what the heck are fields?
    def get_playlists(self,
                      playlist_ids,
                      fields=None,
                      market=const.TOKEN_REGION):
        """ Gets the playlist(s) with the given Spotify ids.

        Args:
            playlist_ids (str, List[str]): The Spotify playlist ids to get.
            fields (str): filters for the query: a comma-separated list of the
                fields to return.  If omitted, all fields are returned. A dot
                separator can be used to specify non-reoccurring fields, while
                parentheses can be used to specify reoccurring fields within
                objects. Use multiple parentheses to drill down into nested
                objects.  Fields can be excluded by prefixing them with an
                exclamation mark.
            market (str): a :term:`market code <Market>` or sp.TOKEN_REGION,
                used for :term:`track relinking <Track Relinking>`. If None, no
                market is passed to Spotify's Web API, and its default behavior
                is invoked.

        Returns:
            Union[Playlist, List[Playlist]]: The requested playlist(s)

        Raises:
            TypeError: for invalid types in any argument.
            ValueError: if market type is invalid. TODO
            HTTPError: if failure or partial failure.

        Calls endpoints:
            - GET	/v1/playlists/{playlist_id}
        """

        # Note: additional_types is also a valid request param - it
        # has been deprecated and therefore is removed from the API wrapper.

        # Type/Argument validation
        if not isinstance(playlist_ids, str) and\
            not all(isinstance(x, str) for x in playlist_ids):
            raise TypeError('playlist_ids should be str or list of str')
        if fields is not None and not isinstance(fields, str):
            raise TypeError('fields should be None or str')
        if not isinstance(market, str):
            raise TypeError('market should be str')

        if isinstance(playlist_ids, str):
            playlist_ids = list(playlist_ids)

        # Construct params for API call
        uri_params = dict()
        uri_params['market'] = market
        if fields is not None:
            uri_params['fields'] = fields

        # Each API call can return at most 1 playlist. Therefore there is no
        # need to batch this query.
        result = list()
        for playlist_id in playlist_ids:
            endpoint = Endpoints.SEARCH_PLAYLIST % playlist_id

            # Execute requests
            response_json, status_code = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            result.append(Playlist(self, response_json))

        return result if len(result) != 1 else result[0]


    def get_users(self, user_ids):
        """ Gets the users with the given Spotify ids.

        Args:
            user_ids (str, List[str]): The Spotify user id(s) to get.

        Returns:
            Union[User, List[User]]: The requested user(s).

        Raises:
            TypeError: for invalid types in any argument.
            HTTPError: if failure or partial failure.

        Calls endpoints:
            - GET	/v1/users/{user_id}
        """

        # Type validation
        if not isinstance(user_ids, str) and\
            not all(isinstance(x, str) for x in user_ids):
            raise TypeError('user_ids should be str or list of str')

        if isinstance(user_ids, str):
            user_ids = list('user_ids should be str')

        # Construct params for API call
        uri_params = dict()

        # Each API call can return at most 1 user. Therefore there is no need
        # to batch this query.
        result = list()
        for user_id in user_ids:
            # Execute requests
            # TODO: Partial failure - if user with user_id does not exist,
            # status_code is 404
            response_json, status_code = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=Endpoints.SEARCH_USER % user_id,
                uri_params=uri_params
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            result.append(User(self, response_json))

        return result if len(result) != 1 else result[0]


    def current_user(self):
        """
        Returns:
            User: The user associated with the current Spotify API token.

        Raises:
            ValueError: if the Spotify API key is not valid.
            ValueError: if the response is empty.
            HTTPError: if failure or partial failure.

        Calls endpoints:
            - GET /v1/me
        """

        # Construct params for API call
        endpoint = Endpoints.SEARCH_CURRENT_USER

        # Execute requests
        response_json, status_code = utils.request(
            session=self,
            request_type=const.REQUEST_GET,
            endpoint=endpoint
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        return User(self, response_json)


# pylint: disable=wrong-import-position
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.playlist import Playlist
from spotifython.track import Track
from spotifython.user import User
