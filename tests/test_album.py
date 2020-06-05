''' Tests for the Album class
'''
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring
#pylint: disable=too-many-public-methods

# Standard library imports
import unittest
from unittest.mock import patch

# Local imports
from tests.help_lib import get_dummy_data
import spotifython.constants as const
import spotifython.utils as utils
from spotifython.session import Session

TOKEN = 'feebdaed'


class TestAlbum(unittest.TestCase):


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


    def test_dunder(self):
        # Get 2 instances of the same album
        album1 = get_dummy_data(const.ALBUMS, limit=1, to_obj=True)[0]
        album1_dup = get_dummy_data(const.ALBUMS, limit=1, to_obj=True)[0]

        # eq, hash
        self.assertEqual(album1, album1_dup)
        self.assertEqual(hash(album1), hash(album1_dup))
        self.assertIsNot(album1, album1_dup)

        # str, repr should return str and not raise exceptions
        self.assertIsInstance(album1.__str__(), str)
        self.assertIsInstance(album1.__repr__(), str)

        # Get a second album to compare for ne
        album2 = get_dummy_data(const.ALBUMS, limit=2, to_obj=True)[1]
        self.assertNotEqual(album1, album2)

        # The dummy_data albums don't have Tracks, so mock the Spotify request
        # TODO: should this be fixed?
        response_json = {
            'items': get_dummy_data(const.TRACKS, limit=10),
            'total': 10,
            'limit': 50,
            'offset': 0
        }
        empty_response = {
            'items': [],
            'total': 0,
            'limit': 50,
            'offset': 50
        }

        self.request_mock.side_effect = [
            (response_json, 200),
            (empty_response, 200)
        ]

        # iter / next
        counter = 0
        for track in album1:
            # contains
            self.assertIn(track, album1)

            # getitem
            self.assertIs(album1[counter], track)

            self.assertIsInstance(track, Track)
            counter += 1

        # len
        self.assertEqual(len(album1), counter)
        self.assertEqual(len(album1), 10)

        # reversed
        counter = len(album1) - 1
        for track in reversed(album1):
            self.assertIn(track, album1)
            self.assertIs(album1[counter], track)

            counter -= 1


    @unittest.skip('Not yet implemented')
    def test__update_fields(self):
        pass


    @unittest.skip('Not yet implemented')
    def test__update_tracks(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_spotify_id(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_type(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_artists(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_available_markets(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_copyright(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_genres(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_href(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_uri(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_images(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_label(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_name(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_popularity(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_release_date(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_tracks(self):
        pass


# This allows the tests to be executed
if __name__ == '__main__':
    unittest.main()

#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
from spotifython.track import Track
