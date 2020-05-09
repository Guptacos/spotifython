# import endpoint
# endpoint.BASE_URI
class Endpoints:
    BASE_URI = 'https://api.spotify.com'
    GET_ALBUMS = '/v1/artists/{id}/albums'
    PLAYLIST =  '/v1/playlists/{playlist_id}'
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
