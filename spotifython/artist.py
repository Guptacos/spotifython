from album import Album
from track import Track
from copy import deepcopy
from response import Response
import spotifython as sp

class Artist:
    # User should never call this constructor. As a result, they should never
    # have access to the artist_info structure prior to creating an Artist.
    def __init__(self, artist_info: dict, top: Spotifython):
        self._top = top
        self._raw = artist_info
        self.albums = None # Lazily load
        self.top_tracks = None # Lazily load
        self.related_artists = None # Lazily load

    ##################################
    # Overloads
    ##################################

    def __str__(self):
        c = self.name()
        return c.contents() if c else 'ERROR'

    ##################################
    # Field accessors
    ##################################

    ### Unsupported objects ###
    # External url: unsupported object
    # Followers: unsupported object
    # Images: unsupported object
    # Type: is an artist. we don't need to include this.

    def genres(self) -> Response: # List[str]
        return Response(status=Response.OK, contents=self._raw.get('genres'))

    def href(self) -> Response: # str
        return Response(status=Response.OK, contents=self._raw.get('href'))
    
    def artist_id(self) -> Response: # str
        return Response(status=Response.OK, contents=self._raw.get('id'))
    
    def name(self) -> Response: # str
        return Response(status=Response.OK, contents=self._raw.get('name'))
    
    def popularity(self) -> Response: # int
        return Response(status=Response.OK, contents=self._raw.get('popularity'))
    
    def uri(self) -> Response: # str
        return Response(status=Response.OK, contents=self._raw.get('uri'))

    ##################################
    # API Calls
    ##################################
    
    def albums(self, 
        search_limit: int = None,
        include_groups: str = None,
        country: str = sp.TOKEN_REGION,
    ) -> Response: # List[Album]
        '''
        Gets the albums associated with the current Spotify artist.
        
        Args:
            search_limit: (Optional) the maximum number of results to return.
            include_groups: (Optional) A comma-separated list of keywords 
                that will be used to filter the response. If not supplied, 
                all album types will be returned. 
                Valid values are: 'album', 'single', 'appears_on', 'compilation' 
            country: (Optional) An ISO 3166-1 alpha-2 country code or the string sp.TOKEN_REGION.
                Supply this parameter to limit the response to one particular geographical 
                market. If this value is None, results will be returned for all countries and you 
                are likely to get duplicate results per album, one for each country in 
                which the album is available!

        Returns: 
            A response object containing a list of Albums if the request succeeded.

        Exceptions:
            TypeError for invalid types in any argument.
        
        Calls endpoints:
            GET	/v1/artists/{id}/albums
        '''

        # search_limit -> limit: int = None, offset: int = None
        # Request: the response body contains an array of simplified album
        # objects (wrapped in a paging object)
        return self.albums
    
    
    def top_tracks(self,
        country: str = sp.TOKEN_REGION,
        search_limit: int = 10,
    ) -> Response: # List[Track]
        '''
        Gets the top tracks associated with the current Spotify artist.
        
        Args:
            country: An ISO 3166-1 alpha-2 country code or the string sp.TOKEN_REGION.
            search_limit: (Optional) the maximum number of results to return.

        Returns: 
            A response object containing a list of Tracks if the request succeeded.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError for invalid country, or if country is None.
            ValueError if search_limit is > 10: this is the Spotify API's search limit.
        
        Calls endpoints:
            GET	/v1/artists/{id}/top-tracks
        '''

        # This search limit is not part of the API, spotify always returns up to 10.
        return self.top_tracks
    
    def related_artists(self,
        search_limit: int = 20,
    ) -> Response: # List[Artist]
        '''
        Gets Spotify catalog information about artists similar to a given artist.

        Args:
            search_limit: (Optional) the maximum number of results to return.

        Returns: 
            A response object containing a list of Artist objects 
            if the request succeeded.

        Exceptions:
            TypeError for invalid types in any argument.
            ValueError if search_limit is > 20: this is the Spotify API's search limit.
        
        Calls endpoints:
            GET	/v1/artists/{id}/related-artists
        '''

        # This search limit is not part of the API, spotify always returns up to 20.
        return self.related_artists