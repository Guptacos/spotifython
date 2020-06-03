class Endpoints:
    BASE_URI = 'https://api.spotify.com'

    # Search constants
    SEARCH = '/v1/search'
    SEARCH_GET_ALBUMS = '/v1/albums'
    SEARCH_GET_ARTISTS = '/v1/artists'
    SEARCH_GET_TRACKS = '/v1/tracks'
    SEARCH_GET_USER = '/v1/users/%s'
    SEARCH_GET_CURRENT_USER = '/v1/me'
    SEARCH_GET_PLAYLIST = '/v1/playlists/%s'

    # Artist endpoints
    ARTIST_GET_ALBUMS = '/v1/artists/%s/albums'
    ARTIST_TOP_TRACKS = '/v1/artists/%s/top-tracks'
    ARTIST_RELATED_ARTISTS = '/v1/artists/%s/related-artists'
    ARTIST_GET_BY_ID = '/v1/artists/%s'

    # Playlist
    PLAYLIST = '/v1/playlists/{playlist_id}'
    PLAYLIST_TRACKS = '/v1/playlists/{playlist_id}/tracks'
    PLAYLIST_IMAGES = '/v1/playlists/{playlist_id}/images'

    # User
    USER_TOP = '/v1/me/top/%s'
    USER_RECENTLY_PLAYED = '/v1/me/player/recently-played'
    USER_GET_PLAYLISTS = '/v1/users/%s/playlists'
    USER_CREATE_PLAYLIST = '/v1/users/%s/playlists'
    USER_GET_ARTISTS = '/v1/me/following'
    USER_FOLLOWING_CONTAINS = '/v1/me/following/contains'
    # One of 'albums' or 'tracks'
    USER_HAS_SAVED = '/v1/me/%s/contains'
    USER_GET_SAVED = '/v1/me/%s'
    USER_FOLLOW_ARTIST_USER = '/v1/me/following'
    USER_FOLLOW_PLAYLIST = '/v1/playlists/%s/followers'
    USER_SAVE_TRACKS = '/v1/me/tracks'
    USER_SAVE_ALBUMS = '/v1/me/albums'

    # Player
    PLAYER = '/v1/me/player'
    PLAYER_GET_DATA = PLAYER
    PLAYER_SKIP = PLAYER + '/next'
    PLAYER_PREVIOUS = PLAYER + '/previous'
    PLAYER_PAUSE = PLAYER + '/pause'
    PLAYER_PLAY = PLAYER + '/play'
    PLAYER_AVAILABLE_DEVICES = PLAYER + '/devices'
    PLAYER_TRANSFER = PLAYER
    PLAYER_SHUFFLE = PLAYER + '/shuffle'
    PLAYER_SEEK = PLAYER + '/seek'
    PLAYER_VOLUME = PLAYER + '/volume'
    PLAYER_REPEAT = PLAYER + '/repeat'
    PLAYER_QUEUE = PLAYER + '/queue'

    # Track
    TRACK_GET_DATA = '/v1/tracks/%s'
    TRACK_FEATURES = '/v1/audio-features/%s'
    TRACK_ANALYSIS = '/v1/audio-analysis/%s'
