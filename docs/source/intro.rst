Introduction
============

``Spotifython`` is an object-oriented Python wrapper for the Spotify `web API
<https://developer.spotify.com/documentation/web-api/reference/>`_. The object
structure of this library mirrors that of the Spotify `object model
<https://developer.spotify.com/documentation/web-api/reference/object-model/>`_,
and wraps the appropriate endpoints in useful instance methods.

``Spotifython`` currently supports Python 3.6+.

Motivation
**********

While other Python wrappers exist for the Spotify API, we felt that they had
a few flaws:

    * Library functions return the raw JSON object from Spotify. This has huge
      implications for client code:

        * Client programmer must have Spotify documentation open to decipher
          response JSON
        * If the Spotify ODM (the return JSON objects) changes - which it has
          done in the past - client code breaks
        * Client code ends up doing things like:
          ``imageURL = tracks[0]['track']['album']['images'][1]['url']``
          It's very easy for a programmer to type:
          ``imageURL = tracks[0]['track']['album']['images']['url']``
          by accident, and then be left scratching their head as to why their
          code is broken.

    * Non-object oriented approach leading to a flat and sprawling Python API.
      Library method calls end up transliterating Spotify's endpoints instead of
      using a logical relations between objects and methods, leading to messy
      and difficult to modularize client code.

This project was initially started by Niko Gupta, Eugene Luo, Rama Mannava,
Spencer Yu, and Aditya Raghuraman in the Spring of 2020. It was intended to be
our final project for our senior API design course at Carnegie Mellon.

Since then, Niko, Spencer, and Rama have built out the rest of the library.

Limitations
***********

Since this is still the first version of the library, certain features are not
supported. We aimed to get the base funcitonality out before implementing extra
features.

- Certain fields accessible from the raw Spotify JSON are not accessible through
  our library.
- Shows and Episodes are not yet supported
- Browse is not yet supported
- There is no support for Spotify authentication pipelines; the library assumes
  the client already has a Spotify token.

Despite these limitations, we believe that the library can help cover a large
number of use cases. We also have plans to implement the above features in the
near future.
