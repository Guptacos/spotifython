""" Helper functions for the test suite
"""

import json
import sys
sys.path.append('../spotifython')
import spotifython.constants as const

BASE_PATH = 'tests/dummy_data/'
MAPPINGS = {
    const.ARTISTS: 'artists.json',      # 336 total
    const.ALBUMS: 'albums.json',        # 100 total
    const.PLAYLISTS: 'playlists.json',  # 38 total
    const.USERS: 'users.json',          # 200 total
    const.TRACKS: 'tracks.json'         # 205 total
}

def get_dummy_data(data_type: str, limit: int = 50):
    """ Helper function for the test suite to get dummy data

    Dummy data is taken by pinging the Spotify REST api and saving the response

    Args:
        data_type: the type of data supported.
        limit: the maximum number of items to return. May return less

    Returns:
        A list of json objects from Spotify, each for a data_type object.
    """
    if data_type not in [const.ARTISTS,
                         const.ALBUMS,
                         const.PLAYLISTS,
                         const.USERS,
                         const.TRACKS]:
        raise TypeError(data_type)

    with open(BASE_PATH + MAPPINGS[data_type], 'r') as fp:
        result = json.load(fp)

    return result['items'][:limit]
