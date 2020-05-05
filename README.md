# Spotifython
Python library for interfacing with the Spotify REST api

## Getting Started
TODO: how to get this set up as a pip installable package?

## Read our docs
TODO: add docs to wiki or something

## Important notes:
This library does not currently support all of the functionality provided by
Spotify's REST api. See here (TODO: create unsupported wiki page) for more
information about what specific functionality is and isn't supported. If you
find that certain functionality isn't supported, please reach out (TODO). You
can also use the [Spotipy](https://github.com/plamere/spotipy) library, which
currently supports a larger number of Spotify's endpoints than Spotifython does.

At the end of the day, this library is a wrapper for a REST api. It does its
best to hide this fact from the user, however, sometimes this is impossible.
Each function lists in its function docstring the Spotify token scopes that
could be required for proper use of that function. For more specific details on
what combination of arguments necesitates which scopes, see the
[Spotify developer docs](https://developer.spotify.com/documentation/web-api/reference/)
and find the endpoint you are interested in.

## Contributing
TODO: Are others allowed to contribute?

