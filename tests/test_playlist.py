""" Tests for the Playlist class. """

# pylint: disable=missing-docstring

# Standard library imports
import unittest
from unittest.mock import patch

# Local imports
from tests.help_lib import get_dummy_data
import spotifython.constants as const
import spotifython.utils as utils
from spotifython.session import Session

TOKEN = 'feebdaed'


class TestPlaylist(unittest.TestCase):


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
        playlist1 = get_dummy_data(const.PLAYLISTS, limit=1, to_obj=True)[0]
        playlist1_dup = get_dummy_data(const.PLAYLISTS, limit=1, to_obj=True)[0]

        # eq, hash
        self.assertEqual(playlist1, playlist1_dup)
        self.assertEqual(hash(playlist1), hash(playlist1_dup))
        self.assertIsNot(playlist1, playlist1_dup)

        # str, repr should return str and not raise exceptions
        self.assertIsInstance(playlist1.__str__(), str)
        self.assertIsInstance(playlist1.__repr__(), str)

        # Get a second playlist to compare for ne
        playlist2 = get_dummy_data(const.PLAYLISTS, limit=2, to_obj=True)[1]
        self.assertNotEqual(playlist1, playlist2)

        # insert tracks into playlist1
        # pylint: disable=protected-access
        playlist1._tracks = get_dummy_data(const.TRACKS, limit=10, to_obj=True)

        # iter / next
        counter = 0
        for track in playlist1:
            # contains
            self.assertIn(track, playlist1)

            # getitem
            self.assertIs(playlist1[counter], track)

            self.assertIsInstance(track, Track)
            counter += 1

        # len
        self.assertEqual(len(playlist1), counter)
        self.assertEqual(len(playlist1), 10)

        # reversed
        counter = len(playlist1) - 1
        for track in reversed(playlist1):
            self.assertIn(track, playlist1)
            self.assertIs(playlist1[counter], track)

            counter -= 1


    @unittest.skip('Not yet implemented')
    def test_refresh(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_raw(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_owner(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_uri(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_href(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_name(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_spotify_id(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_add_tracks(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_update_name(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_update_description(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_update_visibility(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_image(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_tracks(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_remove_tracks(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_reorder_tracks(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_replace_all_tracks(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_replace_image(self):
        pass


# This allows the tests to be executed
if __name__ == '__main__':
    unittest.main()

#pylint: disable=wrong-import-position
from spotifython.track import Track
