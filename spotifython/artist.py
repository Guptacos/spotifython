from album import Album
from track import Track
from copy import deepcopy

class Artist:
    # User should never call this constructor. As a result, they should never
    # have access to the artist_info structure prior to creating an Artist.
    def __init__(self, artist_info: dict):
        self._raw = artist_info
        # External url: unsupported object -> leave alone for now
        # Followers: unsupported object -> leave alone for now
        self.genres = artist_info.get("genres", []) # List[str]
        self.href = artist_info.get("href", None) # str
        self.id = artist_info.get("id", None) # str
        # Images: unsupported object -> leave alone for now
        self.name = artist_info.get("name", None) # str
        self.popularity = artist_info.get("popularity", None) # int
        # type: is an artist. we don't need to include this.
        self.uri = artist_info.get("uri", None) # str

        # Results of API calls
        self.albums = None # Lazily load
        self.top_tracks = None # Lazily load
        self.related_artists = None # Lazily load

    # API Calls
    # return <field> if <field> else <make API call and populate field>
    def albums(self, 
        include_groups: str = None,
        country: str = None,
        limit: int = None,
        offset: int = None
    ) -> List[Album]:
        return self.albums
    
    def top_tracks(self,
        country: str = "from_token"
    ) -> List[Track]:
        return self.top_tracks
    
    def related_artists(self) -> List[Artist]:
        return self.related_artists