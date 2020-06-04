""" Album class

This class represents an Album object, which represents a Spotify album.
"""

# Standard library imports
import copy

# Local imports
import spotifython.constants as const
from spotifython.endpoints import Endpoints
import spotifython.utils as utils


class Album:
    """ The Album class. Use methods here to get information about an Album.

    Required token scopes:
        None: the methods in the Album class require a token, but the token
            needs no scopes.
    TODO: is this true?
    """


    def __init__(self, session, info):
        """ Get an instance of Album

        This constructor should never be called by the client. To get an
        instance of Album, use Session.get_albums()

        Args:
            session: a Session instance
            info: the album's information
        """
        # Validate inputs
        if 'id' not in info:
            raise ValueError('Album id not in info')

        self._id = info['id']

        self._raw = copy.deepcopy(info)
        self._session = session

        # TODO:?????
        self._iter = 0


    def __str__(self):
        pass


    def __repr__(self):
        pass


    def __eq__(self, other):
        pass


    def __ne__(self, other):
        pass


    def __hash__(self):
        pass


    def __len__(self):
        # return len(self._tracks)
        pass


    # iter and next let you loop through the tracks in the album. len gives you
    # the number of tracks in the album.
    def __iter__(self):
        self._iter = 0
        return self


    def __next__(self):
        # if self._iter < len(self._tracks):
        #     track = self._tracks[self._iter]
        #     self._iter += 1
        #     return track

        # raise StopIteration
        pass


    def __reversed__(self):
        pass


    def __contains__(self, other):
        pass


    def __getitem__(self, key):
        # Should accept negative keys and slice objects
        pass


    def spotify_id(self):
        return self._id


    def type(self):
        pass


    def artists(self):
        # for artist in album_info.get('artists', []):
        #     self._artists.append(Artist(artist))
        # return self._artists
        pass


    def available_markets(self):
        pass


    def copyrights(self):
        pass


    def genres(self):
        pass


    def href(self):
        pass


    def uri(self):
        pass


    def images(self):
        """
        # TODO: usually has three sizes, maybe take in an optional arg for size,
        # otherwise return the first one (largest).
        def image(self, size=None):
            return self._images[0] if size == None else self._images[0]
        """
        pass


    def label(self):
        pass


    def name(self):
        pass


    def popularity(self):
        pass


    def release_date(self):
        pass


    def tracks(self):
        # tracks_wrapper = album_info.get('tracks', None)
        # if tracks_wrapper != None:
        #     self._tracks = list()
        #     for track in tracks_wrapper.get('items', []):
        #         self._tracks.append(Track(track))
        # return self._tracks
        pass


#pylint: disable=wrong-import-position
from spotifython.track import Track
from spotifython.artist import Artist
