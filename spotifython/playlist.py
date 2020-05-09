from __future__ import annotations

from typing import List, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from spotifython import Spotifython
    from album import Album
    from artist import Artist
    from player import Player
    from track import Track
    from user import User

from copy import deepcopy
from endpoint import Endpoint
import base64

# objects created in this constructor
class Playlist:
    """
    A Playlist object.

    Raises TypeError for incorrect types and ValueError for inappropriate
    values.
    """

    def __init__(self, playlist_info: dict, top: Spotifython):
        """
        Playlist constructor that should never be called directly.
        """
        self._raw = deepcopy(playlist_info)
        self._top = top
        self._owner = User(playlist_info.get('owner', {}))
        self._tracks = []
        tracks = playlist_info.get('tracks', {})
        if tracks:
            for item in tracks.get('items', []):
                self._tracks.append(Track(item.get('track', {})))


    def owner(self):
        """
        Returns the owner of the playlist.

        Returns:
        A User object.
        """
        return deepcopy(self._owner)


    def uri(self):
        """
        Returns the URI of the playlist.

        Returns:
        A String URI.
        """
        return self._raw['uri']
        

    def add_tracks(self, tracks: Union[Track, List[Track]], position: int=None):
        """
        Add one or more tracks to the playlist.

        Parameters:
        tracks:   A Track object or list of Track objects to be added.

        Optional Parameters:
        position: An integer specifying the 0-indexed position in the playlist
                  to insert tracks. Position can be omitted to append to the
                  playlist instead.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        body = {}
        uris = []
        if isinstance(tracks, list):
            for track in tracks:
                uris.append(track.uri())
        else:
            uris.append(tracks.uri())
        body['uris'] = uris
        if position:
            body['position'] = position
        response_json, status_code = self._top._request('POST', endpoint, body=body)


    def update_name(self, name: str):
        """
        Update the playlist name.

        Parameters:
        name: A string containing the new name of this playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['name'] = name
        response_json, status_code = self._top._request('PUT', endpoint, body=body)


    def update_description(self, description: str):
        """
        Update the playlist description.

        Parameters:
        description: A string containing the new description of this playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['description'] = name
        response_json, status_code = self._top._request('PUT', endpoint, body=body)


    def update_visibility(self, visibility: str):
        """
        Update the playlist public/private visibility and collaborative access.

        Parameters:
        visibility: One of [sp.PUBLIC, sp.PRIVATE, sp.PRIVATE_COLLAB]
                    containing the new visibility of this playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        if visibility == sp.PUBLIC:
            body['public'] = true
        elif visibility == sp.PRIVATE:
            body['public'] = false
        elif visibility == s.PRIVATE_COLLAB:
            body['public'] = false
            body['collaborative'] = true
        else:
            raise ValueError("Invalid visibility, must be one of [sp.PUBLIC, sp.PRIVATE, sp.PRIVATE_COLLAB]")
        response_json, status_code = self._top._request('PUT', endpoint, body=body)


    # TODO test the response from this endpoint and clarify usage
    def image(self):
        """
        Return the playlist cover image.

        Returns:
        The String URL of the cover image.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_IMAGES.replace('{playlist_id}', self._raw['id'])
        response_json, status_code = self._top._request('GET', endpoint)
        return response_json['url']


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
        A List of Track objects.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['offset'] = start
        # TODO repeat queries if greater than 100
        if num_tracks:
            body['limit'] = num_tracks
        response_json, status_code = self._top._request('GET', endpoint, body=body)
        tracks = []
        for track in response_json['items']:
            tracks.append(Track(track))
        return tracks

    # TODO test this in practice, what does it actually mean? Nobody knows.
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
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['tracks'] = []
        if tracks and not positions:
            if not isinstance(tracks, list):
                tracks = [tracks]
            for track in tracks:
                track_info = {}
                track_info['uri'] = track.uri()
                body['tracks'].append(track_info)
        elif positions:
            if not isinstance(positions, list):
                positions = [positions]
            if not tracks:
                all_tracks = self._raw['tracks']['items']
                tracks = [all_tracks[i] for i in range(len(all_tracks)) if i in positions]
            for i in range(len(tracks)):
                if i in positions:
                    track = tracks[i]
                    track_info = {}
                    track_info['uri'] = track['uri']
                    track_info['positions'] = [i]
                    body['tracks'].append(track_info)
        else:
            return
        response_json, status_code = self._top._request('DELETE', endpoint, body=body)

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
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        if source_index < 0:
            source_index += len(self._raw['tracks']['items'])
        if destination_index < 0:
            destination_index += len(self._raw['tracks']['items'])
        if source_index < 0 or source_index >= len(self._raw['tracks']['items']):
            raise ValueError
        if destination_index < 0 or destination_index >= len(self._raw['tracks']['items']):
            raise ValueError
        body = {}
        body['range_start'] = source_index
        body['range_length'] = number
        body['insert_before'] = destination_index
        response_json, status_code = self._top._request('PUT', endpoint, body=body)

    def replace_all_tracks(self, tracks):
        """
        Replace all of the tracks in the playlist.

        Parameters:
        tracks: A list of Track objects to populate the playlist. These will
                be the only tracks in the playlist.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_TRACKS.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['uris'] = []
        for track in tracks:
            body['uris'].append(track.uri())
        response_json, status_code = self._top._request('PUT', endpoint, body=body)

    # TODO test this, no example in web api reference
    def replace_image(self, image):
        """
        Replace the playlist cover image.

        The image must be a JPEG and can be at most 256 KB in size.

        Parameters:
        image: A string containing the filename of the image to use as the
               playlist cover image. The image must be a JPEG up to 256 KB.
        """
        endpoint = Endpoint.BASE_URI + Endpoint.PLAYLIST_IMAGES.replace('{playlist_id}', self._raw['id'])
        body = []
        with open(image, "rb") as f:
            body.append(base64.b64encode(f.read()))
        response_json, status_code = self._top._request('GET', endpoint, body=body)

    def __str__(self):
        """Return a printable representation of the playlist."""
        return self._raw['name']

    def __len__(self):
        """Return the number of tracks in the playlist."""
        return len(self._raw['tracks']['items'])


from spotifython import Spotifython
from album import Album
from artist import Artist
from player import Player
from track import Track
from user import User
