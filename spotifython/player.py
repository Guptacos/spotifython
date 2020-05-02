from album import Album
from artist import Artist
from playlist import Playlist
from track import Track
from user import User

from response import Response
from typing import Union

class Player():
    ''' Interact with a user's playback, such as pausing / playing the current
        song, modifying the queue, etc.

    Getting an instance of Player should only be done using User.player()

    Shared keyword arguments:
        device_id: the device the command should target. The given device must
            be a device listed in player.available_devices() or an error will be
            returned.

            Defaults to using the currently active device, which is what you
            will want most of the time.

        position: always an integer that represents milliseconds.

    Errors:
        Many of these methods will do nothing if there is no active or available
        device. You should check response.status() to see if that was the case.

    Note:
        Due to the asynchronous nature of many Player commands, you should use
        the Player's getter methods to check that your issued command was
        handled correctly by the player.
    '''

    
    def __init__(self,
                 user: User
        ) -> Player:
        ''' Should only be called from within the User class
        
        Keyword arguments:
            user: the User object that created the Player. For example, User can
                say self._player = Player(self)

        Return:
            A Player object
        '''
        pass


    # Format should be 'Player for user <%s>' with user_id
    def __str__(self) -> str:
        return ''

    
    def next(self,
             device_id: str=None
        ) -> Response:
        ''' Skip the current song in the playback

        response.contents():
            None
        '''
        # POST /v1/me/player/next
        pass


    def previous(self,
                 device_id: str=None
        ) -> Response:
        ''' Skip to the previous song in the playback, regardless of where in
            the current song playback is.

        response.contents():
            None
        '''
        # POST /v1/me/player/previous


    # Note for me: if nothing playing and pause, raises 403 restriction violated
    def pause(self,
              device_id: str=None
        ) -> Response:
        ''' Pause the current playback

        response.contents():
            None
        '''
        # PUT /v1/me/player/pause
        pass


    # Note for me: if playing and resume, raises 403 restriction violated
    def resume(self,
               device_id: str=None
        ) -> Response:
        ''' Resume the current playback

        response.contents():
            None
        '''
        # PUT /v1/me/player/play
        pass


    # Future support: inputing a context object
    # Future support: offsetting into context
    # Future support: position in track
    def play(self,
             item: Union[Track, Album, Playlist, Artist],
             device_id: str=None
        ) -> Response:
        ''' Change the current track and context for the player

        Uses the currently active device, if one exists.

        Keyword arguments:
            item: an instance of sp.Track, sp.Album, sp.Playlist, or sp.Artist.
                to begin playing.

        Note: Does not currently support playing a specific context, or an
            offset into a playlist, album, or artist. Also does not support
            starting playback at a position in the track, playback will start at
            the beginning of the track.

        response.contents():
            None
        '''
        # PUT /v1/me/player/play
        pass


    def is_paused(self) -> Response:
        ''' Check if the current playback is paused

        Uses the currently active device, if one exists.

        response.contents():
            Success: True if paused, else False
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def is_playing(self) -> Response:
        ''' Check if the current playback is playing (not paused)

        Uses the currently active device, if one exists.

        response.contents():
            Success: True if playing, else False
            Failure: None
        '''
        # GET /v1/me/player
        pass


    # TODO: This method name is not final. Here are alternatives we considered:
    # get_currently_playing
    # now_playing
    # get_active_audio
    # Note for me: in the future, add 'additional_types' to support episodes.
    # Note for me: in the future support returning a context object
    def get_currently_playing(self,
                              market: str='from_token'
        ) -> Response:
        ''' Get the currently playing track in the playback

        Uses the currently active device, if one exists.

        Keyword arguments:
            market: a 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                if 'from_token' (default) is given, will use appropriate country
                code for user based on their auth token and location.

        response.contents():
            Success: a Track object
            Failure: None
        '''
        # GET /v1/me/player/currently-playing
        pass


    # Note for me: in the future add a separate device abstraction
    def available_devices(self) -> Response:
        ''' Get all devices currently available

        response.contents():
            Success: A list of strings, where each is a device id.
            Failure: None
        '''
        # GET /v1/me/player/devices
        pass


    def get_active_device(self) -> Response:
        ''' Get the currently active device

        response.contents():
            Success: The device id of the active device, if a device is active.
            Failure: None
        '''
        # GET /v1/me/player
        pass


    # TODO: random boolean flag? set_active_device(id, True) isn't clear
    def set_active_device(self,
                          device_id: str,
                          force_play: bool=False
        ) -> Response:
        ''' Transfer playback to a different available device

        Keword arguments:
            force_play: True: resume playback after transfering to new device
                        False: keep the current playback state.

        response.contents():
            None
        '''
        # PUT /v1/me/player
        pass


    def get_shuffle(self) -> Response:
        ''' Get the current shuffle state of the playback

        Uses the currently active device, if one exists.

        response.contents():
            Success: True if shuffle is enabled else False
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_shuffle(self,
                    shuffle_state: bool,
                    device_id: str=None
        ) -> Response:
        ''' Set the shuffle state of the active device

        Keyword arguments:
            shuffle_state: True to set shuffle to on, False to set it to off.

        response.contents():
            None
        '''
        # PUT /v1/me/player/shuffle
        pass


    # TODO: naming. what is a seek?
    def get_seek(self) -> Response:
        ''' Get the current position in the currently playing track in ms

        Uses the currently active device, if one exists.

        response.contents():
            Success: the position (in ms) as an int
            Failure: None
        '''
        # GET /v1/me/player
        pass


    # TODO: naming. what is a seek?
    def set_seek(self,
                 position: int,
                 device_id: str=None
        ) -> Response:
        ''' Set the current position in the currently playing track in ms

        Keyword arguments:
            position: the position (in ms) as an int. Must be non-negative.
                If greater than the len of the track, will play the next song.

        response.contents():
            None
        '''
        # PUT /v1/me/player/seek
        pass


    def get_volume(self) -> Response:
        ''' Get the current volume for the playback

        Uses the currently active device, if one exists.

        response.contents():
            Success: the volume (in percent) as an int from 0 to 100 inclusive
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_volume(self,
                   volume: int,
                   device_id: str=None
        ) -> Response:
        ''' Set the current volume for the playback

        Keyword arguments:
            volume: the volume (in percent) as an int from 0 to 100 inclusive

        response.contents():
            None
        '''
        # PUT /v1/me/player/volume
        pass


    def get_repeat(self) -> Response:
        ''' Get the repeat state for the current playback

        Uses the currently active device, if one exists.

        response.contents():
            Success: one of sp.TRACK, sp.CONTEXT, sp.OFF
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_repeat(self,
                   mode: str,
                   device_id: str=None
        ) -> Response:
        ''' Set the repeat state for the current playback

        Keyword arguments:
            mode: one of
                sp.TRACK: repeat the current track
                sp.CONTEXT: repeat the current context (playlist, album, etc.)
                sp.OFF: turn repeat off

        response.contents():
            None
        '''
        # PUT /v1/me/player/repeat
        pass


    # Note for me: add episodes at some point
    def enqueue(self,
                item: Union[Album, Track],
                device_id: str=None
        ) -> Response:
        ''' Add an item to the end of the queue
        
        Keyword arguments:
            item: the item to add to the queue. Must be an instance of sp.Album
                or sp.Track. Adding playlists to the queue is not currently
                supported.

        response.contents():
            None
        '''
        # POST /v1/me/player/queue
        pass
