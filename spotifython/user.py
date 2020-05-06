from __future__ import annotations # Allow type hinting a class within the class
from typing import Union, List, Dict, Tuple
from typeguard import typechecked
from endpoint import Endpoint
import math

# TODO: remove these after integrating.
# TODO: consolidate the paging functionality
# TODO: feels like TypeError and ValueError used interchangeably
# TODO: have to implement equality methods
#from album import Album
#from artist import Artist
#from player import Player
#from playlist import Playlist
#from track import Track
class Album:
    def __init__(self, sp_obj, album_info):
        self._raw = album_info
        return None

class Artist:
    def __init__(self, sp_obj, artist_info):
        self._raw = artist_info
        return None
    def artist_id(self):
        return self._raw['id']

class Player:
    def __init__(self, sp_obj, user):
        return None

class Playlist:
    def __init__(self, sp_obj, playlist_info):
        self._raw = playlist_info
        return None

    def __str__(self):
        return ('%s owned by %s' %(self._raw['name'], self._raw['owner']['id']))

    def __repr__(self):
        return ('%s owned by %s' %(self._raw['name'], self._raw['owner']['id']))

    def __eq__(self, other):
        if not isinstance(other, Playlist):
            return False
        return self._raw['id'] == other._raw['id']

class Track:
    def __init__(self, sp_obj, track_info):
        self._raw = track_info
        return None


from spotifython import Spotifython
from spotifython import Spotifython as sp

