## Running tests
While in the top level directory, run
`python -m unittest tests` to run all tests
`python -m unittest tests.__filename__` to run a specific set of tests
`python -m unittest tests.__filename__.classname.module` to run a specific test
You can read more about the python unittest framework
[here](https://docs.python.org/3/library/unittest.html), including the variety
of assert statements available to use in your tests.


## Writing a new test
Take a look at template.py, and use that as a base to create unit tests for your
class.

__NOTE__: only print in your tests on failure.
