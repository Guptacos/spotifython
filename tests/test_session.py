'''Tests for the Session class

Note: these tests are not exhaustive and could always be improved. Since the
Spotify REST api is mocked, if it's functionality ever changes these tests may
become obsolete.

Last updated: May 30, 2020
'''
# These 2 statements are fine to include in your test file
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring

# These are here so the template in particular passes pylint; don't copy them
#pylint: disable=no-name-in-module
#pylint: disable=no-member
#pylint: disable=import-error
#pylint: disable=redundant-unittest-assert

#TODO: remove this pylint ignore when the tests are written
#pylint: disable=unused-import

# Standard library imports
import unittest
from unittest.mock import patch

# Local imports
from tests.help_lib import get_dummy_data
import spotifython.constants as const
import spotifython.utils as utils

USER_ID = 'deadbeef'
TOKEN = 'feebdaed'
TOKEN1 = TOKEN + TOKEN

SEARCH_LIMIT_1 = 100
SEARCH_LIMIT_2 = 49

expected_albums_json = get_dummy_data(
    const.ALBUMS,
    limit=SEARCH_LIMIT_1,
)
expected_albums = get_dummy_data(
    const.ALBUMS,
    limit=SEARCH_LIMIT_1,
    to_obj=True
)

expected_artists_json = get_dummy_data(
    const.ARTISTS,
    limit=SEARCH_LIMIT_1,
)
expected_artists = get_dummy_data(
    const.ARTISTS,
    limit=SEARCH_LIMIT_1,
    to_obj=True
)

expected_playlists_json = get_dummy_data(
    const.PLAYLISTS,
    limit=SEARCH_LIMIT_2,
)
expected_playlists = get_dummy_data(
    const.PLAYLISTS,
    limit=SEARCH_LIMIT_2,
    to_obj=True
)

expected_tracks_json = get_dummy_data(
    const.TRACKS,
    limit=SEARCH_LIMIT_2,
)
expected_tracks = get_dummy_data(
    const.TRACKS,
    limit=SEARCH_LIMIT_2,
    to_obj=True
)

