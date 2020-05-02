# TODO: many of the modify / read methods can error out if no active device
# TODO: which methods need a device_id param or other extra params?
# TODO: need to define error handling for when there is no active device
# TODO: Remove Spotify defaults everywhere
# TODO: mention that all time is in ms
# TODO: return values
# TODO: type hints
# TODO: due to async nature, may need to check getters for true success
# TODO: when None is returned, check status code for success / failure. Could be
#       due to no active device
# TODO: is device_id really needed?
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
    '''

    
    def __init__(self, user):
        ''' Should only be called from within the User class
        
        Keyword arguments:
            user: the User object that created the Player. For example, User can
                say self._player = Player(self)
        '''
        pass


    # Format should be 'Player for user <%s>' with user_id
    def __str__(self):
        return ''

    
    def next(self, device_id=None):
        ''' Skip the current song in the playback

        Return:
            None
        '''
        # POST /v1/me/player/next
        pass


    def previous(self, device_id=None):
        ''' Skip to the previous song in the playback, regardless of where in
            the current song playback is.

        Return:
            None
        '''
        # POST /v1/me/player/previous


    # Note for me: if nothing playing and pause, raises 403 restriction violated
    def pause(self, device_id=None):
        ''' Pause the current playback

        Return:
            None
        '''
        # PUT /v1/me/player/pause
        pass


    # Note for me: if playing and resume, raises 403 restriction violated
    def resume(self, device_id=None):
        ''' Resume the current playback

        Return:
            None '''
        # PUT /v1/me/player/play
        pass


    # TODO: context, more complicated
    # TODO: device id?
    def play(self, item, context):
        ''' Change the current track and context for the player

        Uses the currently active device, if one exists.

        Return:
            None
        '''
        # PUT /v1/me/player/play
        pass


    def is_paused(self):
        ''' Check if the current playback is paused

        Uses the currently active device, if one exists.

        Return:
            Success: True if paused, else False
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def is_playing(self):
        ''' Check if the current playback is playing (not paused)

        Uses the currently active device, if one exists.

        Return:
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
    # TODO: context
    def get_currently_playing(self, market='from_token'):
        ''' Get the currently playing track in the playback

        Uses the currently active device, if one exists.

        Keyword arguments:
            market: a 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                if 'from_token' (default) is given, will use appropriate country
                code for user based on their auth token and location.

        Return:
            Success: a Track object
            Failure: None
        '''
        # GET /v1/me/player/currently-playing
        pass


    # Note for me: in the future add a separate device abstraction
    def available_devices(self):
        ''' Get all devices currently available

        Return:
            Success: A list of strings, where each is a device id.
            Failure: None
        '''
        # GET /v1/me/player/devices
        pass


    def get_active_device(self):
        ''' Get the currently active device

        Return:
            Success: The device id of the active device, if a device is active.
            Failure: None
        '''
        # GET /v1/me/player
        pass


    # TODO: random boolean flag?
    def set_active_device(self, device_id, force_play=False):
        ''' Transfer playback to a different available device

        Keword arguments:
            force_play: True: resume playback after transfering to new device
                        False: keep the current playback state.

        Return:
            None
        '''
        # PUT /v1/me/player
        pass


    def get_shuffle(self):
        ''' Get the current shuffle state of the playback

        Uses the currently active device, if one exists.

        Return:
            Success: True if shuffle is enabled else False
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_shuffle(self, shuffle_state, device_id=None):
        ''' Set the shuffle state of the active device

        Keyword arguments:
            shuffle_state: True to set shuffle to on, False to set it to off.

        Return:
            None
        '''
        # PUT /v1/me/player/shuffle
        pass


    # TODO: naming
    def get_seek(self):
        ''' Get the current position in the currently playing track in ms

        Uses the currently active device, if one exists.

        Return:
            Success: the position (in ms) as an int
            Failure: None
        '''
        # GET /v1/me/player
        pass


    # TODO: naming
    def set_seek(self, position, device_id=None):
        ''' Set the current position in the currently playing track in ms

        Keyword arguments:
            position: the position (in ms) as an int. Must be non-negative.
                If greater than the len of the track, will play the next song.

        Return:
            None
        '''
        # PUT /v1/me/player/seek
        pass


    def get_volume(self):
        ''' Get the current volume for the playback

        Uses the currently active device, if one exists.

        Return:
            Success: the volume (in percent) as an int from 0 to 100 inclusive
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_volume(self, volume, device_id=None):
        ''' Set the current volume for the playback

        Keyword arguments:
            volume: the volume (in percent) as an int from 0 to 100 inclusive

        Return:
            None
        '''
        # PUT /v1/me/player/volume
        pass


    def get_repeat(self):
        ''' Get the repeat state for the current playback

        Uses the currently active device, if one exists.

        Return:
            Success: one of sp.TRACK, sp.CONTEXT, sp.OFF
            Failure: None
        '''
        # GET /v1/me/player
        pass


    def set_repeat(self, mode, device_id=None):
        ''' Set the repeat state for the current playback

        Keyword arguments:
            mode: one of
                sp.TRACK: repeat the current track
                sp.CONTEXT: repeat the current context (playlist, album, etc.)
                sp.OFF: turn repeat off

        Return:
            None
        '''
        # PUT /v1/me/player/repeat
        pass


    # Note for me: add episodes at some point
    def enqueue(self, item, device_id=None):
        ''' Add an item to the end of the queue
        
        Keyword arguments:
            item: the item to add to the queue. Must be an instance of sp.Album
                or sp.Track. Adding playlists to the queue is not currently
                supported.

        Return:
            None
        '''
        # POST /v1/me/player/queue
        pass
