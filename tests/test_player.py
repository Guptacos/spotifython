''' Tests for the Player class
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

USER_ID = 'deadbeef'
TOKEN = 'feedbaed'


class TestPlayer(unittest.TestCase):


    def setUp(self):
        self.session = Session(TOKEN)
        # TODO: fix when sp.get_users() is merged
        self.user = User(self.session, {'id': USER_ID})
        self.player = self.user.player()

        # Mock the sp._request method so that we never actually reach Spotify
        self.patcher = patch.object(utils, 'request', autospec=True)

        # Add cleanup to unmock sp._request. Cleanup always called at end.
        self.addCleanup(self.patcher.stop)
        self.request_mock = self.patcher.start()


    def test_user(self):
        self.assertEqual(self.user, self.player.user())


    @unittest.skip('Not yet implemented')
    def test__player_data(self):
        # Should also test the SpotifyError
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


class TestContext(unittest.TestCase):


    def test_init(self):
        # Get objects
        tracks = get_dummy_data(const.TRACKS, 5, True)
        artist = get_dummy_data(const.ARTISTS, 1, True)[0]
        album = get_dummy_data(const.ALBUMS, 1, True)[0]
        playlist = get_dummy_data(const.PLAYLISTS, 1, True)[0]

        # Should all pass
        Context(tracks)
        Context(artist)
        Context(album)
        Context(playlist)

        # Should fail
        self.assertRaises(TypeError, Context, tracks[0])
        self.assertRaises(TypeError, Context, tracks + [artist])
        self.assertRaises(ValueError, Context, tracks, -1)
        self.assertRaises(ValueError, Context, tracks, 10)
        self.assertRaises(ValueError, Context, tracks[:3], tracks[4])


    def test_eq(self):
        # Get objects
        tracks = get_dummy_data(const.TRACKS, 5, True)
        album = get_dummy_data(const.ALBUMS, 1, True)[0]

        self.assertEqual(Context(album), Context(album))
        self.assertEqual(Context(tracks), Context(tracks))
        self.assertEqual(Context(tracks, 3), Context(tracks, 3))
        self.assertNotEqual(Context(tracks, 2), Context(tracks, 3))
        self.assertNotEqual(Context(album, 3), Context(tracks, 3))


    def test_accessors(self):
        # Test basic accessor equality
        tracks = get_dummy_data(const.TRACKS, 5, True)
        cont = Context(tracks, 4)
        self.assertEqual(cont.item(), tracks)
        self.assertEqual(cont.offset(), 4)

        # Test passing a Track as offset
        tracks = get_dummy_data(const.TRACKS, 5, True)
        cont = Context(tracks, tracks[2])
        self.assertEqual(cont.offset(), 2)

        # Test a different type for item
        album = get_dummy_data(const.ALBUMS, 1, True)[0]
        cont = Context(album)
        self.assertEqual(cont.item(), album)


# This allows the tests to be executed
if __name__ == '__main__':
    unittest.main()

#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
from spotifython.user import User
from spotifython.player import Player, Context
