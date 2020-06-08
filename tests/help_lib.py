""" Helper functions for the test suite
"""

# Standard library imports
import json
import sys

# Local imports
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.playlist import Playlist
from spotifython.track import Track
from spotifython.user import User

#pylint: disable=wrong-import-position
sys.path.append('../spotifython')
import spotifython.constants as const

BASE_PATH = 'tests/dummy_data/'
FILE_MAPPINGS = {
    const.ALBUMS: 'albums.json',        # 100 total
    const.ARTISTS: 'artists.json',      # 336 total
    const.PLAYLISTS: 'playlists.json',  # 38 total
    const.TRACKS: 'tracks.json',        # 205 total
    const.USERS: 'users.json'           # 200 total
}

CLASS_MAPPINGS = {
    const.ALBUMS: Album,
    const.ARTISTS: Artist,
    const.PLAYLISTS: Playlist,
    const.TRACKS: Track,
    const.USERS: User
}

def get_dummy_data(data_type: str,
                   limit: int = 50,
                   to_obj: bool = False):
    """ Helper function for the test suite to get dummy data

    Dummy data is taken by pinging the Spotify REST api and saving the response

    Args:
        data_type: the type of data supported.
        limit: the maximum number of items to return. May return less
        to_obj: if True, will construct the objects
                if False, will return raw jsons

    Returns:
        A list of json objects from Spotify, each for a data_type object.
    """
    if data_type not in [const.ARTISTS,
                         const.ALBUMS,
                         const.PLAYLISTS,
                         const.USERS,
                         const.TRACKS]:
        raise TypeError(data_type)

    with open(BASE_PATH + FILE_MAPPINGS[data_type], 'r') as fp:
        result = json.load(fp)

    result = result['items'][:limit]

    if to_obj:
        map_func = lambda elem: CLASS_MAPPINGS[data_type](None, elem)
        result = [map_func(elem) for elem in result]

    return result
