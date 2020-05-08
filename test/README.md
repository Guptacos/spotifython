## Running tests
In order to run these tests, the following env variables must be defined:
- NO\_ACCESS\_TOKEN:  a Spotify access token with no authorizations
- ALL\_ACCESS\_TOKEN: a Spotify access token with all authorizations
- USER\_ID: The user id of the user who authorized the above tokens

These can be defined by doing `export NO_ACCESS_TOKEN=__token__`
The easiest way to get a developer access token is through any of the methods on
the developer console, such as [this
one.](https://developer.spotify.com/console/get-users-currently-playing-track/?market=&additional_types=)

While in the test directory, run 
`python -m unittest` to run all tests
`python -m unittest __filename__` to run a specific set of tests
`python -m unittest __filename__.classname.module` to run a specific test
You can read more about the python unittest framework
[here.](https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertRaises)


## Writing new test
For now, follow the format of the test\_user.py file on the user-implementation
branch. I will add more detailed instructions in the future.

__NOTE__: only print in your tests on failure.

### Untested Features
- Expired tokens: difficult to get an expired token, and bad practice to commit
    a token, even an expired one.
