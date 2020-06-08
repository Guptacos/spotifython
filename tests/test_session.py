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

# Standard library imports
import unittest
from unittest.mock import patch

# Local imports
from tests.help_lib import get_dummy_data
import spotifython.constants as const

USER_ID = 'deadbeef'
TOKEN = 'feebdaed'

class TestSession(unittest.TestCase):

    # This function is called before every test_* function. Anything that is
    # needed by every test_* function should be stored in "self" here.
    def setUp(self):
        # Note: since we're mocking Spotify and never actually using the token,
        # we can put any string here for the token.
        self.session = sp(TOKEN)

        # Mock the sp._request method so that we never actually reach Spotify
        self.patcher = patch.object(sp, '_request', autospec=True)

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
    @unittest.skip('Not yet implemented')
    def test_str_overloads(self):
        self.assertTrue(self.session == self.session)

    # Test __eq__, __ne__, __hash__
    @unittest.skip('Not yet implemented')
    def test_equality_overloads(self):
        self.assertTrue(False)

    # Test reauthenticate
    @unittest.skip('Not yet implemented')
    def test_reauthenticate(self):
        self.assertTrue(False)

    # Test token, timeout
    @unittest.skip('Not yet implemented')
    def test_getters(self):
        self.assertTrue(False)

    # Test search
    @unittest.skip('Not yet implemented')
    def test_search(self):
        self.assertTrue(False)

    # Test get_albums
    @unittest.skip('Not yet implemented')
    def test_get_albums(self):
        self.assertTrue(False)

    # Test get_artists
    @unittest.skip('Not yet implemented')
    def test_get_artists(self):
        self.assertTrue(False)

    # Test get_tracks
    @unittest.skip('Not yet implemented')
    def test_get_tracks(self):
        self.assertTrue(False)

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
from spotifython.session import Session as sp
