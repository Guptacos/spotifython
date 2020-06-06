class Endpoints:
    BASE_URI = 'https://api.spotify.com'

    # Artist endpoints
    ARTIST_GET_ALBUMS = '/v1/artists/%s/albums'
    ARTIST_TOP_TRACKS = '/v1/artists/%s/top-tracks'
    ARTIST_RELATED_ARTISTS = '/v1/artists/%s/related-artists'
    ARTIST_GET_BY_ID = '/v1/artists/%s'