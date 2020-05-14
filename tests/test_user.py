''' Tests for the User class

Note: these tests are not exhaustive and could always be improved. Since the
Spotify REST api is mocked, if it's functionality ever changes these tests may
become obsolete.

Last updated: May 14, 2020

'''
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring

# TODO: mock all the functions

# Standard library imports
import unittest
from unittest.mock import patch

# Local imports
from spotifython.spotifython import Spotifython as sp

USER_ID = ''
NO_ACCESS_TOKEN = ''
ALL_ACCESS_TOKEN = ''
INVALID_TOKEN = 'deadbeef'


class TestUser(unittest.TestCase):
    def setUp(self):
        self.session = sp(ALL_ACCESS_TOKEN)
        #TODO: fix when sp.get_users() is merged
        self.user = User(self.session, {'id': USER_ID})

        # Mock the sp._request method so that we never actually reach Spotify
        self.patcher = patch.object(sp, '_request', autospec=True)

        # Add cleanup to unmock sp._request. Cleanup always called at end.
        self.addCleanup(self.patcher.stop)
        self.request_mock = self.patcher.start()


    # Test that methods raise appropriate exns when given an unauthorized token.
    # TODO:
    @unittest.skip('Not yet implemented')
    def test_unauthorized_token(self):
        #session = sp(NO_ACCESS_TOKEN)
        #TODO: fix when sp.get_users() is merged
        #user = User(session, {'id': USER_ID})
        pass


    # Test that methods raise appropriate exns when given a bad token.
    # TODO:
    @unittest.skip('Not yet implemented')
    def test_invalid_token(self):
        pass


    # User.player
    def test_player(self):
        user = self.user
        self.assertIsInstance(user.player(), Player)


    # User.user_id
    def test_spotify_id(self):
        user = self.user
        uid = user.spotify_id()
        self.assertEqual(uid, USER_ID)


    # User.top
    def test_top(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.top, sp.PLAYLIST, 1)
        self.assertRaises(TypeError, user.top, sp.TRACK, 1, sp.ARTIST)
        self.assertRaises(TypeError, user.top, sp.TRACK, 1, 5)
        self.assertRaises(ValueError, user.top, sp.TRACK, -1)

        # Get top track
        # Want to mock items, limit, offset
        self.request_mock.return_value = (
            {},
            200
        )
        top = user.top(sp.TRACK, 1)
        self.assertLessEqual(len(top), 1)
        self.assertIsInstance(top[0], Track)

        # Get top artist
        top = user.top(sp.ARTIST, 1)
        self.assertIsInstance(top[0], Artist)

        # Get at most 55 top tracks
        top = user.top(sp.TRACK, 55)
        self.assertLessEqual(len(top), 55)


    # User.recently_played
    def test_recently_played(self):
        user = self.user

        # Validate input checking
        self.assertRaises(ValueError, user.recently_played, -1)
        self.assertRaises(ValueError, user.recently_played, 51)

        # Make sure you get at most 10 Tracks
        recently_played = user.recently_played(10)
        self.assertLessEqual(len(recently_played), 10)
        for elem in recently_played:
            self.assertIsInstance(elem, Track)


    # User.get_playlists
    # Note: this function requires you to have at least 3 playlists
    def test_get_playlists(self):
        user = self.user

        self.assertRaises(ValueError, user.get_playlists, -1)
        self.assertRaises(ValueError, user.get_playlists, 100123)

        # Make sure you get 1 Playlist
        playlist = user.get_playlists(1)
        self.assertEqual(len(playlist), 1)
        self.assertIsInstance(playlist[0], Playlist)

        playlists = user.get_playlists()
        total = len(playlists)
        print('\n%s has %d playlists in their library. Does this look right?'
              % (user, total))

        if total >= 2:
            minus_one = user.get_playlists(limit=total - 1)
            self.assertEqual(len(minus_one), total - 1)


    # Note: also manually tested, creates a playlist
    # User.create_playlist
    def test_create_playlist(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.create_playlist, 'test', sp.TRACK)

        self.request_mock.return_value = {}, 201
        # Make sure playlist creation returns the playlist
        # TODO: add integration test to check that playlist was created
        playlist = user.create_playlist('test',
                                        sp.PRIVATE,
                                        description='test playlist, pls del')
        self.assertIsInstance(playlist, Playlist)


    # User.is_following
    def test_is_following(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.is_following, sp.TRACK)
        self.assertRaises(TypeError, user.is_following, 5)

        playlists = user.get_following(sp.PLAYLIST)
        for playlist, following in user.is_following(playlists):
            self.assertTrue(following,
                            msg='%s in user.get_following(sp.PLAYLIST), but '
                                'False in user.is_following' % playlist)

        artists = user.get_following(sp.ARTIST)
        for artist, following in user.is_following(artists):
            self.assertTrue(following,
                            msg='%s in user.get_following(sp.ARTIST), but '
                                'False in user.is_following' % artist)


        # TODO: test following users
        # TODO: test failing cases
        # TODO: maybe mock this instead of hardcoding an artist?
        # TODO: this is messy... should it return a bool instead?
        art = Artist(None, {'id':'6GI52t8N5F02MxU0g5U69P'})
        result = user.is_following(art)
        self.assertFalse(result[0][1], msg='Apparently following Santana')


    # User.get_following
    def test_get_following(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.get_following, sp.USER, 10)
        self.assertRaises(TypeError, user.get_following, 5, limit=10)
        self.assertRaises(ValueError, user.get_following, sp.ARTIST, limit=-1)

        # Get all followed playlists
        playlists = user.get_following(sp.PLAYLIST)
        for elem in playlists:
            self.assertIsInstance(elem, Playlist)

        total_playlists = len(playlists)
        print('\n%s follows %d playlists. Does this look right?'
              % (user, total_playlists))

        if total_playlists >= 2:
            minus_one = user.get_following(sp.PLAYLIST,
                                           limit=total_playlists - 1)
            self.assertEqual(len(minus_one), total_playlists - 1)

        # Get all followed artists
        artists = user.get_following(sp.ARTIST)
        for elem in artists:
            self.assertIsInstance(elem, Artist)

        print('%s follows %d artists. Does this look right?'
              % (user, len(artists)))

    # User.has_saved
    def test_has_saved(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.has_saved, Playlist(None, {}))
        self.assertRaises(TypeError, user.has_saved, 5)

        # TODO: maybe mock this instead of hardcoding?
        # TODO: this is messy... should it return a bool instead?
        track = Track(None, {'id':'65rgrr0kAPjOkeWA2bDoUQ'})
        self.assertFalse(user.has_saved(track)[0][1],
                         msg='Apparently you have a random lofi song saved')


    # User.get_saved
    def test_get_saved(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.get_saved, sp.PLAYLIST)
        self.assertRaises(ValueError, user.get_saved, sp.TRACK, limit=-1)

        # TODO: test the market?

        # Get all saved tracks
        tracks = user.get_saved(sp.TRACK)
        total_tracks = len(tracks)
        print('\n%s has %d tracks in their library. Does this look right?'
              % (user, total_tracks))

        for elem in tracks:
            self.assertIsInstance(elem, Track)

        if total_tracks >= 2:
            minus_one = user.get_saved(sp.TRACK, limit=total_tracks - 1)
            self.assertEqual(len(minus_one), total_tracks - 1)

        # Get all saved albums
        albums = user.get_saved(sp.ALBUM)
        total_albums = len(albums)
        print('%s has %d albums in their library. Does this look right?'
              % (user, total_albums))

        for elem in albums:
            self.assertIsInstance(elem, Album)

        if total_albums >= 2:
            minus_one = user.get_saved(sp.ALBUM, limit=total_albums - 1)
            self.assertEqual(len(minus_one), total_albums - 1)


if __name__ == '__main__':
    unittest.main()

    # bad token, expired token, correct token

    # player
    # user_id
    # top
    # recently_played
    # get_playlists
    # create_playlist
    # is_following
    # get_following
    # has_saved
    # get_saved

    # follow
    # unfollow
    # save
    # remove

from spotifython.user import User
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.player import Player
from spotifython.playlist import Playlist
from spotifython.track import Track
