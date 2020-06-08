''' Tests for the Track class
'''
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring

# Standard library imports
import unittest
from unittest.mock import patch

# Local imports
from tests.help_lib import get_dummy_data
import spotifython.constants as const
import spotifython.utils as utils
from spotifython.session import Session

TOKEN = 'feedbaed'


class TestTrack(unittest.TestCase):


    def setUp(self):
        self.session = Session(TOKEN)

        # Mock the sp._request method so that we never actually reach Spotify
        self.patcher = patch.object(utils, 'request', autospec=True)

        # Add cleanup to unmock sp._request. Cleanup always called at end.
        self.addCleanup(self.patcher.stop)
        self.request_mock = self.patcher.start()


    @unittest.skip('Not yet implemented')
    def test_init(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_dunder(self):
        #str
        #repr
        #eq
        #ne
        #hash
        #len
        pass


    @unittest.skip('Not yet implemented')
    def test__update_fields(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_spotify_id(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_album(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_artists(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_available_markets(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_name(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_popularity(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_disc_number(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_track_number(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_explicit(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_uri(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_href(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_audio_features(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_audio_analysis(self):
        pass


# This allows the tests to be executed
if __name__ == '__main__':
    unittest.main()

#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.track import Track
