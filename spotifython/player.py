""" User class

This class represents a Player object, which is tied to a User

"""

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils

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

        position: always an integer that represents milliseconds.

    Raises:
        TypeError:  if incorrectly typed parameters are given.
        ValueError: if parameters with illegal values are given.
        SpotifyError: if there is no active or available device.

    Note:
        Due to the asynchronous nature of many Player commands, you should use
        the Player's getter methods to check that your issued command was
        handled correctly by the player.
    """


    def __init__(self, session, user):
        """ Should only be called from within the User class

        Args:
            session: a Spotifython instance
            user: the User object the Player is associated with
        """
        pass


    # Format should be 'Player for user <%s>' with user_id
    def __str__(self) -> str:
        return ''


    def __repr__(self):
        pass


    def __eq__(self, other):
        pass


    def __ne__(self, other):
        pass


    def __hash__(self):
        pass


    def user(self):
        """ Get the User associated with this player
        """
        pass


    def next(self, device_id=None):
        """ Skip the current song in the playback

        Returns:
            None
        """
        # POST /v1/me/player/next
        pass


    def previous(self, device_id=None):
        """ Skip to the previous song.

        Note: will skip to the previous song in the playback regardless of where
            in the current song playback is.

        Returns:
            None
        """
        # POST /v1/me/player/previous


    # Note for me: if nothing playing and pause, raises 403 restriction violated
    def pause(self, device_id=None):
        """ Pause the current playback

        Returns:
            None
        """
        # PUT /v1/me/player/pause
        pass


    # Note for me: if playing and resume, raises 403 restriction violated
    def resume(self, device_id=None):
        """ Resume the current playback

        Returns:
            None
        """
        # PUT /v1/me/player/play
        pass


    # Future support: inputing a context object
    # Future support: offsetting into context
    # Future support: position in track
    def play(self, item, device_id=None):
        """ Change the current track and context for the player

        Uses the currently active device, if one exists.

        Args:
            item: an instance of sp.Track, sp.Album, sp.Playlist, or sp.Artist.
                to begin playing.

        Note: Does not currently support playing a specific context, or an
            offset into a playlist, album, or artist. Also does not support
            starting playback at a position in the track, playback will start at
            the beginning of the track.

        Returns:
            None
        """
        # PUT /v1/me/player/play
        pass


    def is_paused(self):
        """ Check if the current playback is paused

        Uses the currently active device, if one exists.

        Returns:
            True if paused, else False
        """
        # GET /v1/me/player
        pass


    def is_playing(self):
        """ Check if the current playback is playing (not paused)

        Uses the currently active device, if one exists.

        Returns:
            True if playing, else False
        """
        # GET /v1/me/player
        pass


    # TODO: This method name is not final. Here are alternatives we considered:
    # get_currently_playing
    # now_playing
    # get_active_audio
    # Note for me: in the future, add 'additional_types' to support episodes.
    # Note for me: in the future support returning a context object
    def get_currently_playing(self, market=const.TOKEN_REGION):
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
        """
        # GET /v1/me/player/currently-playing
        pass


    # Note for me: in the future add a separate device abstraction
    def available_devices(self):
        """ Get all devices currently available

        Returns:
            A list of strings, where each is a device id.
        """
        # GET /v1/me/player/devices
        pass


    def get_active_device(self):
        """ Get the currently active device

        Returns:
            The device id of the active device, if a device is active.
            None if there is no active device.
        """
        # GET /v1/me/player
        pass


    def set_active_device(self, device_id, force_play=const.KEEP_PLAY_STATE):
        """ Transfer playback to a different available device

        Args:
            force_play: one of:
                sp.FORCE_PLAY: resume playback after transfering to new device
                sp.KEEP_PLAY_STATE: keep the current playback state.

        Returns:
            None
        """
        # PUT /v1/me/player
        pass


    def get_shuffle(self):
        """ Get the current shuffle state of the playback

        Uses the currently active device, if one exists.

        Returns:
            True if shuffle is enabled else False
        """
        # GET /v1/me/player
        pass


    def set_shuffle(self, shuffle_state: bool, device_id=None):
        """ Set the shuffle state of the active device

        Args:
            shuffle_state: (bool)
                True to set shuffle to on
                False to set shuffle to off

        Returns:
            None
        """
        # PUT /v1/me/player/shuffle
        pass


    def get_playback_position(self):
        """ Get the current position in the currently playing track in ms

        Uses the currently active device, if one exists.

        Returns:
            The position (in ms) as an int if there is an active playback.
            None if there is no active playback. TODO: is this possible?
        """
        # GET /v1/me/player
        pass


    def set_playback_position(self, position, device_id=None):
        """ Set the current position in the currently playing track in ms

        Args:
            position: (int) the position (in ms) as an int. Must be
                non-negative. If greater than the len of the track, will play
                the next song.

        Returns:
            None
        """
        # PUT /v1/me/player/seek
        pass


    def get_volume(self):
        """ Get the current volume for the playback

        Uses the currently active device, if one exists.

        Returns:
            The volume (in percent) as an int from 0 to 100 inclusive.
            TODO: What if there is no active playback?
        """
        # GET /v1/me/player
        pass


    def set_volume(self, volume, device_id=None):
        """ Set the current volume for the playback

        Args:
            volume: (int) volume (in percent) as an int from 0 to 100 inclusive

        Returns:
            None
        """
        # PUT /v1/me/player/volume
        pass


    def get_repeat(self):
        """ Get the repeat state for the current playback

        Uses the currently active device, if one exists.

        Returns:
            One of sp.TRACKS, sp.CONTEXT, sp.OFF
        """
        # GET /v1/me/player
        pass


    def set_repeat(self, mode, device_id=None):
        """ Set the repeat state for the current playback

        Args:
            mode: one of
                sp.TRACKS: repeat the current track
                sp.CONTEXT: repeat the current context (playlist, album, etc.)
                sp.OFF: turn repeat off

        Returns:
            None
        """
        # PUT /v1/me/player/repeat
        pass


    # Note for me: add episodes at some point
    def enqueue(self, item, device_id=None):
        """ Add an item to the end of the queue

        Args:
            item: the item to add to the queue. Must be an instance of sp.Album
                or sp.Track. Adding playlists to the queue is not currently
                supported.

        Returns:
            None
        """
        # POST /v1/me/player/queue
        pass


