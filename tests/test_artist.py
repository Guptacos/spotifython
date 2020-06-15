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

#TODO: remove this pylint ignore when the tests are written
#pylint: disable=unused-import

# Standard library imports
import unittest
from unittest.mock import patch

# Local imports
from tests.help_lib import get_dummy_data
import spotifython.constants as const
import spotifython.utils as utils

ARTIST_ID = 'deadbeef'
TOKEN = 'feebdaed'

class TestArtist(unittest.TestCase):

    # This function is called before every test_* function. Anything that is
    # needed by every test_* function should be stored in "self" here.
    def setUp(self):
        # Note: since we're mocking Spotify and never actually using the token,
        # we can put any string here for the token.
        self.session = Session(TOKEN)

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
    @unittest.skip('Not yet implemented')
    def test_str_overloads(self):
        artist = get_dummy_data(const.ARTISTS, limit=1, to_obj=True)[0]
        self.assertTrue(isinstance(artist.__str__(), str))
        self.assertTrue(isinstance(artist.__repr__(), str))

    # Test __eq__, __ne__, __hash__
    def test_equality_overloads(self):
        artists = get_dummy_data(const.ARTISTS, limit=2, to_obj=True)
        self.assertTrue(artists[0] != artists[1])
        self.assertTrue(artists[0] == artists[0])
        self.assertTrue(artists[1] == artists[1])

    # Test genres(), href(), spotify_id(), name(), popularity(), uri() when
    # their corresponding fields are present
    def test_field_accessors(self):
        artists = get_dummy_data(const.ARTISTS, limit=2, to_obj=True)
        artist_0, artist_1 = artists[0], artists[1]

        self.assertTrue(all(
            (isinstance(genre, str) for genre in x.genres()) for x in [artist_0, artist_1])
        )
        self.assertTrue(all(
            isinstance(x.href(), str) for x in [artist_0, artist_1])
        )
        self.assertTrue(all(
            isinstance(x.spotify_id(), str) for x in [artist_0, artist_1])
        )
        self.assertTrue(all(
            isinstance(x.name(), str) for x in [artist_0, artist_1])
        )
        self.assertTrue(all(
            isinstance(x.popularity(), int) for x in [artist_0, artist_1])
        )
        self.assertTrue(all(
            isinstance(x.uri(), str) for x in [artist_0, artist_1])
        )

    # Test _update_fields()
    def test_update_fields(self):
        self.request_mock.return_value = (get_dummy_data(const.ARTISTS, limit=1)[0], 200)
        expected_artist = get_dummy_data(const.ARTISTS, limit=1, to_obj=True)[0]
        artist = Artist(session=self.session, info={'id': expected_artist.spotify_id()})

        # Check state before updating the fields
        self.assertTrue(artist == expected_artist)
        self.assertEqual(artist._raw.__len__(), 1)

        # Check state after updating the fields
        artist._update_fields()
        self.assertTrue(artist == expected_artist)
        self.assertEqual(artist._raw.__len__(), expected_artist._raw.__len__())

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
