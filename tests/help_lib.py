import json
import sys
sys.path.append('../spotifython')
from spotifython import Spotifython as sp

BASE_PATH = 'dummy_data/'
MAPPINGS = {
    sp.ARTIST: 'artists.json',
    sp.ALBUM: 'albums.json',
    sp.PLAYLIST: 'playlists.json',
    sp.USER: 'users.json',
    sp.TRACK: 'tracks.json'
}

def get_dummy_data(data_type: str, limit: int = 50):
    ''' Helper function for the test suite to get dummy data

    Dummy data is taken by pinging the Spotify REST api and saving the response

    Keyword arguments:
        data_type: the type of data supported.
        limit: the maximum number of items to return. May return less

    Returns:
        A list of json objects from Spotify, each for a data_type object.
    '''
    if data_type not in [sp.ARTIST,
                         sp.ALBUM,
                         sp.PLAYLIST,
                         sp.USER,
                         sp.TRACK]:
        raise TypeError(data_type)

    with open(BASE_PATH + MAPPINGS[data_type], 'r') as fp:
        result = json.load(fp)

    return result['items'][:limit]
