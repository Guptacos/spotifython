# This class is used to interact with the current user's player. This
# includes things such as pausing / playing the current song, modifying the
# queue, etc.
# TODO: is it pythonic to underscore a class?
# @param deviceId=None: the device to target. If none given, will use the
#       currently active device. Applies in any of these functions where
#       deviceId is optional.
class Player():
    
    # TODO: should params be passed in to optionally fill in some values? Also name
    def __init__(self, userId, knownVals=None):
        pass
        
    # TODO: what should the string represent?
    def __str__(self):
        pass

    # TODO: how is this different than __str__?
    def __repr__(self):
        pass
    
    # TODO: what if nothing playing?
    # Takes extra params??
    def pause(self, deviceId=None):
        # PUT /v1/me/player/pause
        pass

    # TODO: what if already playing?
    # Takes extra params??
    def resume(self, deviceId=None):
        # PUT /v1/me/player/play
        pass

    def set_playing
    def get_active_device
    def get_shuffle
    def get_seek
    def get_volume
    def get_repeat

    # TODO: should name be 'skip' or something else??
    def next(self, deviceId=None):
        # POST /v1/me/player/next
        pass

    def previous(self, deviceId=None):
        # POST /v1/me/player/previous

    # TODO: no enum, cleave method
    # @param mode: one of sp.TRACK, sp.CONTEXT, sp.OFF
    def setRepeat(self, mode, deviceId=None):
        # PUT /v1/me/player/repeat
        pass

    # @param play: if True, ensure playback starts on the new device.
    #              if False, keep the current playback state.
    # TODO: Remove Spotify defaults everywhere
    # TODO: snake_case
    # Previously 'transfer_playback...'
    def set_active_device(self, deviceId, forcePlay=False):
        # PUT /v1/me/player
        pass

    # TODO: in the future, add 'additionalTypes' to support episodes.
    # @param market: a 2 letter country code as defined here:
    #       https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    #       Used for track relinking:
    #       https://developer.spotify.com/documentation/general/guides/track-relinking-guide/
    #       if 'from_token' (default) is given, will use appropriate country
    #       code for user based on their auth token and location.
    # TODO: previously currently_playing
    def get_playing(self, market='from_token'):
        # GET /v1/me/player/currently-playing
        pass

    # TODO: there is a lot of info in here........
    # TODO: for any setter method, make corresponding getter. Ignore rest.
    def getPlayer(self):
        # GET /v1/me/player
        ''' return json structure
        device {}
            id (str)
            is_active (bool)
            is_private_session (bool)
            is_restricted (bool)
            name (str)
            type (str)
                Computer, Tablet, Smartphone, Speaker, TV, AVR, STB,
                AudioDongle, GameConsole, CastVideo, CastAudio, Automobile,
                Unknown
            volume_percent (int)
        shuffle_state (bool)
        repeat_state (str: 'track', 'context', 'off')
        timestamp (int: I think epoch time of last play/pause)
        context (str: 'the context the song was played from'???)
        progress_ms (int: time in cur song)
        currently_playing_type (str: track, artist, etc.)
        actions {}
            disallows {}
                (str : bool). If bool true, action not allowed to be done.
                May be due to account restrictions, token restrictions, or
                current playback state. I.e. if song is playing, 'resuming'
                is disallowed, if on a song radio, 'repeat' is disallowed.
            maybe some others???
        is_playing (bool)
        item {}
            album {} an album object
            artists [{}] a list of artist objects
            disc_number (int)
            duration_ms (int)
            explicit (bool)
            external_ids ??
            external_urls ??
            href ??
            id (str: I think the item id)
            is_local (bool: ??)
            is_playable (bool: ??)
            name (str: item name)
            popularity (int: ??)
            preview_url (str: ??)
            track_number (int)
            type (str: track, artist, etc.)
            uri (str: ??)
        '''
        pass

    # @param position: position in ms of the current song to go to.
    #       Must be positive.
    #       If greater than the len of the track, will play the next song.
    # TODO: name is whack?
    def set_seek(self, position, deviceId=None):
        # PUT /v1/me/player/seek
        pass

    # @param volume: volume percent as int from 0 to 100 inclusive.
    def setVolume(self, volume, deviceId=None):
        # PUT /v1/me/player/volume
        pass

    # TODO: maybe don't name get?
    # @param limit: max number of items to return. Max 50.
    # @param after: Unix time stamp in ms (int). Return songs after
    #       (exclusive) this timestamp.
    # @param before: Unix time stamp in ms (int). Return songs before
    #       (exclusive) this timestamp.
    # @note: you cannot filter using BOTH after and before at the same time.
    # TODO: what to do with after and before? Should we remove?
    # TODO: Should we use time module?
    def recentlyPlayed(self, limit=50, after=None, before=None):
        # GET /v1/me/player/recently-played
        pass

    # TODO: may need a separate device abstraction
    # For now, return device Id
    def availableDevices(self):
        # GET /v1/me/player/devices
        pass

    # @param state: True to set shuffle to on, False to set it to off.
    def setShuffle(self, shuffleState):
        # PUT /v1/me/player/shuffle
        pass

    # @param uri: the uri of the item to add. Can only be a Track or an
    #       Episode.... Should we allow input of a Track object? Why can't
    #       we add albums?? TODO
    # TODO: Allow Track or Album as input, iterate album and hit endpoint
    def enqueue(self, uri, deviceId=None):
        # POST /v1/me/player/queue
        pass
