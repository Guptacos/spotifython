## Running tests
To run all tests, run `make test` while in the top level directory

To run specific tests, run:
`python -m unittest tests.__filename__` to run all tests in a specific file
`python -m unittest tests.__filename__.classname.module` to run a specific test
You can read more about the python unittest framework
[here](https://docs.python.org/3/library/unittest.html), including the variety
of assert statements available to use in your tests.


## Writing a new test
Take a look at template.py, and use that as a base to create unit tests for your
class.

__NOTE__: only print in your tests on failure.
