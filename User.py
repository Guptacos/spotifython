
### Spotifython general object

| Method | Endpoint                                        | Description               |
|--------|-------------------------------------------------|---------------------------|
| `GET`  | `/v1/search`                                    | Search for an item        |
| `GET`  | `/v1/albums/{id}`                               | Get an Album              |
| `GET`  | `/v1/albums`                                    | Get several Albums        |
| `GET`  | `/v1/artists/{id}`                              | Get an Artist             |
| `GET`  | `/v1/artists`                                   | Get Several Artists       |
| `GET`  | `/v1/playlists/{playlist_id}`                   | Get a Playlist            |
| `GET`  | `/v1/me`                                        | Get Current User's Profile|
| `GET`  | `/v1/users/{user_id}`                           | Get a User's Profile      |
| `GET`  | `/v1/tracks/{id}`                               | Get a Track               |
| `GET`  | `/v1/tracks`                                    | Get Several Tracks        |

# TODO: exceptions for each param
# TODO: auth required for each param
# TODO: standardize function inputs and names

# TODO: one of these shouldn't be here
# GET /v1/me/playlists`              | Get a List of Current User's Playlists
# GET /v1/users/{user_id}/playlists` | Get a List of a User's Playlists
# Standardize the get methods?
class User():

    # TODO: What things should pollute the global namespace?
    # TODO: What state should be stored / cached? Definitely ID

    # TODO: should params be past in to optionally fill in some values? Also name
    def __init__(self, user_id, knownVals=None):
        pass
        
    # TODO: what should the string represent? <User __userName__, Id __userId__>
    def __str__(self):
        pass

    # TODO: how is this different than __str__?
    def __repr__(self):
        pass

    #TODO: func name, param name
    def _updateInternal(self, knownVals):

    # @param name: The name for the new playlist. Does not need to be unique;
    #       a user may have several playlists with the same name.
    # @param public: whether the playlist should be publicly viewable. Spotify
    #       default is currently True.
    # @param collaborative: whether the playlist should be collaborative. Note
    #       that if collaborative=True, public must=False. Spotify default is
    #       currently False.
    # @param description: viewable description of the playlist. Default empty.
    # @auth-requirements: auth token used needs the following authorizations:
    #       playlist-modify-private for public=False
    #       playlist-modify-public for public=True
    #       both of the above for collaborative=True
    # @return TODO:
    # @exceptions TODO: should I throw exception for collab=public=True??
    def createPlaylist(self, name, public=None, collaborative=None,
                       description=None):
        # POST /v1/users/{user_id}/playlists
        pass


    # @param followType: check if current user is following 'other'. Must be an
    #       instance of sp.ARTIST, sp.USER, or sp.PLAYLIST.
    # @param followId: the ID to check
    # @return: True if self follows followId, else False
    # @note: if you have multiple ids, call isFollowingBatch instead.
    def isFollowing(self, followType, followId):
        # GET /v1/me/following/contains
        # GET /v1/playlists/{playlist_id}/followers/contains
        ''' example code using this:
        myUser = sp.getUser(myUserId)
        myUser.isFollowing(sp.ARTIST, artistsId)
        myUser.isFollowing(sp.PLAYLIST, playlistId)
        myUser.isFollowing(sp.USER, otherUserId)
        '''
        pass

    # @param followType: same as isFollowing.
    # @param followIds: collection of Ids to check if the current user is
    #       following. All Ids must be for objects of followType.
    # @return: TODO: dict? list of tuples?
    # @note: use this if you have many requests instead of repeatedly calling
    #       isFollowing, as it combines queries into a single request for
    #       Spotify (faster and respects Spotify rate-limiting). 
    # TODO: What types are allowed for batches? Any iterable or just a list?
    # TODO: Batch size limit?
    def isFollowingBatch(self, followType, followIds):
        pass

    # @param followType: get all followType objects followed by the user.
    # @return: list of followType objects.
    # @note: if sp.USER is passed in, will throw an exception. This is because
    #       the Spotify web api does not currently allow you to receive this
    #       information.
    #       See https://github.com/spotify/web-api/issues/4
    # TODO: Batch size limit?
    # TODO: Pagination?
    def getFollowed(self, followType):
        # GET /v1/me/following
        # get user playlists / parse for diff owner to get following playlists
        pass

    # @param followType: the type of object you are trying to follow.
    # @param followId: the id to follow
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def follow(self, followType, followId):
        # PUT /v1/me/following
        # PUT /v1/playlists/{playlist_id}/followers
        pass

    # @param followType: the type of object you are trying to follow.
    # @param followIds: the ids to follow
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def followBatch(self, followType, followIds):
        pass

    # @param unfollowType: the type of object you are trying to unfollow.
    # @param unfollowId: the id to unfollow
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def unfollow(self, unfollowType, unfollowId):
        # DELETE /v1/me/following
        # DELETE /v1/playlists/{playlist_id}/followers
        pass

    # @param unfollowType: the type of object you are trying to unfollow.
    # @param unfollowIds: the ids to unfollow
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def unfollowBatch(self, unfollowType, unfollowIds):
        pass

    # @param saveType: the type of object you are trying to save.
    # @param saveId: the id to save.
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def save(self, saveType, saveId):
        # PUT /v1/me/albums
        # PUT /v1/me/tracks
        pass

    # @param saveType: the type of object you are trying to save.
    # @param saveIds: the ids to save.
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def saveBatch(self, saveType, saveIds):
        pass

    # @param removeType: the type of object you are trying to remove.
    # @param removeId: the id to remove.
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def remove(self, removeType, removeId):
        # DELETE /v1/me/albums
        # DELETE /v1/me/tracks
        pass

    # @param removeType: the type of object you are trying to remove.
    # @param removeIds: the ids to remove.
    # @return: TODO bool success? Return obj w/ success/fail stat? can it fail?
    def removeBatch(self, removeType, removeIds):
        pass

    # @param savedType: get all savedType objects saved by the user. Must be
    #       sp.ALBUM or sp.TRACK.
    # @return: list of saveType objects
    # TODO: Batch size limit?
    # TODO: Pagination?
    def getSaved(self, savedType):
        # GET /v1/me/albums
        # GET /v1/me/tracks
        pass

    # @param savedType: check if current user has savedId saved to their library
    #       Must be an instance of sp.ALBUM or sp.TRACK.
    # @param savedId: the ID to check
    # @return: True if self has savedId saved, else False
    # @note: if you have multiple ids, call hasSavedBatch instead.
    def hasSaved(self, savedType, savedId):
        # GET /v1/me/albums/contains
        # GET /v1/me/tracks/contains
        pass

    # @param savedType: same as hasSaved.
    # @param savedIds: collection of Ids to check if the current user has
    #       saved. All Ids must be for objects of savedType.
    # @return: TODO: dict? list of tuples?
    # @note: use this if you have many requests instead of repeatedly calling
    #       isSaved, as it combines queries into a single request for
    #       Spotify (faster and respects Spotify rate-limiting). 
    # TODO: What types are allowed for batches? Any iterable or just a list?
    # TODO: Batch size limit?
    def hasSavedBatch(self, savedType, savedIds):
        pass

    # Gets the top artists or tracks for the user over a time range. Spotify
    # defines "top" using internal metrics.
    # @param topType: one of sp.ARTIST or sp.TRACK.
    # @param timeRange: one of sp.LONG (several years)
    #                           sp.MEDIUM (about 6 months)
    #                           sp.SHORT (about 4 weeks)
    #       Current Spotify default is sp.MEDIUM.
    # TODO: limit and offset?
    def top(self, topType, timeRange=None):
        # GET /v1/me/top/{type}
        pass

    # This class is used to interact with the current user's player. This
    # includes things such as pausing / playing the current song, modifying the
    # queue, etc.
    class Player():

# GET`  | `/v1/me/player/recently-played`   | Get the Current User's Recently Played Tracks
# GET`  | `/v1/me/player/devices`           | Get a User's Available Devices
# GET`  | `/v1/me/player/currently-playing` | Get the User's Currently Playing Track
# POST` | `/v1/me/player/next`              | Skip User's Playback To Next Track
# POST` | `/v1/me/player/previous`          | Skip User's Playback To Previous Track
# POST` | `/v1/me/player/queue`             | Add an item to the end of the user's current playback queue
# PUT`  | `/v1/me/player/pause`             | Pause a User's Playback
# PUT`  | `/v1/me/player/play`              | Start/Resume a User's Playback
# PUT`  | `/v1/me/player/repeat`            | Set Repeat Mode On User's Playback
# PUT`  | `/v1/me/player/seek`              | Seek To Position In Currently Playing Track
# PUT`  | `/v1/me/player/shuffle`           | Toggle Shuffle For User's Playback
# PUT`  | `/v1/me/player`                   | Transfer a User's Playback
# GET`  | `/v1/me/player`                   | Get Information About The User's Current Playback
# PUT`  | `/v1/me/player/volume`            | Set Volume For User's Playback
