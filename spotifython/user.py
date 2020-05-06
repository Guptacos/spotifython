from __future__ import annotations # Allow type hinting a class within the class
from typing import Union, List, Dict
from typeguard import typechecked
from endpoint import Endpoint
import math

# TODO: remove these after integrating.
# TODO: consolidate the paging functionality
#from album import Album
#from artist import Artist
#from player import Player
#from playlist import Playlist
#from track import Track
class Album:
    def __init__(self, sp_obj, album_info):
        return None

class Artist:
    def __init__(self, sp_obj, artist_info):
        return None

class Player:
    def __init__(self, sp_obj, user):
        return None

class Playlist:
    def __init__(self, sp_obj, playlist_info):
        return None

class Track:
    def __init__(self, sp_obj, track_info):
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


    def _round(num, multiple):
        ''' Helper to round num up to the next multiple of multiple
        Used to fulfill large requests
        '''
        return math.ceil(num / multiple) * multiple

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
        uri_params = {
            'limit': sp.SPOTIFY_PAGE_SIZE,
            'time_range': time_ranges[time_range]
        }
        endpoint_type = 'artists' if top_type == sp.ARTIST else 'tracks'
        top_class = Artist if top_type == sp.ARTIST else Track

        # Execute requests
        endpoint = Endpoint.USER_TOP % endpoint_type
        results = []
        offset = 0

        # Loop until we get 'limit' many items or run out
        while offset < User._round(limit, sp.SPOTIFY_PAGE_SIZE):

            uri_params['offset'] = offset

            response_json, status_code = self._sp_obj._request(
                request_type = sp.REQUEST_GET,
                endpoint     = endpoint,
                body         = None,
                uri_params   = uri_params
            )

            if status_code != 200:
                raise Exception('Oh no TODO!')

            # No more results to grab from spotify
            if len(response_json['items']) == 0:
                break

            for elem in response_json['items']:
                results.append(top_class(self._sp_obj, elem))

            offset += sp.SPOTIFY_PAGE_SIZE

        return results[:limit]


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
        spotify_max_playlists = 100000
        if limit is None:
            limit = spotify_max_playlists

        if limit <= 0 or limit > spotify_max_playlists:
            raise ValueError(limit)

        # Execute requests
        uri_params = {'limit': sp.SPOTIFY_PAGE_SIZE}
        results = []
        offset = 0

        # Loop until we get 'limit' many items or run out
        while offset < User._round(limit, sp.SPOTIFY_PAGE_SIZE):
            uri_params['offset'] = offset

            response_json, status_code = self._sp_obj._request(
                request_type = sp.REQUEST_GET,
                endpoint     = Endpoint.USER_GET_PLAYLISTS % self.user_id(),
                body         = None,
                uri_params   = uri_params
            )

            if status_code != 200:
                raise Exception('Oh no TODO!')

            # No more results to grab from spotify
            if len(response_json['items']) == 0:
                break

            for elem in response_json['items']:
                results.append(Playlist(self._sp_obj, elem))

            offset += sp.SPOTIFY_PAGE_SIZE

        return results[:limit]


    @typechecked
    def create_playlist(self,
                        name: str,
                        visibility: str=sp.PUBLIC,
                        description: str=""
    ) -> None:
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
            None

        Exceptions:
            TypeError: raised if visibility is not one of the types described
                above.
        '''
        # POST /v1/users/{user_id}/playlists
        pass


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

        Exceptions:
            TypeError: raised if other is not one of the types described above.

        Return:
            Success: List of tuples. Each tuple has an input object and whether
                     the user follows the object.
            Failure: None
        '''
        # GET /v1/me/following/contains
        # GET /v1/playlists/{playlist_id}/followers/contains
        # Note for me: easier to use get_playlists and check in there
        pass


    @typechecked
    def get_following(self,
                      follow_type: str,
                      limit: int=None
    ) -> Union[List[Artist], List[Playlist]]:
        ''' Get all follow_type objects the current user is following

        Keyword arguments:
            follow_type: one of sp.ARTIST or sp.PLAYLIST
            limit: (optional) the max number of items to return. If None, will
                return all. Must be positive.

        Return:
            Success: List of follow_type objects. Could be empty.
            Failure: None

        Exceptions:
            TypeError: if sp.USER is passed in. The Spotify web api does not
                currently allow you to access this information.
                For more info: https://github.com/spotify/web-api/issues/4
        '''
        # GET /v1/me/following
        # get user playlists / parse for diff owner to get following playlists
        pass


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

        Exceptions:
            TypeError: raised if other is not one of the types described above.

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

        Exceptions:
            TypeError: raised if other is not one of the types described above.

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

        Exceptions:
            TypeError: raised if other is not one of the types described above.

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

        Exceptions:
            TypeError: raised if other is not one of the types described above.

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

        Exceptions:
            TypeError: raised if other is not one of the types described above.

        Note: if user already does not have other saved, will do nothing and
            return a success code in response.status()

        Return:
            None
        '''
        # DELETE /v1/me/albums
        # DELETE /v1/me/tracks
        pass
