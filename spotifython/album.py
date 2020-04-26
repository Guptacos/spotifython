from track import Track

class Album:
    def __init__(self, album_info):
        self.album_type = album_info.get('album_type', '')
        self.artists = list()
        for artist in album_info.get('artists', []):
            self.artists.append(Artist(artist))
        self.available_markets = album_info.get('available_markets', [])
        self.id = album_info.get('id', '')
        self.images = album_info.get('images', '')
