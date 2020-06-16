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
import spotifython.utils as utils

ARTIST_ID = 'deadbeef'
TOKEN = 'feebdaed'

class TestArtist(unittest.TestCase):

    # This function is called before every test_* function. Anything that is
    # needed by every test_* function should be stored in 'self' here.
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

        self.assertTrue(all((isinstance(genre, str) for genre in x.genres()) \
                        for x in [artist_0, artist_1])
                        )
        self.assertTrue(all(
                        isinstance(x.href(), str) for x in [artist_0, artist_1])
                        )
        self.assertTrue(all(isinstance(x.spotify_id(), str) \
                        for x in [artist_0, artist_1]))
        self.assertTrue(all(isinstance(x.name(), str) \
                        for x in [artist_0, artist_1]))
        self.assertTrue(all(isinstance(x.popularity(), int) \
            for x in [artist_0, artist_1]))
        self.assertTrue(all(isinstance(x.uri(), str) \
                        for x in [artist_0, artist_1]))

    # Test _update_fields()
    def test_update_fields(self):
        self.request_mock.return_value = (
            get_dummy_data(const.ARTISTS, limit=1)[0],
            200
        )
        expected_artist = get_dummy_data(
            const.ARTISTS,
            limit=1,
            to_obj=True
        )[0]
        artist = Artist(
            session=self.session,
            info={
                'id': expected_artist.spotify_id()
            }
        )

        # Check state before updating the fields
        self.assertTrue(artist == expected_artist)
        # pylint: disable=protected-access
        self.assertEqual(artist._raw.__len__(), 1)

        # Check state after updating the fields
        artist._update_fields()
        self.assertTrue(artist == expected_artist)
        # pylint: disable=protected-access
        self.assertEqual(artist._raw.__len__(), expected_artist._raw.__len__())

    # Test albums()
    def test_albums(self):
        search_limit = 100
        expected_albums_json = get_dummy_data(
            const.ALBUMS,
            limit=search_limit,
        )
        expected_albums = get_dummy_data(
            const.ALBUMS,
            limit=search_limit,
            to_obj=True
        )
        self.request_mock.side_effect = [
            (
                {
                    'href': 'href_uri',
                    'items': expected_albums_json[:50],
                    'limit': 50,
                    'next': 'next_here',
                    'offset': 0,
                    'previous': 'previous_uri',
                    'total': 100,
                },
                200
            ),
            (
                {
                    'href': 'href_uri',
                    'items': expected_albums_json[50:100],
                    'limit': 50,
                    'next': 'next_here',
                    'offset': 50,
                    'previous': 'previous_uri',
                    'total': 100,
                },
                200
            ),
            (
                {
                    'href': 'href_uri',
                    'items': [],
                    'limit': 50,
                    'next': None,
                    'offset': 100,
                    'previous': 'previous_uri',
                    'total': 100,
                },
                200
            )
        ]
        artist = get_dummy_data(const.ARTISTS, limit=1, to_obj=True)[0]
        albums = artist.albums(search_limit=search_limit)
        self.assertEqual(albums, expected_albums)

    # Test top_tracks()
    def test_top_tracks(self):
        self.request_mock.return_value = (
            {
                'tracks': get_dummy_data(const.TRACKS, limit=10)
            },
            200
        )
        expected_tracks = get_dummy_data(const.TRACKS, limit=10, to_obj=True)
        artist = get_dummy_data(const.ARTISTS, limit=1, to_obj=True)[0]
        tracks = artist.top_tracks()
        self.assertEqual(tracks, expected_tracks)

    # Test related_artists()
    def test_related_artists(self):
        self.request_mock.return_value = (
            {
                'artists': get_dummy_data(const.ARTISTS, limit=20)
            },
            200
        )
        expected_artists = get_dummy_data(const.ARTISTS, limit=20, to_obj=True)
        artist = get_dummy_data(const.ARTISTS, limit=1, to_obj=True)[0]
        related_artists = artist.related_artists()
        self.assertEqual(related_artists, expected_artists)

# This allows the tests to be executed
if __name__ == '__main__':
    unittest.main()

#pylint: disable=wrong-import-position
#pylint: disable=wrong-import-order
from spotifython.artist import Artist
from spotifython.session import Session
