### Development
To run the linter, run `make lint`

### Packaging
Before packaging, make sure all information (such as version and development
status) is up to date in setup.py

1. To build the Pypi package, run the following:
    ```
    python setup.py sdist bdist_wheel
    ```
    `sdist` builds the distribution directory, and `bdist\_wheel` builds the
    wheel for faster installs.
2. Both `egg-info` (describes package information), and `build` (temp directory
   for setuptools) are unneeded, so clean up:
    ```
    python setup.py clean --all # Removes build dir
    rm -r *.egg-info
    ```
3. Make sure the README files in the package fit Pypi's requirements:
    ```
    twine check dist/*
    ```

4. Follow the instructions found
   [here](https://packaging.python.org/guides/distributing-packages-using-setuptools/#uploading-your-project-to-pypi)
   to upload to Pypi, or
   [here](https://packaging.python.org/guides/using-testpypi/#using-test-pypi)
   to upload to the Pypi test instance.

5. Once the package is uploaded, you can safely delete the dist directory:
    ```
    rm -r dist
    ```

### Todo
- Look into autocleanup of build directories, see
  [this](https://github.com/pypa/setuptools/issues/1347) github issue for
  setuptools.
- Update documentation link in setup.py once documentation is set up
- Update the version and 'development status' in setup.py once ready for release