class TestArtist(unittest.TestCase):

    # This function is called before every test_* function. Anything that is
    # needed by every test_* function should be stored in "self" here.
    def setUp(self):
        # Mock the sp._request method so that we never actually reach Spotify
        self.patcher = patch.object(utils, 'request', autospec=True)

        # Add cleanup to unmock sp._request. Cleanup always called after trying
        # to execute a test, even if the test or setUp errors out / fails.
        self.addCleanup(self.patcher.stop)

        # Create the actual mock object
        self.request_mock = self.patcher.start()

    # This function is called after every test_* function. Use it to clean up
    # any resources initialized by the setUp function. Only include it if you
    # actually need to clean up resources.
    def tearDown(self):
        pass

    # Test __str__, __repr__
    def test_str_overloads(self):
        # Note: since we're mocking Spotify and never actually using the token,
        # we can put any string here for the token.
        session = Session(TOKEN)
        session_1 = Session(TOKEN1)
        self.assertEqual(str(session), str(session))
        self.assertFalse(str(session) == str(session_1))
        self.assertEqual(repr(session), repr(session))
        self.assertFalse(repr(session) == repr(session_1))

    # Test __eq__, __ne__, __hash__
    def test_equality_overloads(self):
        session = Session(TOKEN)
        session_1 = Session(TOKEN1)
        self.assertEqual(session, session)
        self.assertFalse(session == session_1)
        self.assertEqual(hash(session), hash(session))
        self.assertFalse(hash(session) == hash(session_1))

    # Test reauthenticate
    def test_reauthenticate(self):
        session = Session(TOKEN)
        session.reauthenticate(TOKEN1)
        session_1 = Session(TOKEN1)
        self.assertFalse(session == session_1)

    # Test token, timeout
    def test_getters(self):
        session = Session(TOKEN)
        session_1 = Session(TOKEN1)
        self.assertEqual(session.token(), session.token())
        self.assertFalse(session.token() == session_1.token())
        # Using default timeout
        self.assertEqual(session.timeout(), session.timeout())
        self.assertEqual(session.timeout(), session_1.timeout())

    # Test search
    def test_search(self):
        session = Session(TOKEN)
        self.request_mock.side_effect = [
            (
                {
                    'albums': {
                        'href': 'href_uri',
                        'items': expected_albums_json[:50],
                        'limit': 50,
                        'next': 'next_here',
                        'offset': 0,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_1,
                    },
                    'artists': {
                        'href': 'href_uri',
                        'items': expected_artists_json[:50],
                        'limit': 50,
                        'next': 'next_here',
                        'offset': 0,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_1,
                    },
                    'playlists': {
                        'href': 'href_uri',
                        'items': expected_playlists_json[:50],
                        'limit': 50,
                        'next': 'next_here',
                        'offset': 0,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_2,
                    },
                    'tracks': {
                        'href': 'href_uri',
                        'items': expected_tracks_json[:50],
                        'limit': 50,
                        'next': 'next_here',
                        'offset': 0,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_2,
                    }
                },
                200
            ),
            (
                {
                    'albums': {
                        'href': 'href_uri',
                        'items': expected_albums_json[50:100],
                        'limit': 50,
                        'next': 'next_here',
                        'offset': 50,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_1,
                    },
                    'artists': {
                        'href': 'href_uri',
                        'items': expected_artists_json[50:100],
                        'limit': 50,
                        'next': 'next_here',
                        'offset': 50,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_1,
                    },
                    'playlists': {
                        'href': 'href_uri',
                        'items': [],
                        'limit': 50,
                        'next': None,
                        'offset': 50,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_2,
                    },
                    'tracks': {
                        'href': 'href_uri',
                        'items': [],
                        'limit': 50,
                        'next': None,
                        'offset': 50,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_2,
                    }
                },
                200
            ),
            (
                {
                    'albums': {
                        'href': 'href_uri',
                        'items': [],
                        'limit': 50,
                        'next': None,
                        'offset': 100,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_1,
                    },
                    'artists': {
                        'href': 'href_uri',
                        'items': [],
                        'limit': 50,
                        'next': None,
                        'offset': 100,
                        'previous': 'previous_uri',
                        'total': SEARCH_LIMIT_1,
                    }
                },
                200
            )
        ]
        search_result = session.search(query="dummy_query",
                                      types=[const.ARTISTS, const.ALBUMS, const.PLAYLISTS, const.TRACKS],
                                      limit=None
                                      )
        self.assertEqual(search_result.albums(), expected_albums)
        self.assertEqual(search_result.artists(), expected_artists)
        self.assertEqual(search_result.playlists(), expected_playlists)
        self.assertEqual(search_result.tracks(), expected_tracks)

    # Test get_albums
    def test_get_albums(self):
        session = Session(TOKEN)
        self.request_mock.side_effect = [
            (
                {
                    "albums" : expected_albums_json[0:20]
                },
                200
            ),
            (
                {
                    "albums" : expected_albums_json[20:40]
                },
                200
            ),
            (
                {
                    "albums" : expected_albums_json[40:60]
                },
                200
            ),
            (
                {
                    "albums" : expected_albums_json[60:80]
                },
                200
            ),
            (
                {
                    "albums" : expected_albums_json[80:100]
                },
                200
            )
        ]
        albums = session.get_albums(
            list(
                map(lambda x: x['id'], expected_albums_json)
            )
        )
        self.assertEqual(albums, expected_albums)

    # Test get_artists
    def test_get_artists(self):
        session = Session(TOKEN)
        self.request_mock.side_effect = [
            (
                {
                    "artists" : expected_artists_json[0:50]
                },
                200
            ),
            (
                {
                    "artists" : expected_artists_json[50:100]
                },
                200
            )
        ]
        artists = session.get_artists(
            list(
                map(lambda x: x['id'], expected_artists_json)
            )
        )
        self.assertEqual(artists, expected_artists)

    # Test get_tracks
    def test_get_tracks(self):
        session = Session(TOKEN)
        self.request_mock.side_effect = [
            (
                {
                    "tracks" : expected_tracks_json[0:50]
                },
                200
            ),
            (
                {
                    "tracks" : expected_tracks_json[50:100]
                },
                200
            )
        ]
        tracks = session.get_tracks(
            list(
                map(lambda x: x['id'], expected_tracks_json)
            )
        )
        self.assertEqual(tracks, expected_tracks)

    # Test get_users, current_user
    @unittest.skip('Not yet implemented')
    def test_get_users(self):
        self.assertTrue(False)

    # Test get_playlists
    @unittest.skip('Not yet implemented')
    def test_get_playlists(self):
        self.assertTrue(False)

# This allows the tests to be executed
if __name__ == '__main__':
    unittest.main()

#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.player import Player
from spotifython.playlist import Playlist
from spotifython.track import Track
from spotifython.user import User
from spotifython.session import Session
