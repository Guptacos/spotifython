from user import User
from track import Track
from copy import deepcopy

# TODO should we clarify that indices need to be less than len
# TODO convenience methods like str and len?
# objects created in this constructor
class Playlist:
    """
    A Playlist object.

    Raises TypeError for incorrect types and ValueError for inappropriate
    values.
    """

    # GET https://api.spotify.com/v1/playlists/{playlist_id}
    def __init__(self, playlist_info):
        """
        Playlist constructor that should never be called directly.
        """
        self._raw = deepcopy(playlist_info)
        playlist_info['owner'] = User(playlist_info['owner'])
        for item in playlist_info['tracks']['items']:
            item['track'] = Track(item['track'])
        

    # POST https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    def add_tracks(self, track, position=None):
        """
        Add one or more tracks to the playlist.

        Parameters:
        tracks:   A list of Track objects to be added.

        Optional Parameters:
        position: An integer specifying the 0-indexed position in the playlist
                  to insert tracks. Position can be omitted to append to the
                  playlist instead.

        Returns:
        A Status object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}
    def update_name(self, name):
        """
        Update the playlist name.

        Parameters:
        name: A string containing the new name.

        Returns:
        A Status object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}
    def update_description(self, description):
        """
        Update the playlist description.

        Parameters:
        description: A string containing the new description.

        Returns:
        A Status object.
        """
        pass

    # PUT https://api.spotify.com/v1/playlists/{playlist_id}
    # TODO enum: private+collaborative, private+not collaborative, public
    def update_visibility(self, public, collaborative=False):
        """
        Update the playlist public/private visibility and collaborative access.

        Parameters:
        public:        A boolean value marking the playlist as public. Set to
                       False to mark the playlist as private.

        Optional Parameters:
        collaborative: A boolean value marking the playlist as collaborative.
                       A playlist can be collaborative only if it is not public.

        Returns:
        A Status object.
        """
        pass

    # GET https://api.spotify.com/v1/playlists/{playlist_id}/images
    def image(self):
        """
        Return the playlist cover image.

        Returns:
        A Status object containing the cover image url as a string.
        """
        pass

    # GET https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    # TODO num_tracks should be None - implying there is no limit
    def tracks(self, start=0, num_tracks=-1):
        """
        Return one or more tracks in the playlist.

        Returns the specified number of tracks in the playlist starting at the
        given position. Returns all of the tracks in the playlist when given no
        parameters.

        Optional Parameters:
        start: An integer specifying the 0-indexed position of the first
                  track to return. Position can be omitted to return tracks
                  starting with the first song in the playlist.
        num_tracks:    An integer specifying the number of tracks to return. Limit
                  can be omitted to return as many tracks as are present at
                  the start position.

        Returns:
        A Status object containing a list of Track objects.
        """
        pass

    # TODO api requires track position and track but shouldnt need both
    # TODO should parameter information repeat general function information
    # DELETE https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    # TODO test this in practice, what does it actually mean? Nobody knows.
    def remove_tracks(self, tracks=None, positions=None):
        """
        Remove one or more tracks from the playlist.

        When provided with a list of tracks, all occurrences of those tracks in
        the playlist will be removed. Providing a list of track positions will
        only remove the tracks in those positions from the playlist. No tracks
        will be removed if neither of the parameters are provided.

        Optional Parameters:
        tracks:    A list of Track objects to be removed from the playlist. All
                   occurrences of these tracks will be removed.
        positions: A list of integers specifying the 0-indexed positions of
                   tracks to be remoed from the playlist. Only tracks in these
                   positions will be removed.

        Returns:
        A Status object.
        """
        pass

    # TODO parameter naming
    # TODO how to describe negative integer behavior
    # PUT https://api.spotify.com/v1/playlists/{playlist_id}/tracks
    def reorder_tracks(self, src_index, dest_index, number=1):
        """
        Move one or more tracks to another position in the playlist.

        Moves the specified number of tracks starting at src_index to before the
        track currently at destination. If number is unspecified, only one
        track is moved.

        Parameters:
        src_index:   An integer specifying the 0-indexed position of the first
                     track to be moved. A negative integer will be evaluated 
                     from the end of the playlist as negative indices behave in
                     lists. This must be a valid index into a list of length
                     len(playlist).
        dest_index:  An integer specifying the 0-indexed position of the track
                     before which the other tracks will be moved. A negative
                     integer will be evaluated from the end of the playlist as
                     negative indices behave in lists. This must be a valid
                     index into a list of length len(playlist).

        Optional Parameters:
        number:      A nonnegative integer specifying the number of tracks to
                     be moved. Specifying 0 will result in no change to the
                     playlist.

        Returns:
        A Status object.
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
        A Status object.
        """
        pass

    # TODO hard limit of 256 KB - we need to tell the user hard limits
    # TODO the api wants a base64 encoded jpeg - should we just have filename
    # and should we convert for them
    # PUT https://api.spotify.com/v1/playlists/{playlist_id}/images
    def replace_image(self, image):
        """
        Replace the playlist cover image.

        Parameters:
        image: A string containing the filename of the image to use as the
               playlist cover image. The image must be a JPEG.

        Returns:
        A Status object.
        """
        pass

    def __str__(self):
        """Return a printable representation of the playlist."""
        return self._raw['name']

    def __len__(self):
        """Return the number of tracks in the playlist."""
        return len(self._raw['tracks']['items'])
