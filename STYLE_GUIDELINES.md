# Coding style guidelines for this project

This project for the most part follows the
[Google style guidelines](http://google.github.io/styleguide/pyguide.html)
for Python.

The main difference is that we only use single quotes `'` for strings, and
triple double quotes `"""` for docstrings.

Additional guidelines:
- Function docstrings must contain the following additional sections:
    - Required token scopes: the Spotify scopes necessary for the function to be
      used successfully, such as `user=library-modify`
    - Calls endpoints: a list of endpoints that this function may call.
    - Calls functions: if your function uses other functions in the library that
      also call Spotify endpoints, that should be noted here so users can make
      sure to have appropriate scopes and endpoints.
