class Endpoint:
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

    # Search
    SEARCH = '/v1/search'
    SEARCH_GET_ALBUMS = '/v1/albums'
    SEARCH_GET_ARTISTS = '/v1/artists'
    SEARCH_GET_TRACKS = '/v1/tracks'
    SERACH_GET_USER = '/v1/users/{}'
    SEARCH_GET_CURRENT_USER = '/v1/me'
    SEARCH_GET_PLAYLIST = '/v1/playlists/{}'

# import endpoint
# endpoint.BASE_URI        
