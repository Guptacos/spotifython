## Running tests
In order to run these tests, the following env variables must be defined:
- NO\_ACCESS\_TOKEN:  a Spotify access token with no authorizations
- ALL\_ACCESS\_TOKEN: a Spotify access token with all authorizations
- USER\_ID: The user id of the user who authorized the above tokens

These can be defined by doing `export NO_ACCESS_TOKEN=__token__`
The easiest way to get a developer access token is through any of the methods on
the developer console, such as [this
one.](https://developer.spotify.com/console/get-users-currently-playing-track/?market=&additional_types=)

`>>> python all_tests.py` to run all tests
`>>> python __test_name__` to run an individual test


## Writing new test
1. Create a new file (called foo.py for this example)
2. At the top of foo.py add `from base_testing import *`
3. Write your tests as a script, i.e. it should have a `main` function and
    ```python
    if __name__ == '__main__':
        main()
    ```
    at the bottom.
4. Add to the start of `main`: `print('Starting Foo tests')`
4. Add to the end of `main`: `print('Foo tests finished.')`
5. Add `import foo` at the top of all_tests.py
6. Add `foo` to test_files at the top of all_tests.py

__NOTE__: only print in your tests on failure.

### Untested Features
- Expired tokens: difficult to get an expired token, and bad practice to commit
    a token, even an expired one.
