''' Tests for the Player class
'''
# These 2 statements are fine to include in your test file
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring

# Standard library imports
import unittest
from unittest.mock import patch

# Local imports
from tests.help_lib import get_dummy_data
import spotifython.constants as const
import spotifython.utils as utils

USER_ID = 'deadbeef'
TOKEN = 'feedbaed'


class TestPlayer(unittest.TestCase):


    def setUp(self):
        self.session = sp(TOKEN)
        # TODO: fix when sp.get_users() is merged
        self.user = User(self.session, {'id': USER_ID})
        self.player = self.user.player()

        # Mock the sp._request method so that we never actually reach Spotify
        self.patcher = patch.object(utils, 'request', autospec=True)

        # Add cleanup to unmock sp._request. Cleanup always called at end.
        self.addCleanup(self.patcher.stop)
        self.request_mock = self.patcher.start()


    @unittest.skip('Not yet implemented')
    def test_user(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_next(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_previous(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_pause(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_resume(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_play(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_is_paused(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_is_playing(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_get_currently_playing(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_available_devices(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_get_active_device(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_set_active_device(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_get_shuffle(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_set_shuffle(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_get_playback_position(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_set_playback_position(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_get_volume(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_set_volume(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_get_repeat(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_set_repeat(self):
        pass


    @unittest.skip('Not yet implemented')
    def test_enqueue(self):
        pass


# This allows the tests to be executed
if __name__ == '__main__':
    unittest.main()

#pylint: disable-wrong-import-position
#pylint: disable-wrong-import-order
from spotifython.user import User
