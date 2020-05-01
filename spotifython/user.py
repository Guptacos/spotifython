from typing import Union, List
from response importt
from response import *
from player import Player
from track import Track
from album import Album
from artist import Artist
from playlist import Playlist

# TODO: exceptions for each param
# TODO: auth required for each param
# Review return types and params, along with restrictions?
# Standardize the get and set methods?
# Add python : type syntax to inputs and outputs

# TODO: one of these shouldn't be here
# Note: should we have getFollowing for playlists, or just do getPlaylists?
class User():

    # TODO: What things should pollute the global namespace?
    # TODO: What state should be stored / cached? Definitely ID

    # TODO: param names
    def __init__(self, sp_obj, user_id, known_vals=None):
        #TODO: self.player init?
        pass
        
    # TODO: what should the string represent? <User __userName__, Id __userId__>
    def __str__(self):
        pass

    # TODO: how is this different than __str__?
    def __repr__(self):
        pass

    #TODO: func name, param name
    def _update_internal(self, known_vals):
        pass

    def player(self):
        return self._player

    # TODO: limit and offset?
    def top(self
            top_type,
            time_range=sp.MEDIUM):
        ''' Get the top artists or tracks for the user over a time range.
            Note that Spotify defines "top" using internal metrics.

        Keyword arguments:
        top_type: one of sp.ARTIST or sp.TRACK.
        time_range: one of:
            sp.LONG (several years)
            sp.MEDIUM (about 6 months)
            sp.SHORT (about 4 weeks)
        '''
        # GET /v1/me/top/{type}
        pass

    def recently_played(self, limit=50):
        ''' Get the user's recently played tracks

        Keyword arguments:
            limit: max number of items to return. Can't be more than 50.

        note: the 'before' and 'after' functionalities are not supported.
        '''
        # GET /v1/me/player/recently-played
        pass

    def get_playlists(self):
        ''' Get all playlists that this user has in their library

        Note that this includes both playlists owned by this user, and playlists
        that this user follows but are owned by others.

        To get only playlists this user follows, use get_following(sp.PLAYLISTS)
        '''
        # GET /v1/users/{user_id}/playlists
        pass

    # @return TODO:
    # @exceptions TODO: should I throw exception for collab=public=True??
    # TODO: should name be new_playlist?
    def create_playlist(self,
                        name: str
                        public: bool=True
                        collaborative: bool=False
                        description: str=""):
        ''' Create a new playlist owned by the current user

        Keyword arguments:
        name: The name for the new playlist. Does not need to be unique;
            a user may have several playlists with the same name.
        public: whether the playlist should be publicly viewable.
        collaborative: whether the playlist should be collaborative. Note
            that if collaborative is True, public must be False.
        description: viewable description of the playlist.

        Auth token requirements:
        auth token used needs the following authorizations:
            playlist-modify-private for public=False
            playlist-modify-public for public=True
            both of the above for collaborative=True
        '''
        # POST /v1/users/{user_id}/playlists
        pass

    # @return: TODO: if batch, then what? dict? list of tuples?
    # TODO: What types are allowed for batches? Any iterable or just a list?
    # TODO: Batch size limit?
    # TODO: object type instead of 'object'
    def is_following(self,
                     other: Union[object, List[object]]):
        # GET /v1/me/following/contains
        # GET /v1/playlists/{playlist_id}/followers/contains
        ''' Check if the current user is following something

        Keyword arguments:
        other: check if current user is following 'other'. Object must be an
            instance of sp.Artist, sp.User, or sp.Playlist. other must be either
            a single instance of object, or a list of same-type objects.

        Return:
            True if self follows other, else False
        '''
        pass

    # TODO: Batch size limit?
    # TODO: Pagination?
    # TODO: fo follow_type type???
    def get_following(self,
                      follow_type):
        ''' Get all follow_type objects the current user is following

        Keyword arguments:
        follow_type: one of sp.ARTIST or sp.PLAYLIST

        return: list of follow_type objects.

        @note: if sp.USER is passed in, will throw an exception. This is because
              the Spotify web api does not currently allow you to access this
              information.
              See https://github.com/spotify/web-api/issues/4
        '''
        # GET /v1/me/following
        # get user playlists / parse for diff owner to get following playlists
        pass

    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def follow(self,
               other: Union[object, List[object]]):
        ''' Follow one or more things

        Keyword arguments:
        other: the object(s) to follow
        '''
        # PUT /v1/me/following
        # PUT /v1/playlists/{playlist_id}/followers
        pass

    # @param unfollowType: the type of object you are trying to unfollow.
    # @param unfollowId: the id to unfollow
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    # TODO: what if already not following the thing?
    def unfollow(self,
                 other: Union[object, List[object]]):
        ''' Unfollow one or more things

        Keyword arguments:
        other: the object(s) to unfollow
        '''
        # DELETE /v1/me/following
        # DELETE /v1/playlists/{playlist_id}/followers
        pass

    # @return: TODO: dict? list of tuples?
    # TODO: What types are allowed for batches? Any iterable or just a list?
    # TODO: Batch size limit?
    def has_saved(self,
                  other: Union[object, List[object]])):
        ''' Check if the user has one or more things saved to their library

        Keyword arguments:
        other: check if the current user has 'other' saved to the library.
            Object must be an instance of sp.Album or sp.Track.
            other must be either a single instance of object, or a list of
            same-type objects.
        '''
        # GET /v1/me/albums/contains
        # GET /v1/me/tracks/contains
        pass

    # @param savedType: get all savedType objects saved by the user. Must be
    #       sp.ALBUM or sp.TRACK.
    # @return: list of saveType objects
    # TODO: Batch size limit?
    # TODO: Pagination?
    # TODO: can you use both save types?
    def get_saved(self,
                  saved_type):
        ''' Get all saved_type objects the user has saved to their library

        Keyword arguments:
        saved_type: one of sp.ALBUM or sp.TRACK

        return: list of saved_type objects.
        '''
        # GET /v1/me/albums
        # GET /v1/me/tracks
        pass

    # @param saveType: the type of object you are trying to save.
    # @param saveId: the id to save.
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def save(self,
             other: Union[object, List[object]]):
        ''' Save one or more things to the user's library

        Keyword arguments:
        other: the object(s) to save.
        '''
        # PUT /v1/me/albums
        # PUT /v1/me/tracks
        pass

    # @param removeType: the type of object you are trying to remove.
    # @param removeId: the id to remove.
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def remove(self,
               other: Union[object, List[object]]):
        ''' Remove one or more things from the user's library

        Keyword arguments:
        other: the object(s) to remove.
        '''
        # DELETE /v1/me/albums
        # DELETE /v1/me/tracks
        pass
