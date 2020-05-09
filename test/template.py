# This file is a template for how to write tests for this library
# The test are for the nonexistent 'DeadBeef' library, located in
# spotifython/deadbeef.py
#
# Note that this code doesn't compile as is because DeadBeef doesn't exist

from mock import patch
import unittest
import sys
sys.path.append('../spotifython')

from spotifython import Spotifython as sp
from deadbeef import DeadBeef


class TestDeadBeef(unittest.TestCase):


    # This function is called before every test_* function. Anything that is
    # needed by every test_* function should be stored in "self" here.
    def setUp(self):
        self.session = sp(ALL_ACCESS_TOKEN)
        self.deadbeef = self.session.get_beef({'id': 'deadbeef'})

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


    # This shows how to skip tests so they don't execute when running
    @unittest.skip("Not yet implemented")
    def test_beyond_beef(self):
        self.assertTrue(False)


    # This method shows how to actually mock
    # Here we will test the following imaginary function:
    # def mince(self, method: str, quantity: int)
    #
    # Note that the test function name doesn't have to mirror the function it's
    # testing; you can test any number of function within a test, as long as the
    # test function is prefixed by test_
    def test_mock_beef(self):
        beef = self.deadbeef

        # Input checking: can't mince beef with a spoon, and True isn't an int!
        self.assertRaises(TypeError, beef.mince, sp.SPOON, True)

        # Now we mock the _request method. The next time _request is called (and
        # every time afterwards that it's called in this test until it's
        # changed) it will return ({}, 200) to the DeadBeef library.
        self.request_mock.return_value = {}, 200

        minced = beef.mince(sp.KNIFE, quantity=10)
        self.assertIsInstance(minced, DeadBeef)
        self.assertEqual(minced.weight, 100)


# This allows the tests to be executed
if __name__ == '__main__':
    unittest.main()
