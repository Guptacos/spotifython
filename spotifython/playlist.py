""" The Playlist class.

This class represents a playlist as defined by Spotify.
"""

class Playlist:
    """ A Playlist object. """

    # TODO store only static fields
    def __init__(self, session, info):
        """ Playlist constructor that should never be called directly.

        Args:
            session: The Spotifython session object used to create this object.
            info: The dict with playlist data produced from a Spotify API call.
        """
        self._raw = deepcopy(info)
        self._session = session
        self._owner = User(session, info.get('owner', {}))
        self._tracks = []
        tracks = info.get('tracks', {})
        if tracks:
            for item in tracks.get('items', []):
                self._tracks.append(Track(item.get('track', {})))


    def owner(self):
        """ Returns the owner of the playlist.

        Returns:
            A User object.
        """
        return deepcopy(self._owner)


    def uri(self):
        """ Returns the URI of the playlist.

        Returns:
            A string URI.
        """
        return self._raw['uri']


    def add_tracks(self, tracks, position=None):
        """ Adds one or more tracks to the playlist.

        Args:
            tracks: A Track object or list of Track objects to be added.
            position: An integer specifying the 0-indexed position in the
                playlist to insert tracks. Position can be omitted to append to
                the playlist instead.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST_TRACKS.replace('{playlist_id}',
                                                      self._raw['id'])
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
        response_json, status_code = utils.request(self._session, 'POST',
                                                   endpoint, body=body)
        if status_code != 201:
            raise utils.SpotifyError(status_code, response_json)


    def update_name(self, name):
        """ Updates the playlist name.

        Args:
            name: A string containing the new name of this playlist.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['name'] = name
        response_json, status_code = utils.request(self._session, 'PUT',
                                                   endpoint, body=body)
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)


    def update_description(self, description):
        """ Updates the playlist description.

        Args:
            description: A string containing the new description of this
                playlist.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        body['description'] = description
        response_json, status_code = utils.request(self._session, 'PUT',
                                                   endpoint, body=body)
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)


    def update_visibility(self, visibility):
        """ Updates the playlist public/private visibility and collaborative
            access.

        Args:
            visibility: One of [sp.PUBLIC, sp.PRIVATE, sp.PRIVATE_COLLAB]
                containing the new visibility of this playlist.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST.replace('{playlist_id}', self._raw['id'])
        body = {}
        if visibility == const.PUBLIC:
            body['public'] = True
        elif visibility == const.PRIVATE:
            body['public'] = False
        elif visibility == const.PRIVATE_COLLAB:
            body['public'] = False
            body['collaborative'] = True
        else:
            raise ValueError('Invalid visibility, must be one of [sp.PUBLIC,' +
                             'sp.PRIVATE, sp.PRIVATE_COLLAB]')
        response_json, status_code = utils.request(self._session, 'PUT',
                                                   endpoint, body=body)
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)


    # TODO test the response from this endpoint and clarify usage
    def image(self):
        """ Returns the playlist cover image.

        Returns:
            The string URL of the cover image.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST_IMAGES.replace('{playlist_id}',
                                                      self._raw['id'])
        response_json, status_code = utils.request(self._session, 'GET',
                                                   endpoint)
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        return response_json['url']


    def tracks(self, start=0, num_tracks=None):
        """ Returns one or more tracks in the playlist.

        Returns the specified number of tracks in the playlist starting at the
        given position. Returns all of the tracks in the playlist when given no
        parameters.

        Args:
            start: An integer specifying the 0-indexed position of the first
                track to return. Can be omitted to return tracks starting from
                the first song in the playlist.
            num_tracks: An integer specifying the number of tracks to return.
                Can be omitted to return as many tracks as are present at
                start.

        Returns:
            A list of Track objects.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST_TRACKS.replace('{playlist_id}',
                                                      self._raw['id'])
        if not num_tracks:
            num_tracks = sys.maxsize
        tracks = utils.paginate_get(self._session, num_tracks, Track,
                                    endpoint)
        return tracks[start:]

    # TODO test this in practice, what does it actually mean? Nobody knows.
    def remove_tracks(self, tracks=None, positions=None):
        """ Removes one or more tracks from the playlist.

        When provided with a list of tracks, all occurrences of those tracks in
        the playlist will be removed. Providing a list of track positions will
        only remove the tracks in those positions from the playlist. No tracks
        will be removed if neither of the parameters are provided. If both
        parameters are provided, positions takes precedence.

        Args:
            tracks: A Track or list of Track objects to be removed from the
                playlist.  All occurrences of these tracks will be removed.
            positions: An integer or list of integers specifying the 0-indexed
                positions of tracks to be removed from the playlist. Only
                tracks in these positions will be removed.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST_TRACKS.replace('{playlist_id}',
                                                      self._raw['id'])
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
                all_tracks = self.tracks()
                tracks = [all_tracks[i] for i in range(len(all_tracks))
                          if i in positions]
            for i, track in enumerate(tracks):
                if i in positions:
                    track_info = {}
                    track_info['uri'] = track['uri']
                    track_info['positions'] = [i]
                    body['tracks'].append(track_info)
        else:
            return

        response_json, status_code = utils.request(self._session, 'DELETE',
                                                   endpoint, body=body)
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

    def reorder_tracks(self, source_index, destination_index, number=1):
        """ Move one or more tracks to another position in the playlist.

        Moves the specified number of tracks starting at source_index to before
        the track currently at destination_index. If number is unspecified,
        only one track is moved.

        Args:
            source_index: An integer specifying the 0-indexed position of the
                first track to be moved. A negative integer will be evaluated
                from the end of the playlist as negative indices behave in
                lists. This must be a valid index into a list of length
                len(playlist).
            destination_index: An integer specifying the 0-indexed position of
                the track before which the other tracks will be moved. A
                negative integer will be evaluated from the end of the playlist
                as negative indices behave in lists. This must be a valid index
                into a list of length len(playlist).
            number: A nonnegative integer specifying the number of tracks to be
                moved. Specifying 0 will result in no change to the playlist.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST_TRACKS.replace('{playlist_id}',
                                                      self._raw['id'])
        original_source_index = source_index
        original_destination_index = destination_index
        if source_index < 0:
            source_index += len(self)
        if destination_index < 0:
            destination_index += len(self)
        if (source_index < 0 or
                source_index >= len(self)):
            raise ValueError(f'Invalid source_index: {original_source_index}')
        if (destination_index < 0 or
                destination_index >= len(self)):
            raise ValueError('Invalid destination_index:' +
                             f' {original_destination_index}')
        body = {}
        body['range_start'] = source_index
        body['range_length'] = number
        body['insert_before'] = destination_index
        response_json, status_code = utils.request(self._session, 'PUT',
                                                   endpoint, body=body)
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

    def replace_all_tracks(self, tracks):
        """ Replace all of the tracks in the playlist.

        Args:
        tracks: A list of Track objects to populate the playlist. These will be
            the only tracks in the playlist.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST_TRACKS.replace('{playlist_id}',
                                                      self._raw['id'])
        body = {}
        body['uris'] = [track.uri() for track in tracks]
        response_json, status_code = utils.request(self._session, 'PUT',
                                                   endpoint, body=body)
        if status_code != 201:
            raise utils.SpotifyError(status_code, response_json)

    # TODO test this, no example in web api reference
    def replace_image(self, image):
        """ Replace the playlist cover image.

        The image must be a JPEG and can be at most 256 KB in size.

        Args:
        image: A string containing the filename of the image to use as the
            playlist cover image. The image must be a JPEG up to 256 KB.
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST_IMAGES.replace('{playlist_id}',
                                                      self._raw['id'])
        body = []
        with open(image, 'rb') as image_file:
            body.append(base64.b64encode(image_file.read()))
        response_json, status_code = utils.request(self._session, 'PUT',
                                                   endpoint, body=body)
        if status_code != 202:
            raise utils.SpotifyError(status_code, response_json)

    def __str__(self):
        """ Return a printable representation of the playlist. """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST.replace('{playlist_id}', self._raw['id'])

        response_json, status_code = utils.request(self._session, 'GET',
                                                   endpoint)
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        return response_json['name']

    def __repr__(self):
        """ Return a printable representation of the playlist. """
        return str(self)

    def __len__(self):
        """ Return the number of tracks in the playlist. """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST.replace('{playlist_id}', self._raw['id'])

        response_json, status_code = utils.request(self._session, 'GET',
                                                   endpoint)
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        return response_json['tracks']['total']


# pylint: disable=wrong-import-position
from copy import deepcopy
import base64
import sys

from spotifython.endpoints import Endpoints
from spotifython.user import User
from spotifython.track import Track
import spotifython.constants as const
import spotifython.utils as utils
