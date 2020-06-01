class Endpoints:
    BASE_URI = 'https://api.spotify.com'
    SEARCH = '/v1/search'

    # Search constants
    SEARCH_GET_ALBUMS = '/v1/albums'
    SEARCH_GET_ARTISTS = '/v1/artists'
    SEARCH_GET_TRACKS = '/v1/tracks'
    SEARCH_GET_USER = '/v1/users/%s'
    SEARCH_GET_CURRENT_USER = '/v1/me'
    SEARCH_GET_PLAYLIST = '/v1/playlists/%s'
