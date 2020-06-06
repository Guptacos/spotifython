""" Session class

This class represents an interactive Spotify session, tied to a Spotify
API token.
"""

# Standard library imports
import math

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils

class Session:
    """ Session class

    This class represents an interactive Spotify session, tied to a Spotify
    API token.
    """

    def __init__(self, token, timeout=const.DEFAULT_REQUEST_TIMEOUT):
        """ This object should be constructed by the user to instantiate the
        session of Spotify Web API usage.

        Args:
            token: str, Spotify API authentication token
            timeout: (Optional) int, timeout value for each request made to
                Spotify's API

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
        """
        Updates the stored Spotify authentication token for this instance.

        Args:
            token: str, the new Spotify authentication token.
        """
        if not isinstance(token, str):
            raise TypeError('token should be string')

        self._token = token

    def token(self):
        """ Getter for the token provided by the client.

        Returns:
            A str containing the token.
        """
        return self._token

    def timeout(self):
        """ Getter for the timeout provided by the client.

        Returns:
            An int containing the provided timeout.
        """
        return self._timeout

    def __str__(self):
        # Guarantee that the IDs of different objects in memory are different
        # Avoids exposing the token as plaintext for no reason, since that is
        # the other possible indicator of object identity.
        return f'Session<${id(self)}>'

    def __repr__(self):
        return self.__str__()

    class SearchResult:
        """ SearchResult class

        This class represents the results of a Spotify API search call.
        """

        def __init__(self, search_result):
            """ User should never call this constructor. Internally, the search result will
            perform all necessary API calls to get the desired number of search
            results (up to search limit).

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
            """ Getter for the albums returned by the search query.

            Returns:
                A list of Album objects.
            """
            return self._albums

        def artists(self):
            """ Getter for the artists returned by the search query.

            Returns:
                A list of Artist objects.
            """
            return self._artists

        def playlists(self):
            """ Getter for the playlist returned by the search query.

            Returns:
                A list of Playlist objects.
            """
            return self._playlists

        def tracks(self):
            """ Getter for the tracks returned by the search query.

            Returns:
                A list of Track objects.
            """
            return self._tracks

    ##################################
    # API Calls
    ##################################

    # pylint: disable=too-many-arguments, too-many-locals, too-many-branches
    # TODO: unfortunately this function has to be kind of long to accomodate the
    # logic required. Refactor this in the future.
    def search(self,
               query,
               types,
               limit,
               market=const.TOKEN_REGION,
               include_external_audio=False
               ):
        """
        Searches for content with the given query.

        Args:
            query: str, search query keywords and optional field filters and
                operators.
            types: str or List[str], singular search type or a list of the types
                of results to search for.
                Valid arguments are sp.SEARCH_TYPE_ALBUM,
                sp.SEARCH_TYPE_ARTIST, sp.SEARCH_TYPE_PLAYLIST, and
                sp.SEARCH_TYPE_TRACK.
                Note: shows and episodes will be supported in a future release.
            limit: int, the maximum number of results to return.
            market: (Optional) str, An ISO 3166-1 alpha-2 country code or the
                string sp.TOKEN_REGION. If a country code is specified,
                only artists, albums, and tracks with content that is playable
                in that market is returned.
                Note:
                - Playlist results are not affected by the market parameter.
                - If market is set to sp.TOKEN_REGION, and a valid access
                token is specified in the request header, only content playable
                in the country associated with the user account, is returned.
                - If market is set to None, no market is passed to Spotify's Web
                API, and its default behavior is invoked.
            include_external_audio: (Optional) bool, If true,
                the response will include any relevant audio content that is
                hosted externally. By default external content is filtered out
                from responses.

        Returns:
            Returns a SearchResult if the request succeeded.
            On failure or partial failure, throws an HTTPError.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if query type or market is invalid.
                TODO: how to validate?
            ValueError if limit is > 2000: this is the Spotify API's
                search limit.
            HTTPError if failure or partial failure.

        Required token scopes:
            user-read-private

        Calls endpoints:
            GET   /v1/search
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
        if not isinstance(limit, int):
            raise TypeError('limit should be int')
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
        # search types in the argument for uniformity.
        type_mapping = {
            const.ALBUMS: 'album',
            const.ARTISTS: 'artist',
            const.PLAYLISTS: 'playlist',
            const.TRACKS: 'track',
            const.SHOWS: 'show',
            const.EPISODES: 'episode',
        }
        remaining_types = [type_mapping.get(s) for s in types]

        # Initialize SearchResult object
        result = {
            type_mapping[const.ALBUMS]: list(),
            type_mapping[const.ARTISTS]: list(),
            type_mapping[const.PLAYLISTS]: list(),
            type_mapping[const.TRACKS]: list(),
        }

        # Unfortunately because each type can have a different amount of return
        # values, utils.paginate_get() is not suited for this call.
        for offset in range(0, num_to_request, const.SPOTIFY_PAGE_SIZE):
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
                items = response_json[curr_type]['items']

                # Add items to accumulator
                for item in items:
                    if curr_type is type_mapping[const.ALBUMS]:
                        result.get(curr_type).append(Album(self, item))
                    elif curr_type is type_mapping[const.ARTISTS]:
                        result.get(curr_type).append(Artist(self, item))
                    elif curr_type is type_mapping[const.PLAYLISTS]:
                        result.get(curr_type).append(Playlist(self, item))
                    elif curr_type is type_mapping[const.TRACKS]:
                        result.get(curr_type).append(Track(self, item))
                    else:
                        # Should never reach here, but here for safety!
                        raise ValueError("Invalid type when building search")

            # Only make necessary search queries
            new_remaining_types = list()
            for curr_type in remaining_types:
                if response_json[curr_type]['next'] != 'null':
                    new_remaining_types.append(curr_type)
            remaining_types = new_remaining_types

        return self.SearchResult(result)

    def get_albums(self,
                   album_ids,
                   market=const.TOKEN_REGION
                   ):
        """
        Gets the albums with the given Spotify album ids.

        Args:
            album_ids: str or List[str], a string or list of strings of the
                Spotify album ids to search for.
            market: (Optional) str, an ISO 3166-1 alpha-2 country code or the
                string sp.TOKEN_REGION.
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web
                API, and its default behavior is invoked.

        Returns:
            Returns an Album or List[Album] if the request succeeded.
            On failure or partial failure, throws an HTTPError.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

        Required token scopes:
            None

        Calls endpoints:
            GET   /v1/albums

        Note: the following endpoint is not used.
            GET   /v1/albums/{id}
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
        endpoint = Endpoints.SEARCH_GET_ALBUMS
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

    def get_artists(self,
                    artist_ids
                    ):
        """
        Gets the artists with the given Spotify artists ids.

        Args:
            artist_ids: str or List[str], the Spotify artist ids to search for.

        Returns:
            Returns an Artist or List[Artists] if the request succeeded.
            On failure or partial failure, throws an HTTPError.

        Exceptions:
            TypeError for invalid types in any argument.
            HTTPError if failure or partial failure.

        Required token scopes:
            None

        Calls endpoints:
            GET   /v1/artists

        Note: the following endpoint is not used.
            GET   /v1/artists/{id}
        """

        # Type validation
        if not isinstance(artist_ids, str) and\
            not all(isinstance(x, str) for x in artist_ids):
            raise TypeError('artist_ids should be str or list of str')

        if isinstance(artist_ids, str):
            artist_ids = list(artist_ids)

        # Construct params for API call
        endpoint = Endpoints.SEARCH_GET_ALBUMS
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
                   market=const.TOKEN_REGION
                   ):
        """
        Gets the tracks with the given Spotify track ids.

        Args:
            track_ids: str or List[str], the Spotify track ids to search for.
            market: (Optional) An ISO 3166-1 alpha-2 country code or the string
                sp.TOKEN_REGION.
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web
                API, and its default behavior is invoked.

        Returns:
            Returns a Track or List[Track] if the request succeeded.
            On failure or partial failure, throws an HTTPError.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

        Required token scopes:
            None

        Calls endpoints:
            GET   /v1/tracks

        Note: the following endpoint is not used.
            GET   /v1/tracks/{id}
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
        endpoint = Endpoints.SEARCH_GET_TRACKS
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

    def get_users(self,
                  user_ids
                  ):
        """
        Gets the users with the given Spotify user ids.

        Args:
            user_ids: str or List[str], the Spotify user id to search for.

        Returns:
            Returns a User or List[User] if the request succeeded.
            On failure or partial failure, throws an HTTPError.

        Exceptions:
            TypeError for invalid types in any argument.
            HTTPError if failure or partial failure.

        Required token scopes:
            None

        Calls endpoints:
            GET	/v1/users/{user_id}
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
                endpoint=Endpoints.SEARCH_GET_USER % user_id,
                uri_params=uri_params
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            result.append(User(self, response_json))

        return result if len(result) != 1 else result[0]

    def get_current_user(self):
        """ Gets the user associated with the current Spotify API
        authentication key.

        If the user-read-email scope is authorized, the returned JSON will
        include the email address that was entered when the user created their
        Spotify account. This email address is unverified; do not assume that
        the email address belongs to the user.

        Returns:
            Returns a User if the request succeeded. On failure or partial
            failure, throws an HTTPError.

        Exceptions:
            ValueError if the Spotify API key is not valid.
            ValueError if the response is empty.
            HTTPError if failure or partial failure.

        Required token scopes:
            user-read-private
            user-read-email

        Calls endpoints:
            GET /v1/me
        """

        # Construct params for API call
        endpoint = Endpoints.SEARCH_GET_CURRENT_USER

        # Execute requests
        response_json, status_code = utils.request(
            session=self,
            request_type=const.REQUEST_GET,
            endpoint=endpoint
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        return User(self, response_json)

    def get_playlists(self,
                      playlist_ids,
                      fields=None,
                      market=const.TOKEN_REGION
                      ):
        """
        Gets the tracks with the given Spotify playlist ids.

        Args:
            playlist_ids: str or List[str], the Spotify playlist ids to
                search for.
            fields: (Optional) str, filters for the query: a comma-separated
                list of the fields to return.
                If omitted, all fields are returned. A dot separator can be used
                to specify non-reoccurring fields, while parentheses can be used
                to specify reoccurring fields within objects. Use multiple
                parentheses to drill down into nested objects.
                Fields can be excluded by prefixing them with an exclamation
                mark.
            market: (Optional) str, an ISO 3166-1 alpha-2 country code or the
                string sp.TOKEN_REGION.
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's
                Web API.

        Returns:
            Returns a Playlist or List[Playlist] if the request succeeded.
            On failure or partial failure, throws an HTTPError.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

        Required token scopes:
            None

        Calls endpoints:
            GET	/v1/playlists/{playlist_id}
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
            endpoint = Endpoints.SEARCH_GET_PLAYLIST % playlist_id

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

# pylint: disable=wrong-import-position
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.playlist import Playlist
from spotifython.track import Track
from spotifython.user import User