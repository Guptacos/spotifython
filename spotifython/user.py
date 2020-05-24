""" User class

This class represents a User object, tied to a Spotify user id.

"""

# Standard library imports
from __future__ import annotations # Allow type hinting a class within the class

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils


# TODO: fix imports after integrating.
# TODO: feels like TypeError and ValueError used interchangeably
# TODO: have to implement equality methods
# TODO: market as input?
# TODO: what to do about partial success?
# TODO: return success vs failure in docstring
# TODO: default params

class User:
    """ Define behaviors related to a user, such as reading / modifying the
        library and following artists.

    Getting an instance of User should be done using spotifython.get_users()

    Raises:
        TypeError:  if incorrectly typed parameters are given.
        ValueError: if parameters with illegal values are given.
    """


    #@typechecked
    def __init__(self,
                 session,
                 info=None):
        """
        Args:
            session: a Spotifython instance
            info: a dictionary containing known values about the user
        """
        self._session = session
        self._info = info
        self._player = Player(self._session, self)


    def __str__(self):
        uid = self._info.get('id', None)
        # TODO:
        if uid is None:
            return super().__str__()
        return 'User <%s>' % uid


    def __repr__(self):
        return self.__str__()


    def _update_internal(self, new_vals):
        """ Used internally to keep cached data up to date

        Args:
            new_vals: (dict) the fields that should be added to or updated in
                the internal cache. Any values in the dictionary will become the
                new value for that key.

        Returns:
            None
        """
        # {**A, **B} returns (A - B) U B
        self._info = {**self._info, **new_vals}


    def spotify_id(self):
        """ Get the id of this user

        Returns:
            The same id that this user was created with as a string.
        """
        result = self._info.get('id', None)
        if result is None:
            raise Exception('Uh oh! TODO!')

        return result


    def player(self):
        """ Get the player object for this user

        This is how client code should access a player. For example:
            u = sp.get_user(user_id)
            u.player().pause()

        Returns:
            A Player object.
        """
        return self._player


    # TODO: can this return more than 50?
    #@typechecked
    def top(self,
            top_type,
            limit,
            time_range=const.MEDIUM):
        """ Get the top artists or tracks for the user over a time range.

        Args:
            top_type: only get items of this type. One of:
                sp.ARTISTS
                sp.TRACKS
            limit: (int) max number of items to return. Must be positive.
            time_range: (optional) only get items for this time range. One of:
                sp.LONG (several years)
                sp.MEDIUM (about 6 months)
                sp.SHORT (about 4 weeks)

        Returns:
            A list of artists or a list of tracks, depending on top_type. Could
            be empty.

        Required token scopes:
            user-top-read

        Calls endpoints:
            GET     /v1/me/top/{type}

        Note: Spotify defines "top items" using internal metrics.
        """
        # Validate arguments
        if top_type not in [const.ARTISTS, const.TRACKS]:
            raise TypeError(top_type)
        if time_range not in [const.LONG, const.MEDIUM, const.SHORT]:
            raise TypeError(time_range)
        if limit <= 0:
            raise ValueError(limit)

        # Parse arguments
        time_ranges = {
            const.LONG: 'long_term',
            const.MEDIUM: 'medium_term',
            const.SHORT: 'short_term',
        }

        uri_params = {'time_range': time_ranges[time_range]}
        endpoint_type = 'artists' if top_type == const.ARTISTS else 'tracks'
        return_class = Artist if top_type == const.ARTISTS else Track

        # Execute requests
        return utils.paginate_get(
                        self._session,
                        limit=limit,
                        return_class=return_class,
                        endpoint=Endpoints.USER_TOP % endpoint_type,
                        uri_params=uri_params,
                        body=None)


    #@typechecked
    def recently_played(self, limit=50):
        """ Get the user's recently played tracks

        Args:
            limit: (int, optional) max number of items to return. Must be
                between 1 and 50, inclusive.

        Returns:
            Success: a list of tracks. Could be empty.
            Failure: None

        Required token scopes:
            user-read-recently-played

        Calls endpoints:
            GET     /v1/me/player/recently-played

        Note: the 'before' and 'after' functionalities are not supported.
        Note: does not return the time the tracks were played
        Note: a track must be played for >30s to be included in the history.
              Tracks played while in a 'private session' not recorded.
        """
        # Validate arguments
        if limit <= 0 or limit > 50:
            raise ValueError(limit)

        # Execute requests
        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_GET,
            endpoint=Endpoints.USER_RECENTLY_PLAYED,
            body=None,
            uri_params={'limit': limit}
        )

        if status_code != 200:
            raise Exception('Oh no TODO!')

        results = []
        for elem in response_json['items']:
            results.append(Track(self._session, elem))

        return results


    #@typechecked
    # TODO: default value
    def get_playlists(self, limit=None):
        """ Get all playlists that this user has in their library

        Args:
            limit: (int, optional) the max number of items to return. If None,
                will return all. Must be between 1 and 100,000 inclusive.

        Returns:
            Success: a list of playlists. Could be empty.
            Failure: None

        Note: this includes both playlists owned by this user and playlists
            that this user follows but are owned by others.

        Required token scopes:
            playlist-read-private
            playlist-read-collaborative

        Calls endpoints:
            GET     /v1/users/{user_id}/playlists

        To get only playlists this user follows, use get_following(sp.PLAYLISTS)
        """
        # Validate inputs
        if limit is None:
            limit = const.SPOTIFY_MAX_PLAYLISTS

        if limit <= 0 or limit > const.SPOTIFY_MAX_PLAYLISTS:
            raise ValueError(limit)

        endpoint = Endpoints.USER_GET_PLAYLISTS % self.spotify_id()

        return utils.paginate_get(
                        self._session,
                        limit=limit,
                        return_class=Playlist,
                        endpoint=endpoint,
                        uri_params={},
                        body=None)


    #@typechecked
    def create_playlist(self,
                        name,
                        visibility=const.PUBLIC,
                        description=None):
        """ Create a new playlist owned by the current user

        Args:
            name: (str) The name for the new playlist. Does not need to be
                unique; a user may have several playlists with the same name.
            visibility: (optional) describes how other users can interact with
                this playlist. One of:
                    sp.PUBLIC: publicly viewable, not collaborative
                    sp.PRIVATE: not publicly viewable, not collaborative
                    sp.PRIVATE_COLLAB: not publicly viewable, collaborative
            description: (str, optional) viewable description of the playlist.

        Returns:
            The newly created Playlist object. Note that this function modifies
            the user's library.

        Required token scopes:
            playlist-modify-public
            playlist-modify-private

        Calls endpoints:
            POST    /v1/users/{user_id}/playlists
        """
        # Validate inputs
        if visibility not in [const.PUBLIC,
                              const.PRIVATE,
                              const.PRIVATE_COLLAB]:
            raise TypeError(visibility)

        body = {
            'name': name,
            'public': visibility == const.PUBLIC,
            'collaborative': visibility == const.PRIVATE_COLLAB
        }

        if description is not None:
            body['description'] = description

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_POST,
            endpoint=Endpoints.USER_CREATE_PLAYLIST % self.spotify_id(),
            body=body,
            uri_params=None
        )

        if status_code != 201:
            raise Exception('Oh no TODO!')

        return Playlist(self._session, response_json)


    #@typechecked
    def is_following(self, other):
        """ Check if the current user is following something

        Args:
            other: check if current user is following 'other'. Other must be
                one of the following:
                    Artist
                    User
                    Playlist
                    List: can contain multiple of the above types

        Required token scopes:
            user-follow-read
            playlist-read-private
            playlist-read-collaborative

        Calls endpoints:
            GET     /v1/me/following/contains
            GET     /v1/users/{user_id}/playlists

        Returns:
            List of tuples. Each tuple has an input object and whether the user
            follows the object.
        """
        # Validate input
        if not isinstance(other, list):
            other = [other]

        for elem in other:
            if type(elem) not in [Artist, User, Playlist]:
                raise TypeError(elem)

        # Split up input
        artists = utils.separate(other, Artist)
        users = utils.separate(other, User)
        playlists = utils.separate(other, Playlist)

        # Get boolean values for whether the user follows each in 'other'
        endpoint = Endpoints.USER_FOLLOWING_CONTAINS
        artist_bools = utils.batch_get(self._session,
                                       utils.map_ids(artists),
                                       endpoint,
                                       uri_params={'type': 'artist'})

        user_bools = utils.batch_get(self._session,
                                     utils.map_ids(users),
                                     endpoint,
                                     uri_params={'type': 'user'})

        # For each playlist in other, check if in the User's followed playlists
        followed_playlists = self.get_following(const.PLAYLISTS)
        playlist_bools = list(map(lambda p: p in followed_playlists, playlists))

        # Zip output with input to make tuples
        return list(zip(artists, artist_bools)) + list(zip(users, user_bools)) + list(zip(playlists, playlist_bools))


    #@typechecked
    # TODO: default parameter limit
    def get_following(self,
                      follow_type,
                      limit=None):
        """ Get all follow_type objects the current user is following

        Args:
            follow_type: one of sp.ARTISTS or sp.PLAYLISTS
            limit: (int, optional) the max number of items to return. If None,
                will return all. Must be between 1 and 100000 inclusive.

        Returns:
            Success: List of follow_type objects. Could be empty.
            Failure: None

        Required token scopes:
            user-follow-read
            playlist-read-private
            playlist-read-collaborative

        Calls endpoints:
            GET     /v1/me/following
            GET     /v1/users/{user_id}/playlists

        Calls functions:
            self.get_playlists() if follow_type == sp.PLAYLISTS

        Raises:
            ValueError: if sp.USERS is passed in. The Spotify web api does not
                currently allow you to access this information.
                For more info: https://github.com/spotify/web-api/issues/4
        """
        # Validate inputs
        if follow_type not in [const.ARTISTS, const.PLAYLISTS]:
            raise TypeError(follow_type)
        if limit is None:
            limit = const.SPOTIFY_MAX_LIB_SIZE
        if limit <= 0 or limit > const.SPOTIFY_MAX_LIB_SIZE:
            raise ValueError(limit)

        if follow_type == const.PLAYLISTS:
            results = []
            for playlist in self.get_playlists():
                if playlist.owner().spotify_id() != self.spotify_id():
                    results.append(playlist)

            return results[:limit]

        # assert(follow_type == const.ARTISTS)
        uri_params = {
            'type': 'artist',
            'limit': const.SPOTIFY_PAGE_SIZE
        }
        results = []

        # Loop until we get 'limit' many items or run out
        # Can't use _paginate because the artist endpoint does it differently...
        while len(results) < limit:

            # Paginate
            if len(results) != 0:
                uri_params['after'] = results[-1].spotify_id()

            response_json, status_code = utils.request(
                self._session,
                request_type=const.REQUEST_GET,
                endpoint=Endpoints.USER_GET_ARTISTS,
                body=None,
                uri_params=uri_params
            )

            if status_code != 200:
                raise Exception('Oh no TODO!')

            # No more results to grab from spotify
            if len(response_json['artists']['items']) == 0:
                break

            for elem in response_json['artists']['items']:
                results.append(Artist(self._session, elem))

        return results[:limit]


    #@typechecked
    def follow(self, other):
        """ Follow one or more things

        Args:
            other: follow 'other'. Other must be one of the following:
                    Artist
                    User
                    Playlist
                    List: can contain multiple of the above types

        Note: if user is already following other, will do nothing and return
            a success code in response.status()

        Returns:
            None

        Required token scopes:
            user-follow-modify
            playlist-modify-public
            playlist-modify-private

        Calls endpoints:
            PUT     /v1/me/following
            PUT     /v1/playlists/{playlist_id}/followers
        """
        # playlist 200 success
        # user/artist 204 success
        # note: calls are completely different :(

        # Validate input
        if not isinstance(other, list):
            other = [other]

        for elem in other:
            if type(elem) not in [Artist, User, Playlist]:
                raise TypeError(elem)

        # Split up input
        artists = utils.separate(other, Artist)
        users = utils.separate(other, User)
        playlists = utils. separate(other, Playlist)

        '''
        # Get boolean values for whetehr the user has each item saved
        endpoint = Endpoints.USER_HAS_SAVED
        track_bools = utils.batch_get(self._session,
                                      utils.map_ids(tracks),
                                      endpoint % 'tracks')
        album_bools = utils.batch_get(self._session,
                                      utils.map_ids(albums),
                                      endpoint % 'albums')

        # Zip output with input to make tuples
        return list(zip(tracks, track_bools)) + list(zip(albums, album_bools))
        pass
        '''


    #@typechecked
    def unfollow(self, other):
        """ Unfollow one or more things

        Args:
            other: unfollow 'other'. Other must be one of the following:
                    Artist
                    User
                    Playlist
                    List: can contain multiple of the above types

        Note: if user is already not following other, will do nothing and return
            a success code in response.status()

        Returns:
            None

        Required token scopes:
            user-follow-modify
            playlist-modify-public
            playlist-modify-private

        Calls endpoints:
            DELETE  /v1/me/following
            DELETE  /v1/playlists/{playlist_id}/followers
        """
        # playlist 200 success
        # user/artist 204 success
        # note: calls are completely different :(
        pass


    #@typechecked
    def has_saved(self, other):
        """ Check if the user has one or more things saved to their library

        Args:
            other: check if the current user has 'other' saved to the library.
                Other must be one of the following:
                    Track
                    Album
                    List: can contain multiple of the above types

        Returns:
            Success: List of tuples. Each tuple has an input object and whether
                     the user has that object saved.
            Failure: None

        Required token scopes:
            user-library-read

        Calls endpoints:
            GET     /v1/me/albums/contains
            GET     /v1/me/tracks/contains
        """
        # Validate input
        if not isinstance(other, list):
            other = [other]

        for elem in other:
            if type(elem) not in [Track, Album]:
                raise TypeError(elem)

        # Split up input
        tracks = utils.separate(other, Track)
        albums = utils.separate(other, Album)

        # Get boolean values for whetehr the user has each item saved
        endpoint = Endpoints.USER_HAS_SAVED
        track_bools = utils.batch_get(self._session,
                                      utils.map_ids(tracks),
                                      endpoint % 'tracks')
        album_bools = utils.batch_get(self._session,
                                      utils.map_ids(albums),
                                      endpoint % 'albums')

        # Zip output with input to make tuples
        return list(zip(tracks, track_bools)) + list(zip(albums, album_bools))


    #TODO: input arg order / labeling of required vs. optional?
    # TODO: checking return means ret[0][1] for 1 elem...
    #@typechecked
    def get_saved(self,
                  saved_type,
                  limit=None,
                  market=const.TOKEN_REGION):
        """ Get all saved_type objects the user has saved to their library

        Args:
            saved_type: one of sp.ALBUMS or sp.TRACKS
            limit: (int, optional) the max number of items to return. If None,
                will return all. Must be positive.
            market: (required) a 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                if sp.TOKEN_REGION (default) is given, will use appropriate
                country code for user based on their auth token and location.

        Returns:
            List of saved_type objects. Could be empty.

        Required token scopes:
            user-library-read

        Calls endpoints:
            GET     /v1/me/albums
            GET     /v1/me/tracks

        """
        # Validate inputs
        if saved_type not in [const.ALBUMS, const.TRACKS]:
            raise TypeError(saved_type)
        if limit is None:
            limit = const.SPOTIFY_MAX_LIB_SIZE
        if limit <= 0 or limit > const.SPOTIFY_MAX_LIB_SIZE:
            raise ValueError(limit)

        # TODO: should I validate the market?

        endpoint_type = 'albums' if saved_type == const.ALBUMS else 'tracks'
        return_class = Album if saved_type == const.ALBUMS else Track
        uri_params = {'market': market}

        return utils.paginate_get(
                        self._session,
                        limit=limit,
                        return_class=return_class,
                        endpoint=Endpoints.USER_GET_SAVED % endpoint_type,
                        uri_params=uri_params,
                        body=None)


    #@typechecked
    def save(self, other):
        """ Save one or more things to the user's library

        Args:
            other: the object(s) to save. Other must be one of the following:
                    Track
                    Album
                    List: can contain multiple of the above types

        Note: if user already has other saved, will do nothing and return
            a success code in response.status()

        Returns:
            None

        Required token scopes:
            user-library-modify

        Calls endpoints:
            PUT     /v1/me/albums
            PUT     /v1/me/tracks
        """
        # Note: ids can go in body or uri
        # 201 on success
        pass


    #@typechecked
    def remove(self, other):
        """ Remove one or more things from the user's library

        Args:
            other: the object(s) to remove. Other must be one of the following:
                    Track
                    Album
                    List: can contain multiple of the above types

        Note: if user already does not have other saved, will do nothing and
            return a success code in response.status()

        Returns:
            None

        Required token scopes:
            user-library-modify

        Calls endpoints:
            DELETE  /v1/me/albums
            DELETE  /v1/me/tracks
        """
        # Note: ids can go in body or uri
        # 200 on success
        pass

#pylint: disable=wrong-import-position
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.player import Player
from spotifython.playlist import Playlist
from spotifython.track import Track