class Context:
    """ A container class used by the Player

    Allows you to set a context (such as an album, playlist, or artist) when
    modifying playback.

    This class is immutable.
    """


    def __init__(self, item, offset=0):
        """ Create a Context for playback

        Args:
            item: one of:
                Artist
                Playlist
                Album
                List[Tracks]
            offset: 0 indexed start index item. Ignored if item is an Artist.
                One of:
                int: must be >= 0 and < len(item). Position into item where
                    playback should start.
                Track: must be a Track object in item.
        """
        # Validate item
        if type(item) not in [Artist, Playlist, Album, list]:
            raise TypeError(item)

        if isinstance(item, list):
            for elem in item:
                if not isinstance(elem, Track):
                    raise TypeError(elem)

        self._item = item

        # Validate offset, ignore if item is an artist
        if isinstance(item, Artist):
            self._offset = None
            return

        if isinstance(offset, int):
            if offset < 0 or offset >= len(item):
                raise ValueError(offset)

            self._offset = offset

        elif isinstance(offset, Track):
            if offset not in item:
                raise ValueError(offset)

            # Get the index for offset
            counter = 0
            while counter < len(item):
                if item[counter] == offset:
                    self._offset = counter
                    break # Make sure to return first occurrence of offset
                counter += 1

        else:
            raise TypeError(offset)


    def __str__(self):
        format_str = 'Context obj with item <%s> and offset <%s>'
        return format_str % (str(self._item), str(self._offset))


    def __repr__(self):
        return str(self)


    # TODO: can I check if the hash codes are the same?
    def __eq__(self, other):
        """
        for self == other,
        if both items are playlists or albums, then:
            self.item() == other.item() and self.offset() == other.offset()
        if both are artists, then:
            self.item() == other.item()
        if both are lists, then:
            each elem in the lists must be equivalent and
            self.offset() == other.offset()
        """
        #pylint: disable=unidiomatic-typecheck
        # Check type equivalence
        if type(self) != type(other) or type(self._item) != type(other._item):
            return False

        # Check item equivalence
        if isinstance(self._item, list):
            if len(self._item) != len(other._item):
                return False
            for counter in range(len(self._item)):
                if self._item[counter] != other._item[counter]:
                    return False

        elif self._item != other._item:
            return False

        # Check offset equivalence
        if not isinstance(self, Artist) and self._offset != other._offset:
            return False

        return True


    def __ne__(self, other):
        return not self == other


    def item(self):
        """ Get the item for this context

        Returns:
            The item passed into the constructor. One of:
                Artist
                Playlist
                Album
                List[Tracks]
        """
        return self._item


    def offset(self):
        """ The offset into item where the current playback is.

        Returns:
            None if item is an Artist object
            A non-negative integer < len(item) otherwise
        """
        return self._offset

#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.playlist import Playlist
from spotifython.track import Track
