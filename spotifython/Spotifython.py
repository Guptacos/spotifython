from response import *

# This object should be constructed by the user to instantiate the 
# session of Spotify Web API usage.
class Spotifython:
    
    def __init__(self, token, timeout=None):
        self.token = token
        self.timeout = timeout
    
    # User should never call this constructor. As a result, they should never
    # have access to the search_info structure prior to creating an SearchResult.
    class SearchResult:

        # Each category of search result from a query is kept within a paging object
        # User should never call this constructor. As a result, they should never
        # have access to the paging_info structure prior to creating an SearchPage.
        class SearchPage:
            def __init__(self, paging_info: dict):
                self._raw = paging_info
                self.href = paging_info.get("href", None) # str
                self.items = paging_info.get("items", list()) # List[]
                self.limit = paging_info.get("limit", None) # int
                self.next = paging_info.get("next", None) # str
                self.offset = paging_info.get("offset", None) # int
                self.previous = paging_info.get("previous", None) # str
                self.total = paging_info.get("total", None) # int

        def __init__(self, search_info: dict):
            self._raw = search_info
            self._albums_paging = SearchPage(search_info.get("albums", dict()))
            self._artists_paging = SearchPage(search_info.get("artists", dict()))
            self._playlists_paging = SearchPage(search_info.get("playlists", dict()))
            self._tracks_paging = SearchPage(search_info.get("tracks", dict()))
        
        # TODO: How to maintain pagination within our objects? The Web API uses offset in conjunction
        # with limit to get the next page of search results.
        def albums(self) -> List[Album]:
            return self._albums_paging.get("items", list())

        def artists(self) -> List[Artist]:
            return self._artists_paging.get("items", list())

        def playlists(self) -> List[Playlist]:
            return self._playlists_paging.get("items", list())
        
        def tracks(self) -> List[Track]:
            return self._tracks_paging.get("items", list())
        
    def search(self, 
        name: str, 
        type: List[str], 
        market: str = None,
        limit: int = None,
        offset: int = None,
        include_external: str = None
    ) -> SearchResult:
        # Don't forget to encode the spaces in strings!
        # See guidelines in Search -> "Writing a Query - Guidelines" 
        # for more specification details that need to be implemented.
        return SearchResult(dict())

    def get_albums(self, 
        album_id: Union[str, List[str]], # If list, is comma separated
        market: str = None
    ) -> Union[Album, List[Album]]:
        return None
    
    def get_artists(self, 
        artist_id: Union[str, List[str]] # If list, is comma separated
    ) -> Union[Artist, List[Artist]]:
        return None

    def get_tracks(self, 
        track_id: Union[str, List[str]], # If list, is comma separated
        market: str = None
    ) -> Union[Track, List[Track]]:
        return None
    
    def get_user(self, 
        user_id: str
    ) -> User:
        return None
    
    def get_current_user(self) -> User:
        return None
    
    def get_playlist(self,
        fields: str = None, # Complicated object - leave the parsing to the client
        market: str = None,
        additional_types: List[str] = None # Comma separated list
    ) -> Playlist:
        return None