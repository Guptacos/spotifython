""" Session class

This class represents an interactive Spotify session, tied to a Spotify
API token.
"""

# Standard library imports
from typing import Union, List, Any
import math
import requests

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils

# Aliases to avoid circular dependencies
Album = Any  # album.py imports this module.
Artist = Any  # artist.py imports this module.
Playlist = Any  # playlist.py imports this module.
Track = Any  # track.py imports this module.
User = Any  # user.py imports this module.

# pylint: disable=pointless-string-statement, too-many-instance-attributes
# pylint: disable=too-many-arguments, too-many-locals, protected-access
# pylint: disable=too-many-branches, too-many-statements, too-many-function-args
# pylint: disable=wrong-import-position

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
            raise TypeError(token)
        if not isinstance(timeout, int):
            raise TypeError(timeout)

        self._token = token
        self._timeout = timeout

    def reauthenticate(self, token):
        """
        Updates the stored Spotify authentication token for this instance.

        Args:
            token: str, the new Spotify authentication token.
        """
        if not isinstance(token, str):
            raise TypeError(token)

        self._token = token

    def token(self):
        """ Getter for the token provided by the client. Returns a str.
        """
        return self._token

    def timeout(self):
        """ Getter for the timeout provided by the client. Returns an int.
        """
        return self._timeout

    def __str__(self):
        # Guarantee that the IDs of different objects in memory are different
        # Avoids exposing the token as plaintext for no reason, since that is
        # the other possible indicator of object identity.
        return f"Session(${id(self)})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # TODO: A session is the same if its token is the same? Or do we want
        # this to be done using memory addresses (id)?
        return self._token == other._token

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.token)

    class SearchResult:
        """ SearchResult class

        This class represents the results of a Spotify API search call.
        """

        def __init__(self, search_info):
            """ User should never call this constructor. As a result, they
            should never have access to the search_info structure prior to
            creating an SearchResult. Internally, the search result will
            perform all necessary API calls to get the desired number of search
            results (up to search limit).

            Args:
                search_info: dictionary, contains known values about the user
            """
            if not isinstance(search_info, dict):
                raise TypeError(search_info)

            self._raw = search_info
            self._albums_paging = self._raw.get('albums', dict())\
                .get('items', list())
            self._artists_paging = self._raw.get('artists', dict())\
                .get('items', list())
            self._playlists_paging = self._raw.get('playlists', dict())\
                .get('items', list())
            self._tracks_paging = self._raw.get('tracks', dict())\
                .get('items', list())

        # Internal: Update search results via paginated searches
        def _add(self, iterable):
            if isinstance(iterable, List[Album]):
                self._add_albums(self, iterable)
            elif isinstance(iterable, List[Artist]):
                self._add_artists(self, iterable)
            elif isinstance(iterable, List[Playlist]):
                self._add_playlists(self, iterable)
            elif isinstance(iterable, List[Track]):
                self._add_tracks(self, iterable)
            else:
                raise TypeError(iterable)

        def _add_albums(self, albums):
            """ Used to build the list of albums returned by the search query.

            Args:
                albums: List[Album], the albums to add to the search result.
            """
            if not isinstance(albums, List[Album]):
                raise TypeError(albums)

            self._albums_paging += albums

        def _add_artists(self, artists):
            """ Used to build the list of artists returned by the search query.

            Args:
                artists: List[Artist], the artists to add to the search result.
            """
            if not isinstance(artists, List[Artist]):
                raise TypeError(artists)

            self._artists_paging += artists

        def _add_playlists(self, playlists):
            """ Used to build the list of playlists returned by the
            search query.

            Args:
                playlists: List[Playlist], the playlists to add to the
                    search result.
            """
            if not isinstance(playlists, List[Playlist]):
                raise TypeError(playlists)

            self._playlists_paging += playlists

        def _add_tracks(self, tracks):
            """ Used to build the list of tracks returned by the search query.

            Args:
                tracks: List[Track], the tracks to add to the search result.
            """
            if not isinstance(tracks, List[Track]):
                raise TypeError(tracks)

            self._tracks_paging += tracks

        # Field accessors
        def albums(self):
            """ Getter for the albums returned by the search query.
            Returns a List[Album].
            """
            return self._albums_paging.get('items', list())

        def artists(self):
            """ Getter for the artists returned by the search query.
            Returns a List[Artist].
            """
            return self._artists_paging.get('items', list())

        def playlists(self):
            """ Getter for the playlist returned by the search query.
            Returns a List[Playlist].
            """
            return self._playlists_paging.get('items', list())

        def tracks(self):
            """ Getter for the tracks returned by the search query.
            Returns a List[Track].
            """
            return self._tracks_paging.get('items', list())

    ##################################
    # API Calls
    ##################################

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
                Valid arguments are const.SEARCH_TYPE_ALBUM,
                const.SEARCH_TYPE_ARTIST, const.SEARCH_TYPE_PLAYLIST, and
                const.SEARCH_TYPE_TRACK.
                Note: shows and episodes will be supported in a future release.
            limit: int, the maximum number of results to return.
            market: (Optional) str, An ISO 3166-1 alpha-2 country code or the
                string const.TOKEN_REGION. If a country code is specified,
                only artists, albums, and tracks with content that is playable
                in that market is returned.
                Note:
                - Playlist results are not affected by the market parameter.
                - If market is set to const.TOKEN_REGION, and a valid access
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
            JSON and a corresponding status code defined in the Response class.

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
        if not isinstance(query, str):
            raise TypeError(query)
        if not isinstance(types, Union[str, List[str]]):
            raise TypeError(types)
        if not isinstance(limit, int):
            raise TypeError(limit)
        if market is not None and not isinstance(market, str):
            raise TypeError(market)
        if include_external_audio is not None and \
            not isinstance(include_external_audio, bool):
            raise TypeError(include_external_audio)

        # Encode the spaces in strings! See the following link for more details.
        # https://developer.spotify.com/documentation/web-api/reference/search/search/
        encoded_query = query.replace(' ', '+')

        # Argument validation
        types = types if isinstance(types, List[str]) else list(types)
        valid_types = [
            const.ALBUMS,
            const.ARTISTS,
            const.PLAYLISTS,
            const.TRACKS
        ]
        for search_type_filter in types:
            if search_type_filter not in valid_types:
                raise ValueError(types)
        if limit > 2000:
            raise ValueError('Spotify only supports up to 2000 search results.')

        # Construct params for API call
        endpoint = Endpoints.SEARCH
        uri_params = dict()
        uri_params['q'] = encoded_query
        if market is not None:
            uri_params['market'] = market
        if include_external_audio:
            uri_params['include_external'] = 'audio'

        # A maximum of 50 search results per search type can be returned per API
        # call to the search backend
        next_multiple = lambda num, mult: math.ceil(num / mult) * mult
        num_to_request = next_multiple(limit, const.SPOTIFY_PAGE_SIZE)

        # Initialize SearchResult object
        result = self.SearchResult(dict())

        # We want the singular search types, while our constants are plural
        # search types in the argument for uniformity.
        type_mapping = {
            const.ALBUMS: const.SEARCH_TYPE_ALBUM,
            const.ARTISTS: const.SEARCH_TYPE_ARTIST,
            const.PLAYLISTS: const.SEARCH_TYPE_PLAYLIST,
            const.TRACKS: const.SEARCH_TYPE_TRACK,
            const.SHOWS: const.SEARCH_TYPE_SHOW,
            const.EPISODES: const.SEARCH_TYPE_EPISODE,
        }
        remaining_types = [type_mapping.get(s) for s in types]

        # Unfortunately because each type can have a different amount of return
        # values, utils.paginate_get() is not suited for this call.
        for offset in range(0, num_to_request, const.SPOTIFY_PAGE_SIZE):
            uri_params['type'] = ','.join(remaining_types)
            uri_params['limit'] = limit
            uri_params['offset'] = offset

            # Execute requests
            response_json, _ = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            # Extract data per search type
            for curr_type in remaining_types:
                items = response_json[curr_type]['items']
                acc = list()

                # Add items to accumulator
                for item in items:
                    if curr_type is const.SEARCH_TYPE_ALBUM:
                        acc.append(Album(item))
                    elif curr_type is const.SEARCH_TYPE_ARTIST:
                        acc.append(Artist(item))
                    elif curr_type is const.SEARCH_TYPE_PLAYLIST:
                        acc.append(Playlist(item))
                    elif curr_type is const.SEARCH_TYPE_TRACK:
                        acc.append(Track(item))

                # Update accumulated results into search result
                result._add(acc)

            # Only make necessary search queries
            new_remaining_types = list()
            for curr_type in remaining_types:
                if response_json[curr_type]['next'] != 'null':
                    new_remaining_types.append(curr_type)
            remaining_types = new_remaining_types

        return result

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
                string const.TOKEN_REGION.
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web
                API, and its default behavior is invoked.

        Returns:
            Returns an Album or List[Album] if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

        Required token scopes:
            N/A

        Calls endpoints:
            GET   /v1/albums

        Note: the following endpoint is not used.
            GET   /v1/albums/{id}
        """

        # Type/Argument validation
        if not isinstance(album_ids, Union[str, List[str]]):
            raise TypeError(album_ids)
        if market is None:
            raise ValueError(market)
        if not isinstance(market, str):
            raise TypeError(market)

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
            response_json, _ = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            items = response_json['albums']

            for item in items:
                result.append(Album(item))

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
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            HTTPError if failure or partial failure.

        Required token scopes:
            N/A

        Calls endpoints:
            GET   /v1/artists

        Note: the following endpoint is not used.
            GET   /v1/artists/{id}
        """

        # Type validation
        if not isinstance(artist_ids, Union[str, List[str]]):
            raise TypeError(artist_ids)

        artist_ids = artist_ids if isinstance(artist_ids, List[str]) \
            else list(artist_ids)

        # Construct params for API call
        endpoint = Endpoints.SEARCH_GET_ALBUMS
        uri_params = dict()

        # A maximum of 50 artists can be returned per API call
        batches = utils.create_batches(artist_ids, 50)

        result = list()
        for batch in batches:
            uri_params['ids'] = ','.join(batch)

            # Execute requests
            response_json, _ = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            items = response_json['artists']

            for item in items:
                result.append(Artist(item))

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
                const.TOKEN_REGION.
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's Web
                API, and its default behavior is invoked.

        Returns:
            Returns a Track or List[Track] if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

        Required token scopes:
            N/A

        Calls endpoints:
            GET   /v1/tracks

        Note: the following endpoint is not used.
            GET   /v1/tracks/{id}
        """

        # Type validation
        if not isinstance(track_ids, Union[str, List[str]]):
            raise TypeError(track_ids)
        if market is not None and not isinstance(market, str):
            raise TypeError(market)

        # Argument validation
        if market is None:
            raise ValueError(market)

        track_ids = track_ids if isinstance(track_ids, List[str]) \
            else list(track_ids)

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
            response_json, _ = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            items = response_json['tracks']

            for item in items:
                result.append(Track(item))

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
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            HTTPError if failure or partial failure.

        Required token scopes:
            N/A

        Calls endpoints:
            GET	/v1/users/{user_id}
        """

        # Type validation
        if not isinstance(user_ids, Union[str, List[str]]):
            raise TypeError(user_ids)

        if isinstance(user_ids, str):
            user_ids = list(user_ids)

        # Construct params for API call
        endpoint = Endpoints.SEARCH_GET_USER
        uri_params = dict()

        # Each API call can return at most 1 user. Therefore there is no need
        # to batch this query.
        result = list()
        for user_id in user_ids:
            uri_params['ids'] = user_id

            # Execute requests
            # TODO: Partial failure - if user with user_id does not exist,
            # status_code is 404
            response_json, _ = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )
            result.append(User(response_json))

        return result if len(result) != 1 else result[0]

    def get_current_user(self):
        """ Gets the user associated with the current Spotify API
        authentication key.

        Returns:
            Returns a User if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            ValueError if the Spotify API key is not valid.
            ValueError if the response is empty.
            HTTPError if failure or partial failure.

        Required token scopes:
            user-read-private
            user-read-email

        Calls endpoints:
            GET	/v1/me
        """

        # Construct params for API call
        endpoint = Endpoints.SEARCH_GET_CURRENT_USER

        # Execute requests
        try:
            response_json, _ = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint
            )
        except requests.exceptions.HTTPError as exception:
            if exception.request.status_code == 403:
                raise ValueError('Spotify API key is not valid')
            raise exception

        # Impossible to initialize a user with no response_json
        if response_json is None:
            raise ValueError(response_json)

        return User(response_json)

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
                string const.TOKEN_REGION.
                Provide this parameter if you want to apply Track Relinking.
                If market is set to None, no market is passed to Spotify's
                Web API.

        Returns:
            Returns a Playlist or List[Playlist] if the request succeeded.
            On failure or partial failure, throws an HTTPError.
            JSON and a corresponding status code defined in the Response class.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if market type is invalid. TODO
            HTTPError if failure or partial failure.

        Required token scopes:
            N/A

        Calls endpoints:
            GET	/v1/playlists/{playlist_id}
        """

        # Note: additional_types is also a valid request param - it
        # has been deprecated and therefore is removed from the API wrapper.

        # Type/Argument validation
        if not isinstance(playlist_ids, Union[str, List[str]]):
            raise TypeError(playlist_ids)
        if fields is not None and not isinstance(fields, str):
            raise TypeError(fields)
        if market is None:
            raise ValueError(market)
        if not isinstance(market, str):
            raise TypeError(market)

        if isinstance(playlist_ids, str):
            playlist_ids = list(playlist_ids)

        # Construct params for API call
        uri_params = dict()
        if market is not None:
            uri_params['market'] = market
        if fields is not None:
            uri_params['fields'] = fields

        # Each API call can return at most 1 playlist. Therefore there is no
        # need to batch this query.
        result = list()
        for playlist_id in playlist_ids:
            endpoint = Endpoints.SEARCH_GET_PLAYLIST.format(playlist_id)

            # Execute requests
            response_json, _ = utils.request(
                session=self,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                uri_params=uri_params
            )

            result.append(Playlist(response_json))

        return result if len(result) != 1 else result[0]
