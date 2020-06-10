""" User class

This class represents a Player object, which is tied to a Spotifython User
object.

"""

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils


# GLobal variables
KEYSTRING = 'Spotify response missing data'


class Player:
    """ Interact with a user's playback, such as pausing / playing the current
        song, modifying the queue, etc.

    Getting an instance of Player should only be done using User.player()

    Shared args:
        device_id: the device the command should target.
            The given id must be a device listed in player.available_devices().
            If the id is invalid, response.content() will be set to None, and
            response.status() will contain an error code.

            Defaults to using the currently active device, which is what you
            will want most of the time.

        position: an integer that always represents milliseconds.

    Raises:
        TypeError:  if incorrectly typed parameters are given.
        ValueError: if parameters with illegal values are given.
        SpotifyError: if there is no active or available device and no device_id
            is given.
        SpotifyError: if the action is disallowed.
            Note that some actions that should be allowed (such as pausing while
            paused) are difficult to implement because the Spotify player API is
            in beta. For example, according to the docs, pausing while paused
            should return a 403 with reason string 'ALREADY_PAUSED', however the
            reason string actually given is 'UNKNOWN'. Player.pause() can't case
            on the reason string, and is forced to raise an exception if
            playback is already paused.

    Note:
        Due to the asynchronous nature of many Player commands, you should use
        the Player's getter methods to check that your issued command was
        handled correctly by the player.
    """


    def __init__(self, session, user):
        """ Get an instance of Player

        This constructor should never be called by the client. To get an
        instance of Player, use User.player().

        Args:
            session: a Session instance
            user: the User object the Player is associated with
        """
        self._session = session
        self._user = user


    # Format should be 'Player for user <%s>' with user_id
    def __str__(self):
        return 'Player for %s' % str(self._user)


    def __repr__(self):
        return str(self)


    def __eq__(self, other):
        #pylint: disable=unidiomatic-typecheck
        return type(self) == type(other) and self._user == other._user


    def __ne__(self, other):
        return not self == other


    def __hash__(self):
        hash_str = self.__class__.__name__
        hash_str += str(hash(self._user))
        return hash(hash_str)


    # Behavior inconsistent with documentation when no active device. See:
    #   https://github.com/spotify/web-api/issues/1588
    def _player_data(self,
                     key,
                     market=const.TOKEN_REGION,
                     should_raise_error=True):
        """ Helper function for the getter methods.
        Wraps calling the player endpoint and handling a missing key.

        Args:
            key: the key to get from the currently playing context
            market: used in track relinking
            should_raise_error:
                if False: returns None when no device available
                if True: raises SpotifyError when no device available

        Returns:
            None if there is no active device and should_raise_error is False
            The result of player_data[key] otherwise

        Raises:
            SpotifyError: if Spotify returns an error or the key isn't found
            NetworkError: for misc network failures

        Calls endpoints:
            GET    /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_GET,
            endpoint=Endpoints.PLAYER_GET_DATA,
            body=None,
            uri_params={'market': market}
        )

        # No active device
        # TODO: update when bug report is resolved
        if status_code == 204:
            if not should_raise_error:
                return None
            raise utils.SpotifyError('No active device',
                                     status_code,
                                     response_json)

        # Valid Player errors
        if status_code in [403, 404]:
            raise utils.SpotifyError(status_code, response_json)

        # Misc other failure
        if status_code != 200:
            raise utils.NetworkError(status_code, response_json)

        if key not in response_json:
            raise utils.SpotifyError(KEYSTRING + ': key <%s> not found' % key)

        return response_json[key]


    def user(self):
        """ Get the User associated with this player
        """
        return self._user


    def skip(self, device_id=None):
        """ Skip the current song in the playback

        Returns:
            None

        Calls endpoints:
            POST    /v1/me/player/next

        Required token scopes:
            user-modify-playback-state
        """
        uri_params = None if device_id is None else {'device_id': device_id}

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_POST,
            endpoint=Endpoints.PLAYER_SKIP,
            body=None,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    def previous(self, device_id=None):
        """ Skip to the previous song.

        Note: will skip to the previous song in the playback regardless of where
            in the current song playback is.

        Returns:
            None

        Calls endpoints:
            POST    /v1/me/player/previous

        Required token scopes:
            user-modify-playback-state
        """
        uri_params = None if device_id is None else {'device_id': device_id}

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_POST,
            endpoint=Endpoints.PLAYER_PREVIOUS,
            body=None,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    def pause(self, device_id=None):
        """ Pause the current playback

        Returns:
            None

        Calls endpoints:
            PUT     /v1/me/player/pause

        Required token scopes:
            user-modify-playback-state

        Raises:
            SpotifyError: if playback is not playing (or already paused)
        """
        uri_params = None if device_id is None else {'device_id': device_id}

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_PUT,
            endpoint=Endpoints.PLAYER_PAUSE,
            body=None,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    def resume(self, device_id=None):
        """ Resume the current playback

        Returns:
            None

        Calls endpoints:
            PUT     /v1/me/player/play

        Required token scopes:
            user-modify-playback-state

        Raises:
            SpotifyError: if playback is already playing
        """
        uri_params = None if device_id is None else {'device_id': device_id}

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_PUT,
            endpoint=Endpoints.PLAYER_PLAY,
            body=None,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    # TODO: Future support: position in track
    # TODO: manual testing once Session is merged / can easily get Artist etc.
    def play(self, item, offset=0, device_id=None):
        """ Change the current track and context for the player

        If device_id is None and no active device exists, raises SpotifyError

        Args:
            item: an instance of sp.Track, sp.Album, sp.Playlist, or sp.Artist.
            offset: a non-negative integer representing the position in item to
                start playback.
                Ignored if item is not an Album or Playlist.
                0 <= offset < len(item)

        Note: playback will start at the beginning of the track.  Use in
            combination with Player.set_playback_position to start elsewhere in
            the item.

        Returns:
            None

        Calls endpoints:
            PUT     /v1/me/player/play

        Required token scopes:
            user-modify-playback-state
        """
        # Validate inputs
        if type(item) not in [Track, Album, Playlist, Artist]:
            raise TypeError(item)

        if type(item) in [Album, Playlist]:
            if offset < 0 or offset >= len(item):
                raise ValueError(offset)

        # Build up the request
        uri_params = None if device_id is None else {'device_id': device_id}
        if isinstance(item, Track):
            body = {'uris': [item.uri()]}
        else:
            body = {'context_uri': item.uri()}

        if type(item) in [Album, Playlist]:
            body['offset'] = {'position': offset}

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_PUT,
            endpoint=Endpoints.PLAYER_PLAY,
            body=body,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    def is_playing(self):
        """ Check if the current playback is playing (not paused)

        Uses the currently active device, if one exists.

        Returns:
            True if playing, else False

        Calls endpoints:
            GET    /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        return self._player_data('is_playing')


    def is_paused(self):
        """ Check if the current playback is paused

        Uses the currently active device, if one exists.

        Returns:
            True if paused, else False

        Calls endpoints:
            GET    /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        return not self.is_playing()


    # Note for me: in the future, add 'additional_types' to support episodes.
    def currently_playing(self, market=const.TOKEN_REGION):
        """ Get the currently playing track in the playback

        Uses the currently active device, if one exists.

        Args:
            market: (str) a 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                if sp.TOKEN_REGION (default) is given, will use appropriate
                country code for user based on their auth token and location.

        Returns:
            A Track object if there is a track playing
            None if nothing is playing

        Calls endpoints:
            GET    /v1/me/player

            Does NOT use GET /v1/me/player/currently-playing
            The data returned at that endpoint is a subset of /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        item = self._player_data('item', market)
        return Track(self._session, item)


    def context(self, market=const.TOKEN_REGION):
        """ Get the currently playing context for the playback

        Uses the currently active device, if one exists.

        Args:
            market: (str) a 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                if sp.TOKEN_REGION (default) is given, will use appropriate
                country code for user based on their auth token and location.

        Returns:
            An Album, Artist, or Playlist if there is a context for the playback
            None if there is no context

        Calls endpoints:
            GET    /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        context = self._player_data('context', market)
        if context is None:
            return None

        # Validate context
        if 'uri' not in context or 'type' not in context:
            raise utils.SpotifyError(KEYSTRING)

        # uri of form 'spotify:type:id'
        context_id = context['uri'].split(':')[-1]

        # Context can only be one of Artist, Album, or Playlist
        if context['type'] == 'album':
            return self._session.get_albums(context_id)
        if context['type'] == 'artist':
            return self._session.get_artists(context_id)
        if context['type'] == 'playlist':
            return self._session.get_playlists(context_id)

        raise utils.SpotifyError('Unrecognized context: %s' % str(context))


    # Note for me: in the future add a separate device abstraction
    def available_devices(self):
        """ Get all devices currently available

        Returns:
            A list of strings, where each is a device id.

        Calls endpoints:
            GET     /v1/me/player/devices

        Required token scopes:
            user-read-playback-state
        """
        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_GET,
            endpoint=Endpoints.PLAYER_AVAILABLE_DEVICES,
            body=None,
            uri_params=None
        )

        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        try:
            devices = response_json['devices']
            result = [elem['id'] for elem in devices]
        except KeyError:
            raise utils.SpotifyError(KEYSTRING)

        return result


    def get_active_device(self):
        """ Get the currently active device

        Returns:
            The device id of the active device, if a device is active.
            None if there is no active device.

        Calls endpoints:
            GET     /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        device = self._player_data('device', should_raise_error=False)
        if device is None:
            return None

        if 'id' not in device:
            raise utils.SpotifyError(KEYSTRING + ': key \'id\' not found')

        return device['id']


    def set_active_device(self, device_id, force_play=const.KEEP_PLAY_STATE):
        """ Transfer playback to a different available device

        Args:
            force_play: one of:
                sp.FORCE_PLAY: resume playback after transfering to new device
                sp.KEEP_PLAY_STATE: keep the current playback state.

        Returns:
            None

        Calls endpoints:
            PUT     /v1/me/player

        Required token scopes:
            user-modify-playback-state
        """
        if force_play not in [const.FORCE_PLAY, const.KEEP_PLAY_STATE]:
            raise ValueError(force_play)

        body = {'device_ids': [device_id],
                'play': force_play == const.FORCE_PLAY}

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_PUT,
            endpoint=Endpoints.PLAYER_TRANSFER,
            body=body,
            uri_params=None
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    def get_shuffle(self):
        """ Get the current shuffle state of the playback

        Uses the currently active device, if one exists.

        Returns:
            True if shuffle is enabled else False

        Calls endpoints:
            GET    /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        return self._player_data('shuffle_state')


    def set_shuffle(self, shuffle_state, device_id=None):
        """ Set the shuffle state of the active device

        Args:
            shuffle_state: (bool)
                True to set shuffle to on
                False to set shuffle to off

        Returns:
            None

        Calls endpoints:
            PUT     /v1/me/player/shuffle

        Required token scopes:
            user-modify-playback-state
        """
        uri_params = {'state': shuffle_state}
        if device_id is not None:
            uri_params['device_id'] = device_id

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_PUT,
            endpoint=Endpoints.PLAYER_SHUFFLE,
            body=None,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    def get_playback_position(self):
        """ Get the current position in the currently playing track in ms

        Uses the currently active device, if one exists.

        Returns:
            The position (in ms) as an int.

        Calls endpoints:
            GET    /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        result = self._player_data('progress_ms')
        return int(result)


    def set_playback_position(self, position, device_id=None):
        """ Set the current position in the currently playing track in ms

        Args:
            position: (int) the position (in ms) as an int. Must be
                non-negative. If greater than the len of the track, will play
                the next song.

        Returns:
            None

        Calls endpoints:
            PUT     /v1/me/player/seek

        Required token scopes:
            user-modify-playback-state
        """
        if position < 0:
            raise ValueError(position)

        uri_params = {'position_ms': position}
        if device_id is not None:
            uri_params['device_id'] = device_id

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_PUT,
            endpoint=Endpoints.PLAYER_SEEK,
            body=None,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    def get_volume(self):
        """ Get the current volume for the playback

        Returns:
            The volume (in percent) as an int from 0 to 100 inclusive.

        Calls endpoints:
            GET    /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        device = self._player_data('device')
        if 'volume_percent' not in device:
            raise utils.SpotifyError(KEYSTRING+': key volume_percent not found')

        return device['volume_percent']


    def set_volume(self, volume, device_id=None):
        """ Set the current volume for the playback

        Args:
            volume: (int) volume (in percent) as an int from 0 to 100 inclusive

        Returns:
            None

        Calls endpoints:
            PUT     /v1/me/player/volume

        Required token scopes:
            user-modify-playback-state
        """
        if volume < 0 or volume > 100:
            raise ValueError(volume)

        uri_params = {'volume_percent': volume}
        if device_id is not None:
            uri_params['device_id'] = device_id

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_PUT,
            endpoint=Endpoints.PLAYER_VOLUME,
            body=None,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    def get_repeat(self):
        """ Get the repeat state for the current playback

        Uses the currently active device, if one exists.

        Returns:
            One of sp.TRACKS, sp.CONTEXT, sp.OFF

        Calls endpoints:
            GET    /v1/me/player

        Required token scopes:
            user-read-playback-state
        """
        result = self._player_data('repeat_state')

        states = {
            const.TRACKS: 'track',
            const.CONTEXT: 'context',
            const.OFF: 'off'
        }
        if result not in states:
            raise utils.SpotifyError('Repeat state <%s> not defined' % result)

        return states[result]


    def set_repeat(self, mode, device_id=None):
        """ Set the repeat state for the current playback

        Args:
            mode: one of
                sp.TRACKS: repeat the current track
                sp.CONTEXT: repeat the current context (playlist, album, etc.)
                sp.OFF: turn repeat off

        Returns:
            None

        Calls endpoints:
            PUT     /v1/me/player/repeat

        Required token scopes:
            user-modify-playback-state
        """
        if mode not in [const.TRACKS, const.CONTEXT, const.OFF]:
            raise ValueError(mode)

        states = {
            const.TRACKS: 'track',
            const.CONTEXT: 'context',
            const.OFF: 'off'
        }
        uri_params = {'state': states[mode]}
        if device_id is not None:
            uri_params['device_id'] = device_id

        response_json, status_code = utils.request(
            self._session,
            request_type=const.REQUEST_PUT,
            endpoint=Endpoints.PLAYER_REPEAT,
            body=None,
            uri_params=uri_params
        )

        if status_code != 204:
            raise utils.SpotifyError(status_code, response_json)


    # Note for me: add episodes at some point
    def enqueue(self, item, device_id=None):
        """ Add an item to the end of the queue

        Args:
            item: the item to add to the queue. One of:
                Album
                Track
                Playlist

            Note that if a playlist is added, the order of added songs may be
            inconsistent.

        Returns:
            None

        Note: when adding an Album or Playlist, this method can fail partway
            through, resulting in only some Tracks being added to the queue.

        Calls endpoints:
            POST    /v1/me/player/queue

        Required token scopes:
            user-modify-playback-state
        """
        if type(item) not in [Album, Track, Playlist]:
            raise ValueError(item)

        # Make into an iterable
        if isinstance(item, Track):
            item = [item]

        uri_params = {} if device_id is None else {'device_id': device_id}

        # Can only enqueue one item at a time
        for track in item:
            uri_params['uri'] = track.uri()

            response_json, status_code = utils.request(
                self._session,
                request_type=const.REQUEST_POST,
                endpoint=Endpoints.PLAYER_QUEUE,
                body=None,
                uri_params=uri_params
            )

            if status_code != 204:
                raise utils.SpotifyError(status_code, response_json)


#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.playlist import Playlist
from spotifython.track import Track
