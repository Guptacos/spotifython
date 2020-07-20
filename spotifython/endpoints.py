""" Container for the Spotify API endpoints.

This class should not be used by the client.
"""

#pylint: disable=missing-class-docstring, too-few-public-methods
class Endpoints:
    BASE_URI = 'https://api.spotify.com/v1/'

    # Search
    SEARCH = 'search'
    SEARCH_ALBUMS = 'albums'
    SEARCH_ARTISTS = 'artists'
    SEARCH_TRACKS = 'tracks'
    SEARCH_USER = 'users/%s'
    SEARCH_CURRENT_USER = 'me'
    SEARCH_PLAYLIST = 'playlists/%s'

    # Artist
    ARTIST_DATA = 'artists/%s'
    ARTIST_ALBUMS = ARTIST_DATA + '/albums'
    ARTIST_TOP_TRACKS = ARTIST_DATA + '/top-tracks'
    ARTIST_RELATED_ARTISTS = ARTIST_DATA + '/related-artists'

    # Playlist
    PLAYLIST = 'playlists/%s'
    PLAYLIST_TRACKS = PLAYLIST + '/tracks'
    PLAYLIST_IMAGES = '/images'

    # User
    USER_DATA = 'users/%s'
    USER_TOP = 'me/top/%s'
    USER_RECENTLY_PLAYED = 'me/player/recently-played'
    USER_ARTISTS = 'me/following'
    USER_FOLLOWING_CONTAINS = 'me/following/contains'
    USER_HAS_SAVED = 'me/%s/contains' # One of 'albums' or 'tracks'
    USER_SAVED = 'me/%s'
    USER_FOLLOW_ARTIST_USER = 'me/following'
    USER_SAVE_TRACKS = 'me/tracks'
    USER_SAVE_ALBUMS = 'me/albums'
    USER_FOLLOW_PLAYLIST = 'playlists/%s/followers'
    USER_PLAYLISTS = 'users/%s/playlists'
    USER_CREATE_PLAYLIST = 'users/%s/playlists'

    # Player
    PLAYER = 'me/player' # GET request
    PLAYER_DATA = PLAYER
    PLAYER_SKIP = PLAYER + '/next'
    PLAYER_PREVIOUS = PLAYER + '/previous'
    PLAYER_PAUSE = PLAYER + '/pause'
    PLAYER_PLAY = PLAYER + '/play'
    PLAYER_AVAILABLE_DEVICES = PLAYER + '/devices'
    PLAYER_TRANSFER = PLAYER # PUT request
    PLAYER_SHUFFLE = PLAYER + '/shuffle'
    PLAYER_SEEK = PLAYER + '/seek'
    PLAYER_VOLUME = PLAYER + '/volume'
    PLAYER_REPEAT = PLAYER + '/repeat'
    PLAYER_QUEUE = PLAYER + '/queue'

    # Track
    TRACK_DATA = 'tracks/%s'
    TRACK_FEATURES = 'audio-features/%s'
    TRACK_ANALYSIS = 'audio-analysis/%s'

    # Album
    ALBUM_DATA = 'albums/%s'
    ALBUM_TRACKS = ALBUM_DATA + '/tracks'
