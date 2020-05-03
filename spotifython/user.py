from album import Album
from artist import Artist
from player import Player
from playlist import Playlist
from spotifython import Spotifython
from track import Track

from response import Response
from typing import Union, List, Dict

# TODO: auth required for each param
# TODO: what to do about partial success?
class User():
    ''' Define behaviors related to a user, such as reading / modifying the
        library and following artists.

    Getting an instance of User should be done using spotifython.get_users()

    Exceptions:
        TypeError:  if incorrectly typed parameters are given.
        ValueError: if parameters with illegal values are given.
    '''


    def __init__(self,
                 sp_obj: Spotifython,
                 user_id: str,
                 known_vals: Dict=None
    ) -> User:
        # note to self: init self.player
        pass

        
    # Format should be 'User <%s>' % user_id
    def __str__(self) -> str:
        pass


    def _update_internal(self,
                         new_vals: Dict
    ) -> None:
        ''' Used internally to keep cached data up to date

        Keyword arguments:
            new_vals: a dictionary with fields that should be added to or
                updated in the internal cache. Any values in the dictionary will
                become the new value for that key.

        Return:
            None
        '''
        pass


    def player(self) -> Player:
        ''' Get the player object for this user

        This is how client code should access a player. For example:
            u = sp.get_user(user_id)
            u.player().pause()

        Return:
            A Player object.
        '''
        pass


    def top(self,
            top_type: str,
            limit: int,
            time_range: str=sp.MEDIUM
    ) -> Response: # Union[List[Artist], List[Track]]
        ''' Get the top artists or tracks for the user over a time range.

        Keyword arguments:
            top_type: only get items of this type. One of:
                sp.ARTIST
                sp.TRACK
            limit: max number of items to return.
            time_range: (optional) only get items for this time range. One of:
                sp.LONG (several years)
                sp.MEDIUM (about 6 months)
                sp.SHORT (about 4 weeks)

        response.contents():
            Success: list of artists or a list of tracks, depending on top_type.
                Could be empty.
            Failure: None

        Note: Spotify defines "top items" using internal metrics.
        '''
        # GET /v1/me/top/{type}
        pass


    def recently_played(self,
                        limit: int=50
    ) -> Response: # List[Track]
        ''' Get the user's recently played tracks

        Keyword arguments:
            limit: (optional) max number of items to return. Can't be larger
                than 50.

        response.contents():
            Success: a list of tracks. Could be empty.
            Failure: None

        Exceptions:
            ValueError: raised if limit > 50

        Note: the 'before' and 'after' functionalities are not supported.
        '''
        # GET /v1/me/player/recently-played
        pass


    def get_playlists(self,
                      limit: int=None
    ) -> Response: # List[Playlist]
        ''' Get all playlists that this user has in their library

        Keyword arguments:
            limit: (optional) the max number of items to return. If None, will
                return all.

        response.contents():
            Success: a list of playlists. Could be empty.
            Failure: None

        Note: this includes both playlists owned by this user and playlists
            that this user follows but are owned by others.

        To get only playlists this user follows, use get_following(sp.PLAYLISTS)
        '''
        # GET /v1/users/{user_id}/playlists
        pass


    def create_playlist(self,
                        name: str,
                        visibility: str=sp.PUBLIC,
                        description: str=""
    ) -> Response: # None
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

        response.contents():
            None

        Exceptions:
            TypeError: raised if visibility is not one of the types described
                above.
        '''
        # POST /v1/users/{user_id}/playlists
        pass


    def is_following(self,
                     other: Union[Artist, User, Playlist,
                                  List[Union[Artist, User, Playlist]]]
    ) -> Response: # List[Tuple[Union[Artist, User, Playlist], bool]]
        ''' Check if the current user is following something

        Keyword arguments:
            other: check if current user is following 'other'. Other must be
                either a single object or a list of objects.
                If other is a list, it can conatin multiple types.

                Can only check for Artist, User, and Playlist.

        Exceptions:
            TypeError: raised if other is not one of the types described above.

        response.contents():
            Success: List of tuples. Each tuple has an input object and whether
                     the user follows the object.
            Failure: None
        '''
        # GET /v1/me/following/contains
        # GET /v1/playlists/{playlist_id}/followers/contains
        # Note for me: easier to use get_playlists and check in there
        pass


    def get_following(self,
                      follow_type: str,
                      limit: int=None
    ) -> Response: # Union[List[Artist], List[Playlist]]
        ''' Get all follow_type objects the current user is following

        Keyword arguments:
            follow_type: one of sp.ARTIST or sp.PLAYLIST
            limit: (optional) the max number of items to return. If None, will
                return all.

        response.contents():
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


    def follow(self,
               other: Union[Artist, User, Playlist,
                            List[Union[Artist, User, Playlist]]]
    ) -> Response: # None
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

        response.contents():
            None
        '''
        # PUT /v1/me/following
        # PUT /v1/playlists/{playlist_id}/followers
        pass


    def unfollow(self,
                 other: Union[Artist, User, Playlist,
                              List[Union[Artist, User, Playlist]]]
    ) -> Response: # None
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

        response.contents():
            None
        '''
        # DELETE /v1/me/following
        # DELETE /v1/playlists/{playlist_id}/followers
        pass


    def has_saved(self,
                  other: Union[Track, Album,
                               List[Union[Track, Album]]]
    ) -> Response: # List[Tuple[Union[Track, Album], bool]]
        ''' Check if the user has one or more things saved to their library

        Keyword arguments:
            other: check if current user has 'other' saved to the library.
                Other must be either a single object or a list of objects.
                If other is a list, it can conatin multiple types.

                Can only check for Track and Album.

        Exceptions:
            TypeError: raised if other is not one of the types described above.

        response.contents():
            Success: List of tuples. Each tuple has an input object and whether
                     the user has that object saved.
            Failure: None
        '''
        # GET /v1/me/albums/contains
        # GET /v1/me/tracks/contains
        pass


    def get_saved(self,
                  saved_type: str,
                  limit: int=None
    ) -> Response: # Union[List[Album], List[Track]]
        ''' Get all saved_type objects the user has saved to their library

        Keyword arguments:
            saved_type: one of sp.ALBUM or sp.TRACK
            limit: (optional) the max number of items to return. If None, will
                return all.

        response.contents():
            Success: List of saved_type objects. Could be empty.
            Failure: None
        '''
        # GET /v1/me/albums
        # GET /v1/me/tracks
        pass


    def save(self,
             other: Union[Track, Album,
                          List[Union[Track, Album]]]
    ) -> Response: # None
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

        response.contents():
            None
        '''
        # PUT /v1/me/albums
        # PUT /v1/me/tracks
        pass


    def remove(self,
               other: Union[Track, Album,
                            List[Union[Track, Album]]]
    ) -> Response: # None
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

        response.contents():
            None
        '''
        # DELETE /v1/me/albums
        # DELETE /v1/me/tracks
        pass
