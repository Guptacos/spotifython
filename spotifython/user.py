''' User class

This class represents a User object, tied to a Spotify user id.

'''

# Standard library imports
from __future__ import annotations # Allow type hinting a class within the class
import math

# Local imports
from spotifython.spotifython import Spotifython as sp
from .endpoint import Endpoint


# TODO: fix imports after integrating.
# TODO: feels like TypeError and ValueError used interchangeably
# TODO: have to implement equality methods
# TODO: market as input?
# TODO: what to do about partial success?
# TODO: return success vs failure in docstring
# TODO: default params

class User:
    ''' Define behaviors related to a user, such as reading / modifying the
        library and following artists.

    Getting an instance of User should be done using spotifython.get_users()

    Exceptions:
        TypeError:  if incorrectly typed parameters are given.
        ValueError: if parameters with illegal values are given.
    '''


    #@typechecked
    def __init__(self,
                 sp_obj,
                 user_info=None):
        '''
        Keyword arguments:
            sp_obj: a Spotifython instance
            user_info: a dictionary containing known values about the user
        '''
        self._sp_obj = sp_obj
        self._raw = user_info
        self._player = Player(self._sp_obj, self)


    def __str__(self):
        uid = self._raw.get('id', None)
        # TODO:
        if uid is None:
            return super().__str__()
        return 'User <%s>' % uid


    def _paginate_get(self,
                      limit,
                      return_class,
                      endpoint,
                      uri_params=None,
                      body=None):
        #pylint: disable=too-many-arguments
        ''' Helper function to make many requests to Spotify

        Keyword arguments:
            limit: (int) the maximum number of items to return
            return_class: the class to construct for the list contents
            endpoint: (str) the endpoint to call.
                Must accept 'limit' and 'offset' in uri_params
                Return json must contain key 'items'
            uri_params: (dict) the uri parameters for the request
            body: (dict) the body of the call

        Return:
            a list of objects of type return_class
        '''
        # Execute requests
        results = []
        offset = 0
        uri_params['limit'] = sp.SPOTIFY_PAGE_SIZE

        # Loop until we get 'limit' many items or run out
        next_multiple = lambda num, mult: math.ceil(num / mult) * mult

        num_to_request = next_multiple(limit, sp.SPOTIFY_PAGE_SIZE)
        while offset < num_to_request:

            uri_params['offset'] = offset

            response_json, status_code = self._sp_obj._request(
                request_type=sp.REQUEST_GET,
                endpoint=endpoint,
                body=body,
                uri_params=uri_params
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


    # TODO: partial failure?
    def _batch_get(self,
                   elements,
                   endpoint,
                   uri_params=None):
        ''' Helper to break a large request into many smaller requests so that
            Spotify doesn't complain.

        Keyword arguments:
            elements: (list) the things to be sent to Spotify
            endpoint: (str) the Spotify endpoint to send a GET request
            uri_params: (dict) any uri params besides 'id' to be sent

        Returns:
            A list of tuples, where each tuple contains one of the input
            elements and the boolean value Spotify returned for that element.
        '''
        if uri_params is None:
            uri_params = {}

        def create_batches(elems, chunk_size=sp.SPOTIFY_PAGE_SIZE):
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
        batches = create_batches(elements, sp.SPOTIFY_PAGE_SIZE)
        results = []
        for batch in batches:
            uri_params['ids'] = [elem.spotify_id() for elem in batch]

            response_json, status_code = self._sp_obj._request(
                request_type=sp.REQUEST_GET,
                endpoint=endpoint,
                body=None,
                uri_params=uri_params
            )

            if status_code != 200:
                raise Exception('Oh no TODO!')

            results += list(zip(batch, response_json))

        return results


    def _update_internal(self, new_vals):
        ''' Used internally to keep cached data up to date

        Keyword arguments:
            new_vals: (dict) the fields that should be added to or updated in
                the internal cache. Any values in the dictionary will become the
                new value for that key.

        Return:
            None
        '''
        # {**A, **B} returns (A - B) U B
        self._raw = {**self._raw, **new_vals}


    def spotify_id(self):
        ''' Get the id of this user

        Return:
            The same id that this user was created with as a string.
        '''
        result = self._raw.get('id', None)
        if result is None:
            raise Exception('Uh oh! TODO!')

        return result


    def player(self):
        ''' Get the player object for this user

        This is how client code should access a player. For example:
            u = sp.get_user(user_id)
            u.player().pause()

        Return:
            A Player object.
        '''
        return self._player


    # TODO: can this return more than 50?
    #@typechecked
    def top(self,
            top_type,
            limit,
            time_range=sp.MEDIUM):
        ''' Get the top artists or tracks for the user over a time range.

        Keyword arguments:
            top_type: only get items of this type. One of:
                sp.ARTIST
                sp.TRACK
            limit: (int) max number of items to return. Must be positive.
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
            raise TypeError(top_type)
        if time_range not in [sp.LONG, sp.MEDIUM, sp.SHORT]:
            raise TypeError(time_range)
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
        return_class = Artist if top_type == sp.ARTIST else Track

        # Execute requests
        return self._paginate_get(
                        limit=limit,
                        return_class=return_class,
                        endpoint=Endpoint.USER_TOP % endpoint_type,
                        uri_params=uri_params,
                        body=None)


    #@typechecked
    def recently_played(self, limit=50):
        ''' Get the user's recently played tracks

        Keyword arguments:
            limit: (int, optional) max number of items to return. Must be
                between 1 and 50, inclusive.

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
            request_type=sp.REQUEST_GET,
            endpoint=Endpoint.USER_RECENTLY_PLAYED,
            body=None,
            uri_params={'limit': limit}
        )

        if status_code != 200:
            raise Exception('Oh no TODO!')

        results = []
        for elem in response_json['items']:
            results.append(Track(self._sp_obj, elem))

        return results


    #@typechecked
    # TODO: default value
    def get_playlists(self, limit=None):
        ''' Get all playlists that this user has in their library

        Keyword arguments:
            limit: (int, optional) the max number of items to return. If None,
                will return all. Must be between 1 and 100,000 inclusive.

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

        endpoint = Endpoint.USER_GET_PLAYLISTS % self.spotify_id()

        return self._paginate_get(
                        limit=limit,
                        return_class=Playlist,
                        endpoint=endpoint,
                        uri_params={},
                        body=None)


    #@typechecked
    def create_playlist(self,
                        name,
                        visibility=sp.PUBLIC,
                        description=None):
        ''' Create a new playlist owned by the current user

        Keyword arguments:
            name: (str) The name for the new playlist. Does not need to be
                unique; a user may have several playlists with the same name.
            visibility: (optional) describes how other users can interact with
                this playlist. One of:
                    sp.PUBLIC: publicly viewable, not collaborative
                    sp.PRIVATE: not publicly viewable, not collaborative
                    sp.PRIVATE_COLLAB: not publicly viewable, collaborative
            description: (str, optional) viewable description of the playlist.

        Return:
            The newly created Playlist object. Note that this function modifies
            the user's library.

        Auth token requirements:
            playlist-modify-public
            playlist-modify-private

        Calls endpoints:
            POST    /v1/users/{user_id}/playlists
        '''
        # Validate inputs
        if visibility not in [sp.PUBLIC, sp.PRIVATE, sp.PRIVATE_COLLAB]:
            raise TypeError(visibility)

        body = {
            'name': name,
            'public': visibility == sp.PUBLIC,
            'collaborative': visibility == sp.PRIVATE_COLLAB
        }

        if description is not None:
            body['description'] = description

        response_json, status_code = self._sp_obj._request(
            request_type=sp.REQUEST_POST,
            endpoint=Endpoint.USER_CREATE_PLAYLIST % self.spotify_id(),
            body=body,
            uri_params=None
        )

        if status_code != 201:
            raise Exception('Oh no TODO!')

        return Playlist(self._sp_obj, response_json)


    #@typechecked
    def is_following(self, other):
        ''' Check if the current user is following something

        Keyword arguments:
            other: check if current user is following 'other'. Other must be
                one of the following:
                    Artist
                    User
                    Playlist
                    List: can contain multiple of the above types

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
        if not isinstance(other, list):
            other = [other]

        artists = list(filter(lambda elem: isinstance(elem, Artist), other))
        users = list(filter(lambda elem: isinstance(elem, User), other))
        playlists = list(filter(lambda elem: isinstance(elem, Playlist), other))

        endpoint = Endpoint.USER_FOLLOWING_CONTAINS
        results = self._batch_get(artists, endpoint, {'type': 'artist'})
        results += self._batch_get(users, endpoint, {'type': 'user'})

        # For each playlist in other, check if in the User's followed playlists
        followed_playlists = self.get_following(sp.PLAYLIST)
        results += list(map(lambda p: (p, p in followed_playlists), playlists))

        return results


    #@typechecked
    # TODO: default parameter limit
    def get_following(self,
                      follow_type,
                      limit=None):
        ''' Get all follow_type objects the current user is following

        Keyword arguments:
            follow_type: one of sp.ARTIST or sp.PLAYLIST
            limit: (int, optional) the max number of items to return. If None,
                will return all. Must be between 1 and 100000 inclusive.

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
            limit = sp.SPOTIFY_MAX_LIB_SIZE
        if limit <= 0 or limit > sp.SPOTIFY_MAX_LIB_SIZE:
            raise ValueError(limit)

        if follow_type == sp.PLAYLIST:
            results = []
            for playlist in self.get_playlists():
                if playlist.owner().spotify_id() != self.spotify_id():
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
                uri_params['after'] = results[-1].spotify_id()

            response_json, status_code = self._sp_obj._request(
                request_type=sp.REQUEST_GET,
                endpoint=Endpoint.USER_GET_ARTISTS,
                body=None,
                uri_params=uri_params
            )

            if status_code != 200:
                raise Exception('Oh no TODO!')

            # No more results to grab from spotify
            if len(response_json['artists']['items']) == 0:
                break

            for elem in response_json['artists']['items']:
                results.append(Artist(self._sp_obj, elem))

        return results[:limit]


    #@typechecked
    def follow(self, other):
        ''' Follow one or more things

        Keyword arguments:
            other: follow 'other'. Other must be one of the following:
                    Artist
                    User
                    Playlist
                    List: can contain multiple of the above types

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


    #@typechecked
    def unfollow(self, other):
        ''' Unfollow one or more things

        Keyword arguments:
            other: unfollow 'other'. Other must be one of the following:
                    Artist
                    User
                    Playlist
                    List: can contain multiple of the above types

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


    #@typechecked
    def has_saved(self, other):
        ''' Check if the user has one or more things saved to their library

        Keyword arguments:
            other: check if the current user has 'other' saved to the library.
                Other must be one of the following:
                    Track
                    Album
                    List: can contain multiple of the above types

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
        if not isinstance(other, list):
            other = [other]

        tracks = list(filter(lambda elem: isinstance(elem, Track), other))
        albums = list(filter(lambda elem: isinstance(elem, Album), other))

        endpoint = Endpoint.USER_HAS_SAVED
        results = self._batch_get(tracks, endpoint % 'tracks')
        results += self._batch_get(albums, endpoint % 'albums')

        return results


    #TODO: input arg order / labeling of required vs. optional?
    #@typechecked
    def get_saved(self,
                  saved_type,
                  limit=None,
                  market=sp.TOKEN_REGION):
        ''' Get all saved_type objects the user has saved to their library

        Keyword arguments:
            saved_type: one of sp.ALBUM or sp.TRACK
            limit: (int, optional) the max number of items to return. If None,
                will return all. Must be positive.
            market: (required) a 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                if sp.TOKEN_REGION (default) is given, will use appropriate
                country code for user based on their auth token and location.

        Return:
            List of saved_type objects. Could be empty.

        Auth token requirements:
            user-library-read

        Calls endpoints:
            GET     /v1/me/albums
            GET     /v1/me/tracks

        '''
        # Validate inputs
        if saved_type not in [sp.ALBUM, sp.TRACK]:
            raise TypeError(saved_type)
        if limit is None:
            limit = sp.SPOTIFY_MAX_LIB_SIZE
        if limit <= 0 or limit > sp.SPOTIFY_MAX_LIB_SIZE:
            raise ValueError(limit)

        # TODO: should I validate the market?

        endpoint_type = 'albums' if saved_type == sp.ALBUM else 'tracks'
        return_class = Album if saved_type == sp.ALBUM else Track
        uri_params = {'market': market}

        return self._paginate_get(
                        limit=limit,
                        return_class=return_class,
                        endpoint=Endpoint.USER_GET_SAVED % endpoint_type,
                        uri_params=uri_params,
                        body=None)


    #@typechecked
    def save(self, other):
        ''' Save one or more things to the user's library

        Keyword arguments:
            other: the object(s) to save. Other must be one of the following:
                    Track
                    Album
                    List: can contain multiple of the above types

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


    #@typechecked
    def remove(self, other):
        ''' Remove one or more things from the user's library

        Keyword arguments:
            other: the object(s) to remove. Other must be one of the following:
                    Track
                    Album
                    List: can contain multiple of the above types

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

#pylint: disable=wrong-import-position
from .album import Album
from .artist import Artist
from .player import Player
from .playlist import Playlist
from .track import Track
