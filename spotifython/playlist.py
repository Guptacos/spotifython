""" The Playlist class. """

# standard library imports
from copy import deepcopy
import base64
import sys
import mimetypes

# local imports
from spotifython.endpoints import Endpoints
import spotifython.constants as const
import spotifython.utils as utils

class Playlist:
    """ Represents a Spotify playlist tied to a unique Spotify id.

    Do not use the constructor. To get a Playlist by its id, use
    :meth:`Session.get_playlists() <spotifython.session.Session.get_playlists>`.
    To get a Playlist from another object, use appropriate methods such as
    :meth:`User.get_following() <spotifython.user.User.get_following>`,
    :meth:`User.get_playlists <spotifython.user.User.get_playlists>`, etc.

    Note:
        Playlist equality may behave unexpectedly, as it only depends on each
        Playslist's Spotify id. If one Playlist object has stale data, the two
        could have the same Spotify id, but have different internal
        representations of the contents of the Playlist.

        This could cause len(playlist), iterating through the playlist, etc. to
        behave unexpectedly.

        To ensure a Playlist's data is up to date, use Playlist.refresh().
    """

    # TODO store only static fields
    def __init__(self, session, info):
        """ Get an instance of Playlist. Client should not use the constructor!

        Args:
            session: a Session instance

            info (dict): the playlist's information. Must contain 'owner' and
                'id'.
        """
        self._raw = deepcopy(info)
        self._session = session
        if 'owner' not in info:
            raise ValueError('Playlist owner information missing')
        if 'id' not in info:
            raise ValueError('Playlist id missing')
        self._owner = User(session, info['owner'])
        self._tracks = []
        tracks = info.get('tracks', {})
        for item in tracks.get('items', []):
            if 'track' not in item:
                raise ValueError('Track information missing')
            self._tracks.append(Track(session, item.get('track', {})))


    def __str__(self):
        """ Returns the track name. """
        return f' Playlist {self.name()}'


    def __repr__(self):
        """ Returns the track name and Spotify id. """
        return str(self) + f' with id <{self.spotify_id()}>'


    def __len__(self):
        """
        Returns:
            int: The number of tracks in the playlist
        """
        return len(self._tracks)


    def __getitem__(self, key):
        """ Allows you to get a track in the playlist as if it were a list.

        Example::

            p = Playlist()
            track = p[2]

        Args:
            key (int, slice): the index into the playlist. The key can be any
                index or slice that that is a valid index into a list of length
                len(playlist).

        Returns:
            Track: The track at index "key"
        """
        if not isinstance(key, int):
            raise TypeError(key)
        if key < 0:
            key += len(self)
        if key < 0 or key >= len(self):
            raise IndexError(key)
        return self._tracks[key]


    def __eq__(self, other):
        """ Two playlists are equal if they have the same Spotify id. """
        return utils.spotifython_eq(self, other)


    def __ne__(self, other):
        """ Two playlists are not equal if they have different Spotify ids. """
        return not self.__eq__(other)


    def __hash__(self):
        """ Two equivalent playlists will return the same hashcode. """
        return utils.spotifython_hash(self)


    def spotify_id(self):
        """
        Returns:
            str: The Spotify id of this album.
        """
        return self._raw['id']


    def refresh(self):
        """ Refreshes the internal playlist data.

        Calls:
            GET /v1/playlists/{playlist_id}
        """
        endpoint = Endpoints.SEARCH_GET_PLAYLIST % self.spotify_id()
        response_json, status_code = utils.request(
            self._session,
            request_type='GET',
            endpoint=endpoint,
        )
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        self._raw = response_json
        self._owner = User(self._session, response_json['owner'])
        self._tracks = []
        tracks = response_json.get('tracks', {})
        for item in tracks.get('items', []):
            if 'track' not in item:
                raise ValueError('Track information missing')
            self._tracks.append(Track(self._session, item.get('track', {})))


    def raw(self):
        """ Returns the raw playlist data.

        Note:
            Makes a call to refresh() to update raw data before returning it.

        Returns:
            dict: The JSON object representing a raw playlist object from the
            Spotify Web API.

        Calls:
            GET /v1/playlists/{playlist_id}
        """
        self.refresh()
        return deepcopy(self._raw)


    def owner(self):
        """
        Returns:
            User: The owner of the playlist.
        """
        return self._owner


    def uri(self):
        """
        Returns:
            str: The playlist's Spotify uri.
        """
        return self._raw['uri']


    def href(self):
        """ Gets the playlist's href.

        Returns:
            str: A link to the Web API endpoint providing full playlist details.
        """
        return self._raw['href']


    def name(self):
        """
        Returns:
            str: The name of the Playlist as it appears on Spotify.
        """
        return self._raw['name']


    def add_tracks(self, tracks, position=None):
        """ Adds one or more tracks to the playlist.

        Args:
            tracks: A Track object or list of Track objects to be added.

            position: An integer specifying the 0-indexed position in the
                playlist to insert tracks. A negative integer will be evaluated
                from the end of the playlist as negative indices behave in
                lists. This must be a valid index into a list of length
                len(playlist). Position can be omitted to append to the
                playlist instead.

        Required token scopes:
            - playlist-modify-public: If the playlist is public.
            - playlist-modify-private: If the playlist is private or
              collaborative.

        Calls endpoints:
            - POST /v1/playlists/{playlist_id}/tracks
        """
        endpoint = Endpoints.PLAYLIST_TRACKS % self.spotify_id()
        body = {}
        uris = []
        if isinstance(tracks, list):
            for track in tracks:
                if not isinstance(track, Track):
                    raise TypeError('The elements of tracks must be Track ' +
                                    'objects')
                uris.append(track.uri())
        else:
            if not isinstance(tracks, Track):
                raise TypeError('The type of tracks must either be a Track ' +
                                'object or a list of Track objects')
            uris.append(tracks.uri())
        body['uris'] = uris
        if position:
            if not isinstance(position, int):
                raise TypeError('The position must be an integer')
            original_position = position
            if position < 0:
                position += len(self)
            if position < 0 or position >= len(self):
                raise ValueError(f'Invalid position: {original_position}')
            body['position'] = position
        response_json, status_code = utils.request(
            self._session,
            request_type='POST',
            endpoint=endpoint,
            body=body
        )
        if status_code != 201:
            raise utils.SpotifyError(status_code, response_json)


    def update_name(self, name):
        """ Updates the playlist's name as it appears on Spotify.

        Args:
            name (str): the new name of this playlist.

        Required token scopes:
            - playlist-modify-public: If the playlist is public.
            - playlist-modify-private: If the playlist is private or
              collaborative.

        Calls endpoints:
            - PUT /v1/playlists/{playlist_id}
        """
        endpoint = Endpoints.PLAYLIST % self.spotify_id()
        if not isinstance(name, str):
            raise TypeError('The name must be a string')
        body = {}
        body['name'] = name
        response_json, status_code = utils.request(
            self._session,
            request_type='PUT',
            endpoint=endpoint,
            body=body
        )
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)


    def update_description(self, description):
        """ Updates the playlist description as it appears on Spotify.

        Args:
            description (str): the new new description of this playlist.

        Required token scopes:
            - playlist-modify-public: If the playlist is public.
            - playlist-modify-private: If the playlist is private or
              collaborative.

        Calls endpoints:
            - PUT /v1/playlists/{playlist_id}
        """
        endpoint = Endpoints.PLAYLIST % self.spotify_id()
        if not isinstance(description, str):
            raise TypeError('The description must be a string')
        body = {}
        body['description'] = description
        response_json, status_code = utils.request(
            self._session,
            request_type='PUT',
            endpoint=endpoint,
            body=body
        )
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)


    def update_visibility(self, visibility):
        """ Updates whether the playlist is public/private/collaborative.

        Args:
            visibility: One of:

                - sp.PUBLIC
                - sp.PRIVATE
                - sp.PRIVATE_COLLAB

        Required token scopes:
            - playlist-modify-public: If the playlist is public.
            - playlist-modify-private: If the playlist is private or
              collaborative.

        Calls endpoints:
            - PUT /v1/playlists/{playlist_id}
        """
        endpoint = Endpoints.PLAYLIST % self.spotify_id()
        body = {}
        if visibility not in [const.PUBLIC, const.PRIVATE,
                              const.PRIVATE_COLLAB]:
            raise ValueError('Invalid visibility, must be one of [sp.PUBLIC,' +
                             'sp.PRIVATE, sp.PRIVATE_COLLAB]')
        body['public'] = (visibility == const.PUBLIC)
        body['collaborative'] = (visibility == const.PRIVATE_COLLAB)
        response_json, status_code = utils.request(
            self._session,
            request_type='PUT',
            endpoint=endpoint,
            body=body
        )
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)


    # TODO test the response from this endpoint and clarify usage
    # TODO: can the image be none?
    def image(self):
        """ Get the the playlist cover image.

        Returns:
            Image: an image object if the Playlist has a cover image.
            None: if the Playlist has no cover image.

        Calls endpoints:
            - PUT /v1/playlists/{playlist_id}
        """
        endpoint = Endpoints.PLAYLIST_IMAGES % self.spotify_id()
        response_json, status_code = utils.request(
            self._session,
            request_type='GET',
            endpoint=endpoint
        )
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)

        if len(response_json) > 1:
            raise utils.SpotifyError('Playlist has more than one cover image!')

        return None if len(response_json) == 0 else Image(response_json[0])

    def tracks(self, start=0, num_tracks=None, market=const.TOKEN_REGION):
        """ Returns one or more tracks in the playlist.

        Returns the specified number of tracks in the playlist starting at the
        given position. Returns all of the tracks in the playlist when called
        with the default parameters.

        Args:
            start: An integer specifying the 0-indexed position of the first
                track to return. A negative integer will be evaluated from the
                end of the playlist as negative indices behave in lists. This
                must be a valid index into a list of length len(playlist). Can
                be omitted to return tracks starting from the first song in the
                playlist.

            num_tracks: A nonnegative integer specifying the number of tracks
                to return. If num_tracks is greater than len(playlist) or if
                num_tracks is omitted, returns as many tracks as are present at
                start.
            market: A 2 letter country code as defined here:
                https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                Used for track relinking:
                https://developer.spotify.com/documentation/general/guides/track-relinking-guide/

                If omitted, will use the appropriate country code based on the
                auth token and location.

        Returns:
            List[Track]: The tracks specified by the arguments.

        Calls endpoints:
            - GET /v1/playlists/{playlist_id}/tracks
        """
        endpoint = Endpoints.PLAYLIST_TRACKS % self.spotify_id()
        if not isinstance(start, int):
            raise TypeError('The start index must be an integer')
        original_start = start
        if start < 0:
            start += len(self)
        if start < 0 or start >= len(self):
            raise ValueError(f'Invalid start: {original_start}')
        if num_tracks:
            if not isinstance(num_tracks, int):
                raise TypeError('The number of tracks must be an integer')
            if num_tracks < 0:
                raise ValueError(f'Invalid num_tracks: {num_tracks}')
        if not num_tracks:
            num_tracks = sys.maxsize
        uri_params = {}
        uri_params['market'] = market
        tracks = utils.paginate_get(self._session, num_tracks, Track,
                                    endpoint, uri_params=uri_params)
        return tracks[start:]

    # TODO test this in practice, what does it actually mean? Nobody knows.
    # TODO condense this messiness
    # pylint: disable=too-many-branches
    def remove_tracks(self, tracks=None, positions=None):
        """ Removes one or more tracks from the playlist.

        When provided with a list of tracks, all occurrences of those tracks in
        the playlist will be removed. Providing a list of track positions will
        only remove the tracks in those positions from the playlist. If both
        parameters are provided, positions takes precedence. At least one of
        the two parameters must be provided.

        Args:
            tracks: A Track or list of Track objects to be removed from the
                playlist. All tracks must be present in the playlist. All
                occurrences of these tracks will be removed.

            positions: An integer or list of integers specifying the
                nonnegative 0-indexed positions of tracks to be removed from
                the playlist. Positions must be valid indices into a list of
                len(playlist). Only tracks in these positions will be removed.

        Required token scopes:
            - playlist-modify-public: If the playlist is public.
            - playlist-modify-private: If the playlist is private or
              collaborative.

        Calls endpoints:
            - DELETE /v1/playlists/{playlist_id}/tracks
        """
        endpoint = Endpoints.PLAYLIST_TRACKS % self.spotify_id()
        body = {}
        body['tracks'] = []
        if tracks is not None and positions is None:
            if not isinstance(tracks, list):
                tracks = [tracks]
            for track in tracks:
                if not isinstance(track, Track):
                    raise TypeError('The tracks must be Track objects')
                if not track in self:
                    raise ValueError('All tracks must be in the playlist')
                track_info = {}
                track_info['uri'] = track.uri()
                body['tracks'].append(track_info)
        elif positions is not None:
            if not isinstance(positions, list):
                positions = [positions]
            for position in positions:
                if not isinstance(position, int):
                    raise TypeError('The positions must be integers')
                if position < 0 or position >= len(self):
                    raise ValueError(f'Invalid position: {position}')
            if tracks is None:
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
            raise ValueError('Neither tracks nor positions were provided')

        response_json, status_code = utils.request(
            self._session,
            request_type='DELETE',
            endpoint=endpoint,
            body=body
        )
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)


    # TODO test overlapping source/dest
    def reorder_tracks(self,
                       source_index,
                       dest_index,
                       number=1):
        """ Move one or more tracks to another position in the playlist.

        Moves the first number tracks starting at source_index to before the
        track currently at dest_index. If number is unspecified, only one track
        is moved.

        Args:
            source_index: An integer specifying the 0-indexed position of the
                first track to be moved. A negative integer will be evaluated
                from the end of the playlist as negative indices behave in
                lists. This must be a valid index into a list of length
                len(playlist).

            dest_index: An integer specifying the 0-indexed position of the
                track before which the other tracks will be moved. A negative
                integer will be evaluated from the end of the playlist as
                negative indices behave in lists. This must be a valid index
                into a list of length len(playlist).

            number: A positive integer specifying the number of tracks to be
                moved. Number may not be larger than len(playlist).

        Required token scopes:
            - playlist-modify-public: If the playlist is public.
            - playlist-modify-private: If the playlist is private or
              collaborative.

        Calls endpoints:
            - PUT /v1/playlists/{playlist_id}/tracks
        """
        endpoint = Endpoints.PLAYLIST_TRACKS % self.spotify_id()
        if not isinstance(source_index, int):
            raise TypeError('The source index must be an integer')
        if not isinstance(dest_index, int):
            raise TypeError('The source index must be an integer')
        if not isinstance(number, int):
            raise TypeError('The source index must be an integer')
        original_source_index = source_index
        original_dest_index = dest_index
        if source_index < 0:
            source_index += len(self)
        if dest_index < 0:
            dest_index += len(self)
        if source_index < 0 or source_index >= len(self):
            raise ValueError(f'Invalid source_index: {original_source_index}')
        if dest_index < 0 or dest_index >= len(self):
            raise ValueError(f'Invalid dest_index: {original_dest_index}')
        if number <= 0 or number > len(self):
            raise ValueError(f'Invalid number: {number}')
        body = {}
        body['range_start'] = source_index
        body['range_length'] = number
        body['insert_before'] = dest_index
        response_json, status_code = utils.request(
            self._session,
            request_type='PUT',
            endpoint=endpoint,
            body=body
        )
        if status_code != 200:
            raise utils.SpotifyError(status_code, response_json)


    def replace_all_tracks(self, tracks):
        """ Replace all of the tracks in the playlist.

        Args:
            tracks (List[Track]): The tracks to populate the playlist.

        Warning:
            All previously present tracks in the playlist will be removed.

        Required token scopes:
            - playlist-modify-public: If the playlist is public.
            - playlist-modify-private: If the playlist is private or
              collaborative.

        Calls endpoints:
            - PUT /v1/playlists/{playlist_id}/tracks
        """
        endpoint = Endpoints.PLAYLIST_TRACKS % self.spotify_id()
        if not all([isinstance(track, Track) for track in tracks]):
            raise TypeError('All elements of tracks must be Track objects')
        body = {}
        body['uris'] = [track.uri() for track in tracks]
        response_json, status_code = utils.request(
            self._session,
            request_type='PUT',
            endpoint=endpoint,
            body=body
        )
        if status_code != 201:
            raise utils.SpotifyError(status_code, response_json)


    # TODO test this, no example in web api reference
    def replace_image(self, path):
        """ Replace the playlist cover image.

        Note:
            The image must be a JPEG and can be at most 256 KB in size.

        Args:
            path: A string containing the path to the image to use as the
                playlist cover image. The image must be a JPEG up to 256 KB.

        Required token scopes:
            - ugc-image-upload
            - playlist-modify-public: If the playlist is public.
            - playlist-modify-private: If the playlist is private or
              collaborative.

        Calls endpoints:
            - PUT /v1/playlists/{playlist_id}/images
        """
        endpoint = Endpoints.BASE_URI
        endpoint += Endpoints.PLAYLIST_IMAGES % self.spotify_id()
        mime_type, encoding = mimetypes.guess_type(path)
        if not mime_type == 'image/jpeg':
            raise ValueError('The image must be an image/jpeg')

        body = []
        with open(path, 'rb') as fp:
            body.append(base64.b64encode(fp.read()))

        response_json, status_code = utils.request(
            self._session,
            request_type='PUT',
            endpoint=endpoint,
            body=body
        )

        if status_code != 202:
            raise utils.SpotifyError(status_code, response_json)


# pylint: disable=wrong-import-position
from spotifython.user import User
from spotifython.track import Track
