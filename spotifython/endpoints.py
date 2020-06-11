""" Container for the Spotify API endpoints.

This class should not be used by the client.
"""

#pylint: disable=missing-class-docstring, too-few-public-methods
class Endpoints:
    BASE_URI = 'https://api.spotify.com/v1/'

    # Search
    SEARCH = 'search'
    SEARCH_GET_ALBUMS = 'albums'
    SEARCH_GET_ARTISTS = 'artists'
    SEARCH_GET_TRACKS = 'tracks'
    SEARCH_GET_USER = 'users/%s'
    SEARCH_CURRENT_USER = 'me'
    SEARCH_GET_PLAYLIST = 'playlists/%s'

    # Artist
    ARTIST_GET_DATA = 'artists/%s'
    ARTIST_GET_ALBUMS = ARTIST_GET_DATA + '/albums'
    ARTIST_TOP_TRACKS = ARTIST_GET_DATA + '/top-tracks'
    ARTIST_RELATED_ARTISTS = ARTIST_GET_DATA + '/related-artists'

    # Playlist
    PLAYLIST = 'playlists/%s'
    PLAYLIST_TRACKS = PLAYLIST + '/tracks'
    PLAYLIST_IMAGES = '/images'

    # User
    USER_GET_DATA = 'users/%s'
    USER_TOP = 'me/top/%s'
    USER_RECENTLY_PLAYED = 'me/player/recently-played'
    USER_GET_ARTISTS = 'me/following'
    USER_FOLLOWING_CONTAINS = 'me/following/contains'
    USER_HAS_SAVED = 'me/%s/contains' # One of 'albums' or 'tracks'
    USER_GET_SAVED = 'me/%s'
    USER_FOLLOW_ARTIST_USER = 'me/following'
    USER_SAVE_TRACKS = 'me/tracks'
    USER_SAVE_ALBUMS = 'me/albums'
    USER_FOLLOW_PLAYLIST = 'playlists/%s/followers'
    USER_GET_PLAYLISTS = 'users/%s/playlists'
    USER_CREATE_PLAYLIST = 'users/%s/playlists'

    # Player
    PLAYER = 'me/player' # GET request
    PLAYER_GET_DATA = PLAYER
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
    TRACK_GET_DATA = 'tracks/%s'
    TRACK_FEATURES = 'audio-features/%s'
    TRACK_ANALYSIS = 'audio-analysis/%s'

    # Album
    ALBUM_GET_DATA = 'albums/%s'
    ALBUM_GET_TRACKS = ALBUM_GET_DATA + '/tracks'