# TODO: auth required for each param
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
        uri_params['limit'] = sp.SPOTIFY_PAGE_SIZE

        # Loop until we get 'limit' many items or run out
        round = lambda num, multiple: math.ceil(num / multiple) * multiple

        num_to_request = round(limit, sp.SPOTIFY_PAGE_SIZE)
        while offset < num_to_request:

            uri_params['offset'] = offset

            response_json, status_code = self._sp_obj._request(
                request_type = sp.REQUEST_GET,
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

            offset += sp.SPOTIFY_PAGE_SIZE

        return results[:limit]


    def _batch(elems, chunk_size = sp.SPOTIFY_PAGE_SIZE):
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


    def user_id(self) -> str:
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
            u = sp.get_user(user_id)
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
            time_range: str=sp.MEDIUM
    ) -> Union[List[Artist], List[Track]]:
        ''' Get the top artists or tracks for the user over a time range.

        Keyword arguments:
            top_type: only get items of this type. One of:
                sp.ARTIST
                sp.TRACK
            limit: max number of items to return. Must be positive.
            time_range: (optional) only get items for this time range. One of:
                sp.LONG (several years)
                sp.MEDIUM (about 6 months)
                sp.SHORT (about 4 weeks)

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
        if top_type not in [sp.ARTIST, sp.TRACK]:
            raise ValueError(top_type)
        if time_range not in [sp.LONG, sp.MEDIUM, sp.SHORT]:
            raise ValueError(time_range)
        if limit <= 0:
            raise ValueError(limit)

        # Parse arguments
        time_ranges = {
            sp.LONG: 'long_term',
            sp.MEDIUM: 'medium_term',
            sp.SHORT: 'short_term',
        }

        uri_params = {'time_range': time_ranges[time_range]}
        endpoint_type = 'artists' if top_type == sp.ARTIST else 'tracks'
        top_class = Artist if top_type == sp.ARTIST else Track

        # Execute requests
        results = self._paginate_get(
                        limit = limit,
                        return_class = top_class,
                        endpoint = Endpoint.USER_TOP % endpoint_type,
                        uri_params = uri_params,
                        body = None)

        return results


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
            request_type = sp.REQUEST_GET,
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

        To get only playlists this user follows, use get_following(sp.PLAYLISTS)
        '''
        # Validate inputs
        if limit is None:
            limit = sp.SPOTIFY_MAX_PLAYLISTS

        if limit <= 0 or limit > sp.SPOTIFY_MAX_PLAYLISTS:
            raise ValueError(limit)

        results = self._paginate_get(
                        limit = limit,
                        return_class = Playlist,
                        endpoint = Endpoint.USER_GET_PLAYLISTS % self.user_id(),
                        uri_params = {},
                        body = None)

        return results


    @typechecked
    def create_playlist(self,
                        name: str,
                        visibility: str=sp.PUBLIC,
                        description: str=None
    ) -> Playlist:
        ''' Create a new playlist owned by the current user

        Keyword arguments:
            name: The name for the new playlist. Does not need to be unique;
                a user may have several playlists with the same name.
            visibility: (optional) describes how other users can interact with
                this playlist. One of:
                    sp.PUBLIC: publicly viewable, not collaborative
                    sp.PRIVATE: not publicly viewable, not collaborative
                    sp.PRIVATE_COLLAB: not publicly viewable, collaborative
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
        if visibility not in [sp.PUBLIC, sp.PRIVATE, sp.PRIVATE_COLLAB]:
            raise ValueError(visibility)

        # Make the request
        body = {
            'name': name,
        }

        response_json, status_code = self._sp_obj._request(
            request_type = sp.REQUEST_POST,
            endpoint     = Endpoint.USER_CREATE_PLAYLIST % self.user_id(),
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

        artists = []
        users = []
        playlists = []
        for elem in other:
            if isinstance(elem, Artist):
                artists.append(elem)

            elif isinstance(elem, User):
                users.append(elem)

            elif isinstance(elem, Playlist):
                playlists.append(elem)

            else:
                raise TypeError(elem)

        # Break into manageable batches for Spotify
        artists = User._batch(artists, sp.SPOTIFY_PAGE_SIZE)
        users = User._batch(users, sp.SPOTIFY_PAGE_SIZE)

        # TODO: partial failure?
        def check_batches(batches, request_type):
            results = []
            for batch in batches:
                if request_type == 'artist':
                    ids = [artist.artist_id() for artist in batch]
                else:
                    ids = [user.user_id() for user in batch]

                response_json, status_code = self._sp_obj._request(
                    request_type = sp.REQUEST_GET,
                    endpoint     = Endpoint.USER_FOLLOWING_CONTAINS,
                    body         = None,
                    uri_params   = {'type': request_type, 'ids': ids}
                )

                if status_code != 200:
                    raise Exception('Oh no TODO!')

                results += list(zip(batch, response_json))

            return results

        results = check_batches(artists, 'artist')
        results += check_batches(users, 'user')

        followed_playlists = self.get_following(sp.PLAYLIST)
        results += list(map(lambda p: (p, p in followed_playlists), playlists))

        return results


    @typechecked
    def get_following(self,
                      follow_type: str,
                      limit: int=None
    ) -> Union[List[Artist], List[Playlist]]:
        ''' Get all follow_type objects the current user is following

        Keyword arguments:
            follow_type: one of sp.ARTIST or sp.PLAYLIST
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
            ValueError: if sp.USER is passed in. The Spotify web api does not
                currently allow you to access this information.
                For more info: https://github.com/spotify/web-api/issues/4
        '''
        # Validate inputs
        if follow_type not in [sp.ARTIST, sp.PLAYLIST]:
            raise TypeError(follow_type)
        if limit is None:
            limit = sp.SPOTIFY_MAX_PLAYLISTS
        if limit <= 0 or limit > sp.SPOTIFY_MAX_PLAYLISTS:
            raise ValueError(limit)

        if follow_type == sp.PLAYLIST:
            my_playlists = self.get_playlists()
            my_id = self.user_id()
            results = []
            for playlist in my_playlists:
                # TODO: shouldn't access _raw
                if playlist._raw['owner']['id'] != my_id:
                    results.append(playlist)

            return results[:limit]

        # assert(follow_type == sp.ARTIST)
        uri_params = {
            'type': 'artist',
            'limit': sp.SPOTIFY_PAGE_SIZE
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
                request_type = sp.REQUEST_GET,
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
        '''
        # PUT /v1/me/following
        # PUT /v1/playlists/{playlist_id}/followers
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
        '''
        # DELETE /v1/me/following
        # DELETE /v1/playlists/{playlist_id}/followers
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
        '''
        # GET /v1/me/albums/contains
        # GET /v1/me/tracks/contains
        pass


    @typechecked
    def get_saved(self,
                  saved_type: str,
                  limit: int=None
    ) -> Union[List[Album], List[Track]]:
        ''' Get all saved_type objects the user has saved to their library

        Keyword arguments:
            saved_type: one of sp.ALBUM or sp.TRACK
            limit: (optional) the max number of items to return. If None, will
                return all. Must be positive.

        Return:
            Success: List of saved_type objects. Could be empty.
            Failure: None
        '''
        # GET /v1/me/albums
        # GET /v1/me/tracks
        pass


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
        '''
        # PUT /v1/me/albums
        # PUT /v1/me/tracks
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
        '''
        # DELETE /v1/me/albums
        # DELETE /v1/me/tracks
        pass
