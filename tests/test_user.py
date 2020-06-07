""" Tests for the User class

Note: these tests are not exhaustive and could always be improved. Since the
Spotify REST api is mocked, if its functionality ever changes these tests may
become obsolete.

Last updated: May 14, 2020

"""
#pylint: disable=missing-class-docstring
#pylint: disable=missing-function-docstring

# Standard library imports
import random
import unittest
from unittest.mock import patch

# Local imports
from tests.help_lib import get_dummy_data
import spotifython.constants as const
import spotifython.utils as utils

USER_ID = 'deadbeef'
TOKEN = 'feebdaed'


class TestUser(unittest.TestCase):


    def setUp(self):
        self.session = sp(TOKEN)
        #TODO: fix when sp.get_users() is merged
        self.user = User(self.session, {'id': USER_ID})

        # Mock the sp._request method so that we never actually reach Spotify
        self.patcher = patch.object(utils, 'request', autospec=True)

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


    # User.spotify_id
    def test_spotify_id(self):
        user = self.user
        uid = user.spotify_id()
        self.assertEqual(uid, USER_ID)


    # User.top
    def test_top(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.top, const.PLAYLISTS, 1)
        self.assertRaises(TypeError, user.top, const.TRACKS, 1, const.ARTISTS)
        self.assertRaises(TypeError, user.top, const.TRACKS, 1, 5)
        self.assertRaises(ValueError, user.top, const.TRACKS, -1)

        # Get top track
        # Want to mock items, limit, offset
        self.request_mock.return_value = (
            {'items': get_dummy_data(const.TRACKS, 1),
             'offset': 0,
             'limit': 1},
            200
        )
        top = user.top(const.TRACKS, 1)
        self.assertLessEqual(len(top), 1)
        for elem in top:
            self.assertIsInstance(elem, Track)

        # Get top artist
        self.request_mock.return_value = (
            {'items': get_dummy_data(const.ARTISTS, 1),
             'offset': 0,
             'limit': 1},
            200
        )
        top = user.top(const.ARTISTS, 1)
        self.assertLessEqual(len(top), 1)
        for elem in top:
            self.assertIsInstance(elem, Artist)

        # Get at most 55 top tracks
        top_tracks = get_dummy_data(const.TRACKS, 100)
        self.request_mock.side_effect = [
            ({'items': top_tracks[:50],
              'offset': 0,
              'limit': 50},
             200),
            ({'items': top_tracks[50:],
              'offset': 50,
              'limit': 50},
             200)
        ]
        top = user.top(const.TRACKS, 55)
        self.assertLessEqual(len(top), 55)


    # User.recently_played
    def test_recently_played(self):
        user = self.user

        # Validate input checking
        self.assertRaises(ValueError, user.recently_played, -1)
        self.assertRaises(ValueError, user.recently_played, 51)

        # Make sure you get at most 10 Tracks
        self.request_mock.return_value = (
            {'items': get_dummy_data(const.TRACKS, 10)},
            200
        )
        recently_played = user.recently_played(10)
        self.assertLessEqual(len(recently_played), 10)
        for elem in recently_played:
            self.assertIsInstance(elem, Track)


    # User.get_playlists
    # Note: this function requires you to have at least 3 playlists
    def test_get_playlists(self):
        user = self.user

        self.assertRaises(ValueError, user.get_playlists, -1)
        self.assertRaises(ValueError, user.get_playlists, 100001)

        # Make sure you get 1 Playlist
        self.request_mock.side_effect = [
            ({'items': get_dummy_data(const.PLAYLISTS, 1),
              'offset': 0,
              'limit': 50},
             200),
            ({'items': []},
             200),
        ]
        playlist = user.get_playlists(1)
        self.assertEqual(len(playlist), 1)
        self.assertIsInstance(playlist[0], Playlist)

        self.request_mock.side_effect = [
            ({'items': get_dummy_data(const.PLAYLISTS, 38),
              'offset': 0,
              'limit': 50},
             200),
            ({'items': []},
             200)
        ]
        playlists = user.get_playlists()
        self.assertEqual(len(playlists), 38)

        self.request_mock.side_effect = [
            ({'items': get_dummy_data(const.PLAYLISTS, 37),
              'offset': 0,
              'limit': 50},
             200),
            ({'items': []},
             200)
        ]
        playlists = user.get_playlists(37)
        self.assertEqual(len(playlists), 37)


    # Note: also manually tested, creates a playlist
    # User.create_playlist
    def test_create_playlist(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.create_playlist, 'test', const.TRACKS)

        to_make = get_dummy_data(const.PLAYLISTS, 1)[0]
        self.request_mock.return_value = to_make, 201

        # Make sure playlist creation returns the playlist
        new_playlist = user.create_playlist(to_make['name'],
                                            const.PRIVATE,
                                            description=to_make['description'])

        self.assertIsInstance(new_playlist, Playlist)
        self.assertEqual(new_playlist.name(), to_make['name'])


    # User.is_following
    @unittest.skip('not yet mocked')
    def test_is_following(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.is_following, const.TRACKS)
        self.assertRaises(TypeError, user.is_following, 5)

        self.request_mock.side_effect = [
            ({'items': get_dummy_data(const.PLAYLISTS, 10)}, 200),
            ([True]*10, 200)
        ]

        # Note: current
        playlists = user.get_following(const.PLAYLISTS)
        self.assertEqual(len(playlists), 0)

        self.request_mock.side_effect = [
            ({'items': get_dummy_data(const.ARTISTS, 10)}, 200),
            ([True]*10, 200)
        ]
        artists = user.get_following(const.ARTISTS)
        self.assertTrue(all(user.is_following(artists)))


        # TODO: test following users
        # TODO: test failing cases
        # TODO: maybe mock this instead of hardcoding an artist?
        # TODO: this is messy... should it return a bool instead?


    # User.get_following
    @unittest.skip('not yet mocked')
    def test_get_following(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.get_following, const.USERS, 10)
        self.assertRaises(TypeError, user.get_following, 5, limit=10)
        self.assertRaises(ValueError,
                          user.get_following,
                          const.ARTISTS,
                          limit=-1)

        # Get all followed playlists
        playlists = user.get_following(const.PLAYLISTS)
        for elem in playlists:
            self.assertIsInstance(elem, Playlist)

        total_playlists = len(playlists)
        print('\n%s follows %d playlists. Does this look right?'
              % (user, total_playlists))

        if total_playlists >= 2:
            minus_one = user.get_following(const.PLAYLISTS,
                                           limit=total_playlists - 1)
            self.assertEqual(len(minus_one), total_playlists - 1)

        # Get all followed artists
        artists = user.get_following(const.ARTISTS)
        for elem in artists:
            self.assertIsInstance(elem, Artist)

        print('%s follows %d artists. Does this look right?'
              % (user, len(artists)))

    # User.has_saved
    def test_has_saved(self):
        user = self.user

        # Validate input checking
        playlist = get_dummy_data(const.PLAYLISTS, 1)[0]
        self.assertRaises(TypeError, user.has_saved, playlist)
        self.assertRaises(TypeError, user.has_saved, 5)


        # Build some objects to check
        tracks = get_dummy_data(const.TRACKS)
        tracks = list(map(lambda elem: Track(None, elem), tracks))
        albums = get_dummy_data(const.ALBUMS)
        albums = list(map(lambda elem: Album(None, elem), albums))

        other = tracks + albums
        random.shuffle(other)

        # Return correct number of values depending on input
        #pylint: disable=unused-argument
        def request_mock_return(session,
                                request_type,
                                endpoint,
                                body,
                                uri_params):
            ret_len = len(tracks) if 'tracks' in endpoint else len(albums)
            return [True]*ret_len, 200

        self.request_mock.side_effect = request_mock_return

        self.assertTrue(all(user.has_saved(other)))


    # User.get_saved
    def test_get_saved(self):
        user = self.user

        # Validate input checking
        self.assertRaises(TypeError, user.get_saved, const.PLAYLISTS)
        self.assertRaises(ValueError, user.get_saved, const.TRACKS, limit=-1)

        # Test getting tracks
        dummy_tracks = get_dummy_data(const.TRACKS, 101)
        self.request_mock.side_effect = [
            ({'items': dummy_tracks[:50]}, 200),
            ({'items': dummy_tracks[50:100]}, 200),
            ({'items': dummy_tracks[100:]}, 200),
            ({'items': []}, 200)
        ]

        tracks = user.get_saved(const.TRACKS)
        self.assertEqual(101, len(tracks))
        for elem in tracks:
            self.assertIsInstance(elem, Track)

        self.request_mock.side_effect = [
            ({'items': dummy_tracks[:50]}, 200),
            ({'items': dummy_tracks[51:100]}, 200),
            ({'items': dummy_tracks[100]}, 200),
            ({'items': []}, 200)
        ]
        self.assertEqual(99, len(user.get_saved(const.TRACKS, limit=99)))

        # Test getting tracks
        dummy_albums = get_dummy_data(const.ALBUMS, 75)
        self.request_mock.side_effect = [
            ({'items': dummy_albums[:50]}, 200),
            ({'items': dummy_albums[50:]}, 200),
            ({'items': []}, 200)
        ]

        albums = user.get_saved(const.ALBUMS)
        self.assertEqual(75, len(albums))
        for elem in albums:
            self.assertIsInstance(elem, Album)

        self.request_mock.side_effect = [
            ({'items': dummy_albums[:50]}, 200),
            ({'items': dummy_albums[51:]}, 200),
            ({'items': []}, 200)
        ]
        self.assertEqual(73, len(user.get_saved(const.ALBUMS, limit=73)))


    def test_follow(self):
        user = self.user

        artists = get_dummy_data(const.ARTISTS, 10, to_obj=True)
        artist_ids = utils.map_ids(artists)
        tracks = get_dummy_data(const.TRACKS, 10, to_obj=True)
        playlists = get_dummy_data(const.PLAYLISTS, 10, to_obj=True)

        # Validate input checking
        self.assertRaises(TypeError, user.follow, tracks)

        # Make sure following artists does what's expected
        #pylint: disable=unused-argument
        def request_mock_return(session,
                                request_type,
                                endpoint,
                                body,
                                uri_params):
            self.assertEqual(request_type, const.REQUEST_PUT)
            self.assertIsNotNone(uri_params)
            self.assertTrue('ids' in uri_params)
            for elem in uri_params['ids']:
                self.assertIsInstance(elem, str)
                self.assertTrue(elem in artist_ids)
            return None, 204

        self.request_mock.side_effect = request_mock_return
        user.follow(artists)

        # Should not raise exception - expects code 200 for playlists
        self.request_mock.side_effect = [(None, 200)]*10
        user.follow(playlists)


    def test_unfollow(self):
        user = self.user

        artists = get_dummy_data(const.ARTISTS, 10, to_obj=True)
        artist_ids = utils.map_ids(artists)
        tracks = get_dummy_data(const.TRACKS, 10, to_obj=True)
        playlists = get_dummy_data(const.PLAYLISTS, 10, to_obj=True)

        # Validate input checking
        self.assertRaises(TypeError, user.unfollow, tracks)

        # Make sure unfollowing artists does what's expected
        #pylint: disable=unused-argument
        def request_mock_return(session,
                                request_type,
                                endpoint,
                                body,
                                uri_params):
            self.assertEqual(request_type, const.REQUEST_DELETE)
            self.assertIsNotNone(uri_params)
            self.assertTrue('ids' in uri_params)
            for elem in uri_params['ids']:
                self.assertIsInstance(elem, str)
                self.assertTrue(elem in artist_ids)
            return None, 204

        self.request_mock.side_effect = request_mock_return
        user.unfollow(artists)

        # Should not raise exception - expects code 200 for playlists
        self.request_mock.side_effect = [(None, 200)]*10
        user.unfollow(playlists)


    def test_save(self):
        user = self.user

        albums = get_dummy_data(const.ALBUMS, 10, to_obj=True)
        album_ids = utils.map_ids(albums)
        tracks = get_dummy_data(const.TRACKS, 10, to_obj=True)
        playlists = get_dummy_data(const.PLAYLISTS, 10, to_obj=True)

        # Validate input checking
        self.assertRaises(TypeError, user.save, playlists)

        # Make sure saving albums does what's expected
        #pylint: disable=unused-argument
        def request_mock_return(session,
                                request_type,
                                endpoint,
                                body,
                                uri_params):
            self.assertEqual(request_type, const.REQUEST_PUT)
            self.assertIsNotNone(uri_params)
            self.assertTrue('ids' in uri_params)
            for elem in uri_params['ids']:
                self.assertIsInstance(elem, str)
                self.assertTrue(elem in album_ids)
            return None, 201

        self.request_mock.side_effect = request_mock_return
        user.save(albums)

        # Should not raise exception - expects code 200 for tracks
        self.request_mock.side_effect = [(None, 200)]*10
        user.save(tracks)


    def test_remove(self):
        user = self.user

        albums = get_dummy_data(const.ALBUMS, 10, to_obj=True)
        album_ids = utils.map_ids(albums)
        tracks = get_dummy_data(const.TRACKS, 10, to_obj=True)
        playlists = get_dummy_data(const.PLAYLISTS, 10, to_obj=True)

        # Validate input checking
        self.assertRaises(TypeError, user.remove, playlists)

        # Make sure saving albums does what's expected
        #pylint: disable=unused-argument
        def request_mock_return(session,
                                request_type,
                                endpoint,
                                body,
                                uri_params):
            self.assertEqual(request_type, const.REQUEST_DELETE)
            self.assertIsNotNone(uri_params)
            self.assertTrue('ids' in uri_params)
            for elem in uri_params['ids']:
                self.assertIsInstance(elem, str)
                self.assertTrue(elem in album_ids)
            return None, 200

        self.request_mock.side_effect = request_mock_return
        user.remove(albums)

        # Should not raise exception - expects code 200 for playlists
        self.request_mock.side_effect = [(None, 200)]*10
        user.remove(tracks)

if __name__ == '__main__':
    unittest.main()
    # TODO: bad token, expired token, correct token
    # TODO: Exceptions?

#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
from spotifython.album import Album
from spotifython.artist import Artist
from spotifython.player import Player
from spotifython.playlist import Playlist
from spotifython.track import Track
from spotifython.user import User
from spotifython.session import Session as sp
