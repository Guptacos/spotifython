# import endpoint
# endpoint.BASE_URI
class Endpoints:
    BASE_URI = 'https://api.spotify.com'
    GET_ALBUMS = '/v1/artists/{id}/albums'

    # User
    USER_TOP = '/v1/me/top/%s'
    USER_RECENTLY_PLAYED = '/v1/me/player/recently-played'
    USER_GET_PLAYLISTS = '/v1/users/%s/playlists'

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
