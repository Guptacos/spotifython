'''Tests for the Artist class

Note: these tests are not exhaustive and could always be improved. Since the
Spotify REST api is mocked, if it's functionality ever changes these tests may
become obsolete.

Last updated: May 25, 2020
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

class TestArtist(unittest.TestCase):

    # This function is called before every test_* function. Anything that is
    # needed by every test_* function should be stored in "self" here.
    def setUp(self):
        # Note: since we're mocking Spotify and never actually using the token,
        # we can put any string here for the token.
        self.session = sp(TOKEN)
        self.artist = Artist(get_dummy_data(const.ARTISTS, 1))

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
        self.assertTrue(False)

    # Test __eq__, __ne__, __hash__
    @unittest.skip('Not yet implemented')
    def test_equality_overloads(self):
        self.assertTrue(False)

    # Test __str__, __repr__
    @unittest.skip('Not yet implemented')
    def test_str_overloads(self):
        self.assertTrue(False)

    # Test genres(), href(), spotify_id(), name(), popularity(), uri() when
    # their corresponding fields are present
    @unittest.skip('Not yet implemented')
    def test_field_accessors(self):
        self.assertTrue(False)

    # Test _update_fields()
    @unittest.skip('Not yet implemented')
    def test_update_fields(self):
        self.assertTrue(False)

    # Test albums()
    @unittest.skip('Not yet implemented')
    def test_albums(self):
        self.assertTrue(False)

    # Test top_tracks()
    @unittest.skip('Not yet implemented')
    def test_top_tracks(self):
        self.assertTrue(False)

    # Test related_artists()
    @unittest.skip('Not yet implemented')
    def test_related_artists(self):
        self.assertTrue(False)

    #########################
    ### TEMPLATE IGNORE THIS
    #########################

    # This shows how to skip tests so they don't execute when running
    @unittest.skip('Not yet implemented')
    def test_beyond_beef(self):
        self.assertTrue(False)


    # This method shows how to actually mock
    # Here we will test the following imaginary function:
    # def mince(self, method: str, quantity: int)
    #
    # Note that the test function name doesn't have to mirror the function it's
    # testing; you can test any number of function within a test, as long as the
    # test function is prefixed by test_
    @unittest.skip('Sample Test')
    def test_mock_beef(self):
        beef = self.deadbeef

        # Input checking: can't mince beef with a spoon, and True isn't an int!
        self.assertRaises(TypeError, beef.mince, const.SPOON, True)

        # Now we mock the _request method. The next time _request is called (and
        # every time afterwards that it's called in this test until it's
        # changed) it will return ({}, 200) to the DeadBeef library.
        self.request_mock.return_value = {}, 200

        minced = beef.mince(const.KNIFE, quantity=10)
        self.assertIsInstance(minced, DeadBeef)
        self.assertEqual(minced.weight, 100)

    #########################
    ### END TEMPLATE
    #########################


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
