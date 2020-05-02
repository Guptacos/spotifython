from user import User
from track import Track
from copy import deepcopy
from typing import Union, List

# objects created in this constructor
class Playlist:
    """
    A Playlist object.

    Raises TypeError for incorrect types and ValueError for inappropriate
    values.
    """

    # GET https://api.spotify.com/v1/playlists/{playlist_id}
    def __init__(self, playlist_info: dict):
        """
        Playlist constructor that should never be called directly.
        """
        self._raw = deepcopy(playlist_info)
        self._owner = User(playlist_info.get('owner', {}))
        self._tracks = []
        tracks = playlist_info.get('tracks', {})
        if tracks:
            for item in tracks.get('items', []):
                self._tracks.append(Track(item.get('track', {})))
        

    # POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    def add_tracks(self, track: Union[Track, List[Track]], position: int=None):
        """
        Add one or more tracks to the playlist.

        Parameters:
        tracks:   A Track object or list of Track objects to be added.

        Optional Parameters:
        position: An integer specifying the 0-indexed position in the playlist
                  to insert tracks. Position can be omitted to append to the
                  playlist instead.

        Returns:
        A Response object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}
    def update_name(self, name: str):
        """
        Update the playlist name.

        Parameters:
        name: A string containing the new name of this playlist.

        Returns:
        A Response object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}
    def update_description(self, description: str):
        """
        Update the playlist description.

        Parameters:
        description: A string containing the new description of this playlist.

        Returns:
        A Response object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}
    def update_visibility(self, visibility: str):
        """
        Update the playlist public/private visibility and collaborative access.

        Parameters:
        visibility: A Visibility enum containing the new visibility of this
                    playlist.

        Returns:
        A Response object.
        """
        pass

    # TODO test the response from this endpoint and clarify usage
    # GET https://api.spotify.com/v1/playlists/{playlist_id}/images
    def image(self):
        """
        Return the playlist cover image.

        Returns:
        A Response object containing the cover image url as a string.
        """
        pass

    # GET https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    def tracks(self, start: int=0, num_tracks: int=None):
        """
        Return one or more tracks in the playlist.

        Returns the specified number of tracks in the playlist starting at the
        given position. Returns all of the tracks in the playlist when given no
        parameters.

        Optional Parameters:
        start:      An integer specifying the 0-indexed position of the first
                    track to return. Can be omitted to return tracks starting
                    from the first song in the playlist.

        num_tracks: An integer specifying the number of tracks to return. Can
                    be omitted to return as many tracks as are present at
                    start.

        Returns:
        A Response object containing a list of Track objects.
        """
        pass

    # TODO test this in practice, what does it actually mean? Nobody knows.
    # DELETE https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    def remove_tracks(self, tracks: Union[Track, List[Track]]=None, positions:
                      Union[int, List[int]]=None):
        """
        Remove one or more tracks from the playlist.

        When provided with a list of tracks, all occurrences of those tracks in
        the playlist will be removed. Providing a list of track positions will
        only remove the tracks in those positions from the playlist. No tracks
        will be removed if neither of the parameters are provided. If both
        parameters are provided, positions takes precedence.

        Optional Parameters:
        tracks:    A list of Track objects to be removed from the playlist. All
                   occurrences of these tracks will be removed.

        positions: A list of integers specifying the 0-indexed positions of
                   tracks to be removed from the playlist. Only tracks in these
                   positions will be removed.

        Returns:
        A Response object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    def reorder_tracks(self, source_index, destination_index, number=1):
        """
        Move one or more tracks to another position in the playlist.

        Moves the specified number of tracks starting at source_index to before
        the track currently at destination_index. If number is unspecified,
        only one track is moved.

        Parameters:
        source_index:      An integer specifying the 0-indexed position of the first
                           track to be moved. A negative integer will be evaluated 
                           from the end of the playlist as negative indices behave in
                           lists. This must be a valid index into a list of length
                           len(playlist).

        destination_index: An integer specifying the 0-indexed position of the track
                           before which the other tracks will be moved. A negative
                           integer will be evaluated from the end of the playlist as
                           negative indices behave in lists. This must be a valid
                           index into a list of length len(playlist).

        Optional Parameters:
        number:            A nonnegative integer specifying the number of tracks to
                           be moved. Specifying 0 will result in no change to the
                           playlist.

        Returns:
        A Response object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    def replace_all_tracks(self, tracks):
        """
        Replace all of the tracks in the playlist.

        Parameters:
        tracks: A list of Track objects to populate the playlist. These will
                be the only tracks in the playlist.

        Returns:
        A Response object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}/images
    def replace_image(self, image):
        """
        Replace the playlist cover image.

        The image must be a JPEG and can be at most 256 KB in size.

        Parameters:
        image: A string containing the filename of the image to use as the
               playlist cover image. The image must be a JPEG up to 256 KB.

        Returns:
        A Response object.
        """
        pass

    def __str__(self):
        """Return a printable representation of the playlist."""
        return self._raw['name']

    def __len__(self):
        """Return the number of tracks in the playlist."""
        return len(self._raw['tracks']['items'])

    class Visibility(Enum):
        """
        An Enum to describe the three possible playlist visibilities.

        Playlists can be public, private but not collaborative, and private and
        collaborative. Playlists cannot be collaborative without also being
        private.
        """

        PUBLIC = 1
        PRIVATE = 2
        COLLABORATIVE = 3
