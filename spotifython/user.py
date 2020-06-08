""" User class """

# Standard library imports
import copy
import sys

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils
from spotifython.image import Image


# TODO: what to do about partial success on batch operations?
class User:
    #pylint: disable=line-too-long
    """ Represents a Spotify user tied to a unique Spotify id

    Use methods here to interact with a User, such as reading / modifying the
    library and following artists.

    Raises:
        TypeError:  if incorrectly typed parameters are given.
        ValueError: if parameters with illegal values are given.

    Unsupported:

        * external_urls
        * followers: unsupported by Spotify, see https://developer.spotify.com/documentation/web-api/reference/object-model/#followers-object
    """


    def __init__(self, session, info):
        """ Get an instance of User

        This constructor should never be called by the client. To get an
        instance of User, use Session.get_users()

        Args:
            session: an instance of sp.Session
            info: (dict) known values about the user. Must contain 'id'.
        """
        # Validate inputs
        if 'id' not in info:
            raise ValueError('Cannot create a User without a user id')

        self._session = session
        self._id = info['id']
        self._player = Player(self._session, self)

        self._raw = copy.deepcopy(info)

        if 'display_name' not in info:
            self._update_fields()


    def _update_fields(self):
        """ Update self._raw using the User id

        Calls endpoints:
            GET     /v1/users/{id}
        """

        response_json, status_code = utils.request(
            session=self._session,
            request_type=const.REQUEST_GET,
            endpoint=Endpoints.USER_GET_DATA % self.spotify_id()
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        # Updates _raw with new values. One liner : for each key in union of
        # keys in self._raw and response_json, takes value for key from
        # response_json if present, else takes value for key from self._raw.
        # TODO: this is weird notation, make a utility function for it.
        # Especially useful since it is an action necessary for many classes.
        self._raw = {**self._raw, **response_json}


    def _get_private_field(self, key):
        """ Get a private user field.

        If the field isn't in self._raw, update private User info

        Raises:
            AuthenticationError: if this User isn't the one who authorized the
                token, in which case the client can't access private user
                information

        Calls endpoints:
            GET     /v1/me
        """

        if key in self._raw:
            return self._raw[key]

        other = self._session.current_user()
        if self != other:
            raise utils.AuthenticationError(
                f'Can\'t access private user field <{key}>'
            )

        # Updates _raw with new values. One liner : for each key in union of
        # keys in self._raw and response_json, takes value for key from
        # response_json if present, else takes value for key from self._raw.
        # TODO: this is weird notation, make a utility function for it.
        # Especially useful since it is an action necessary for many classes.

        # We know other is a 'User' object, so this protected access is okay
        #pylint: disable=protected-access
        self._raw = {**self._raw, **other._raw}

        return self._raw[key]


    def __str__(self):
        return f'User <{self._id}>'


    def __repr__(self):
        return str(self)


    def __eq__(self, other):
        return utils.spotifython_eq(self, other)


    def __ne__(self, other):
        return not self.__eq__(other)


    def __hash__(self):
        return utils.spotifython_hash(self)


    def spotify_id(self):
        """ Get the id of this user

        Returns:
            The same id that this user was created with as a string.
        """
        return self._id


    def name(self):
        """ Get the User's display name

        Returns:
            str: the display name of the User as it appears on Spotify

        Calls endpoints:
            GET     /v1/users/{id}
        """
        return utils.get_field(self, 'display_name')


    def href(self):
        """ Get the User's href

        Returns:
            str: a link to the Web API endpoint containing the User's profile.

        Calls endpoints:
            GET     /v1/users/{id}
        """
        return utils.get_field(self, 'href')


    def uri(self):
        """ Get the User's uri

        Returns:
            str: the Spotify uri for this User

        Calls endpoints:
            GET     /v1/users/{id}
        """
        return utils.get_field(self, 'uri')


    def image(self):
        """ Get the User's profile picture

        Returns:
            Image: an image object if the User has a profile picture
            None: if the User has no profile picture.

        Calls endpoints:
            GET     /v1/users/{id}
        """
        result = utils.get_field(self, 'images')

        if len(result) > 1:
            raise utils.SpotifyError('User has more than one profile picture!')

        return None if len(result) == 0 else Image(result[0])


    def country(self):
        """ Get the User's country code

        Returns:
            str: an ISO alpha-2 country code

        Calls endpoints:
            GET     /v1/me

        Required token scopes:
            user-read-private

        Raises:
            AuthenticationError: if this User is not the User who made the token
        """
        return self._get_private_field('country')


    def email(self):
        """ Get the User's email address

        Returns:
            str: the email address associated with the account

        Calls endpoints:
            GET     /v1/me

        Required token scopes:
            user-read-email

        Raises:
            AuthenticationError: if this User is not the User who made the token
        """
        return self._get_private_field('email')


    def subscription(self):
        """ Get the User's account subscription

        Returns:
            str: the account's subscription, such as 'premium', 'free', etc.

        Note: Spotify does not define all possible subscription types, so
            instead of returning an enum (like many other methods in the
            library), it returns the raw string. See the 'product' field here:
            https://developer.spotify.com/documentation/web-api/reference/users-profile/get-current-users-profile/
        Calls endpoints:
            GET     /v1/me

        Required token scopes:
            user-read-private

        Raises:
            AuthenticationError: if this User is not the User who made the token
        """
        return self._get_private_field('product')


    def player(self):
        """ Get the player object for this user

        This is how client code should access a player. For example:
            u = sp.get_user(user_id)
            u.player().pause()

        Returns:
            A Player object.
        """
        return self._player


    def top(self,
            top_type,
            limit,
            time_range=const.MEDIUM):
        """ Get the top artists or tracks for the user over a time range.

        Args:
            top_type: get top items of this type. One of:
                sp.ARTISTS
                sp.TRACKS
            limit: (int) max number of items to return. Must be positive.
            time_range: get top items for this time range. One of:
                sp.LONG (several years)
                sp.MEDIUM (about 6 months)
                sp.SHORT (about 4 weeks)

        Returns:
            A list of artists or a list of tracks, depending on top_type
            Could return an empty list.

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


    def recently_played(self, limit=50):
        """ Get the user's recently played tracks

        Args:
            limit: (int) max number of items to return. Must be between 1 and
                50, inclusive.

        Returns:
            A list of tracks. Could be empty.

        Required token scopes:
            user-read-recently-played

        Calls endpoints:
            GET     /v1/me/player/recently-played

        Note:
            * The 'before' and 'after' functionalities are not supported.
            * Does not return the time the tracks were played
            * A track must be played for >30s to be included in the history.
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
            raise utils.SpotifyError(status_code, response_json)

        results = []
        for elem in response_json['items']:
            results.append(Track(self._session, elem))

        return results


    def get_playlists(self, limit=const.MAX_PLAYLISTS):
        """ Get the playlists the user has in their library

        Args:
            limit: (int) the max number of items to return. Must be between
                1 and 100,000 inclusive. Default is 100,000.

        Returns:
            A list of playlists. Could be empty.

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
        if limit <= 0 or limit > const.MAX_PLAYLISTS:
            raise ValueError(limit)

        endpoint = Endpoints.USER_GET_PLAYLISTS % self.spotify_id()

        return utils.paginate_get(
                        self._session,
                        limit=limit,
                        return_class=Playlist,
                        endpoint=endpoint,
                        uri_params={},
                        body=None)


    def create_playlist(self,
                        name,
                        visibility=const.PUBLIC,
                        description=None):
        """ Create a new playlist owned by the current user

        Args:
            name: (str) The name for the new playlist. Does not need to be
                unique; a user may have several playlists with the same name.
            visibility: how other users interact with this playlist. One of:
                    sp.PUBLIC: publicly viewable, not collaborative
                    sp.PRIVATE: not publicly viewable, not collaborative
                    sp.PRIVATE_COLLAB: not publicly viewable, collaborative
            description: (str) viewable description of the playlist.

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
            raise utils.SpotifyError(status_code, response_json)

        return Playlist(self._session, response_json)


    # TODO: checking return of tuple funcs means ret[0][1] for 1 elem...
    def is_following(self, other):
        """ Check if the current user is following something

        Args:
            other: check if current user is following 'other'. Other must be
                one of the following:

                    * Artist
                    * User
                    * Playlist
                    * List: can contain multiple of the above types

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
        artist_bools = []
        for batch in utils.create_batches(utils.map_ids(artists)):
            response_json, status_code = utils.request(
                self._session,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                body=None,
                uri_params={'type': 'artist', 'ids': batch}
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            artist_bools.append(response_json)

        user_bools = []
        for batch in utils.create_batches(utils.map_ids(users)):
            response_json, status_code = utils.request(
                self._session,
                request_type=const.REQUEST_GET,
                endpoint=endpoint,
                body=None,
                uri_params={'type': 'user', 'ids': batch}
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            user_bools.append(response_json)

        # For each playlist in other, check if in the User's followed playlists
        followed_playlists = self.get_following(const.PLAYLISTS)
        playlist_bools = list(map(lambda p: p in followed_playlists, playlists))

        # Zip output with input to make tuples
        artists = list(zip(artists, artist_bools))
        users = list(zip(users, user_bools))
        playlists = list(zip(playlists, playlist_bools))
        return artists + users + playlists


    def get_following(self,
                      follow_type,
                      limit=None):
        #pylint: disable=line-too-long
        """ Get all follow_type objects the current user is following

        Args:
            follow_type: one of:
                sp.ARTISTS
                sp.PLAYLISTS
            limit: (int) the max number of items to return. If None,
                will return all. Must be positive.
                If follow_type == sp.PLAYLISTS, must be <= 100,000
                See here: https://developer.spotify.com/documentation/web-api/reference/playlists/get-list-users-playlists/

        Returns:
            List of follow_type objects. Could be empty.

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
        # Validate follow_type
        if follow_type not in [const.ARTISTS, const.PLAYLISTS]:
            raise TypeError(follow_type)

        # Validate limit
        if limit is not None:
            if limit <= 0:
                raise ValueError(limit)
            if follow_type == const.PLAYLISTS and limit > const.MAX_PLAYLISTS:
                raise ValueError(limit)

        # Set limit if not set
        elif follow_type == const.ARTISTS:
            limit = sys.maxsize
        else:
            limit = const.MAX_PLAYLISTS

        # Deal with followed playlists
        if follow_type == const.PLAYLISTS:
            results = self.get_playlists()

            def filter_func(playlist):
                return playlist.owner().spotify_id() != self.spotify_id()
            results = list(filter(filter_func, results))

            return results[:limit]

        # Deal with followed artists assert(follow_type == const.ARTISTS)
        uri_params = {
            'type': 'artist',
            'limit': const.SPOTIFY_PAGE_SIZE
        }
        results = []

        # Loop until we get 'limit' many items or run out
        # Can't use _paginate_get because artist endpoint does it differently...
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
                raise utils.SpotifyError(status_code, response_json)

            # No more results to grab from spotify
            if len(response_json['artists']['items']) == 0:
                break

            for elem in response_json['artists']['items']:
                results.append(Artist(self._session, elem))

        results = results[:limit] if limit is not None else results
        return results


    def _follow_unfollow_help(self, other, request_type):
        """ follow and unfollow are identical, except for the request type.
        This function implements that functionality to remove duplicate code.
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
        playlists = utils. separate(other, Playlist)

        for batch in utils.create_batches(utils.map_ids(artists)):
            response_json, status_code = utils.request(
                self._session,
                request_type=request_type,
                endpoint=Endpoints.USER_FOLLOW_ARTIST_USER,
                body=None,
                uri_params={'type': 'artist', 'ids': batch}
            )

            if status_code != 204:
                raise utils.SpotifyError(status_code, response_json)

        for batch in utils.create_batches(utils.map_ids(users)):
            response_json, status_code = utils.request(
                self._session,
                request_type=request_type,
                endpoint=Endpoints.USER_FOLLOW_ARTIST_USER,
                body=None,
                uri_params={'type': 'user', 'ids': batch}
            )

            if status_code != 204:
                raise utils.SpotifyError(status_code, response_json)

        for playlist in playlists:
            response_json, status_code = utils.request(
                self._session,
                request_type=request_type,
                endpoint=Endpoints.USER_FOLLOW_PLAYLIST % playlist,
                body=None,
                uri_params=None
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

    def follow(self, other):
        """ Follow one or more things

        Args:
            other: follow 'other'. Other must be one of the following:
                    Artist
                    User
                    Playlist
                    List: can contain multiple of the above types

        Note: does not currently support privately following playlists. Any
            playlists followed will be automatically added to the user's public
            playlists.

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
        self._follow_unfollow_help(other, const.REQUEST_PUT)


    def unfollow(self, other):
        """ Unfollow one or more things

        Args:
            other: unfollow 'other'. Other must be one of the following:
                    Artist
                    User
                    Playlist
                    List: can contain multiple of the above types

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
        self._follow_unfollow_help(other, const.REQUEST_DELETE)


    # TODO: checking return of tuple funcs means ret[0][1] for 1 elem...
    def has_saved(self, other):
        """ Check if the user has one or more things saved to their library

        Args:
            other: check if the current user has 'other' saved to the library.
                Other must be one of the following:

                    * Track
                    * Album
                    * List: can contain multiple of the above types

        Returns:
            List of tuples. Each tuple has an input object and whether the user
            has that object saved.

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

        # Get boolean values for whether the user has each item saved
        endpoint = Endpoints.USER_HAS_SAVED

        track_bools = []
        for batch in utils.create_batches(utils.map_ids(tracks)):
            response_json, status_code = utils.request(
                self._session,
                request_type=const.REQUEST_GET,
                endpoint=endpoint % 'tracks',
                body=None,
                uri_params={'ids': batch}
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            track_bools.append(response_json)

        album_bools = []
        for batch in utils.create_batches(utils.map_ids(albums)):
            response_json, status_code = utils.request(
                self._session,
                request_type=const.REQUEST_GET,
                endpoint=endpoint % 'albums',
                body=None,
                uri_params={'ids': batch}
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)

            album_bools.append(response_json)

        # Zip output with input to make tuples
        zipped_tracks = list(zip(tracks, track_bools))
        zipped_albums = list(zip(albums, album_bools))
        return zipped_tracks + zipped_albums


    def get_saved(self,
                  saved_type,
                  limit=None,
                  market=const.TOKEN_REGION):
        """ Get all saved_type objects the user has saved to their library

        Args:
            saved_type: one of:
                sp.ALBUMS
                sp.TRACKS
            limit: (int) the max number of items to return. If None,
                will return all. Must be positive.
            market: a 2 letter country code as defined here:
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

        if limit is None: # Lists can't be longer than sys.maxsize in python
            limit = sys.maxsize

        if limit <= 0:
            raise ValueError(limit)

        # Make request
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


    def _save_remove_help(self, other, request_type):
        """ save and remove are identical, except for the request type and
        return codes.
        This function implements that functionality to remove duplicate code.
        """
        # Validate input
        if not isinstance(other, list):
            other = [other]

        for elem in other:
            if type(elem) not in [Album, Track]:
                raise TypeError(elem)

        # Split up input
        albums = utils.separate(other, Album)
        tracks = utils.separate(other, Track)

        for batch in utils.create_batches(utils.map_ids(albums)):
            response_json, status_code = utils.request(
                self._session,
                request_type=request_type,
                endpoint=Endpoints.USER_SAVE_ALBUMS,
                body=None,
                uri_params={'ids': batch}
            )

            # All success codes are 200, except saving an album
            success = 201 if request_type == const.REQUEST_PUT else 200
            if status_code != success:
                raise utils.SpotifyError(status_code, response_json)

        for batch in utils.create_batches(utils.map_ids(tracks)):
            response_json, status_code = utils.request(
                self._session,
                request_type=request_type,
                endpoint=Endpoints.USER_SAVE_TRACKS,
                body=None,
                uri_params={'ids': batch}
            )

            if status_code != 200:
                raise utils.SpotifyError(status_code, response_json)


    def save(self, other):
        """ Save one or more things to the user's library

        Args:
            other: the object(s) to save. Other must be one of the following:
                    Track
                    Album
                    List: can contain multiple of the above types

        Returns:
            None

        Required token scopes:
            user-library-modify

        Calls endpoints:
            PUT     /v1/me/albums
            PUT     /v1/me/tracks
        """
        self._save_remove_help(other, const.REQUEST_PUT)


    def remove(self, other):
        """ Remove one or more things from the user's library

        Args:
            other: the object(s) to remove. Other must be one of the following:
                    Track
                    Album
                    List: can contain multiple of the above types

        Returns:
            None

        Required token scopes:
            user-library-modify

        Calls endpoints:
            DELETE  /v1/me/albums
            DELETE  /v1/me/tracks
        """
        self._save_remove_help(other, const.REQUEST_DELETE)


#pylint: disable=wrong-import-position
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.player import Player
from spotifython.playlist import Playlist
from spotifython.track import Track
