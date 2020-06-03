Introduction
============

``Spotifython`` is an object-oriented Python wrapper for the Spotify `web api
<https://developer.spotify.com/documentation/web-api/reference/>`_. The object
structure of this library mirrors that of the Spotify `object model
<https://developer.spotify.com/documentation/web-api/reference/object-model/>`_,
and wraps the appropriate endpoints in useful instance methods.

``Spotifython`` currently supports Python 3.6+.

Motivation
**********

While other Python wrappers exist for the Spotify api, we felt that they had
a few flaws:

    * Library functions return the raw json object from Spotify. This has huge
      implications for client code:
        * Client programmer must have Spotify documentation open to decipher
          response json
        * If the Spotify ODM (the return json objects) changes - which it has
          done in the past - client code breaks
        * Client code ends up doing things like:
          ``imageURL = tracks[0]['track']['album']['images'][1]['url']``
          It's very easy for a programmer to accidentally type:
          ``imageURL = tracks[0]['track']['album']['images']['url']``
          by accident, and then be left scratching their head as to why their
          code is broken.
    * Non-object oriented approach leading to a flat and sprawling Python api.
      Library method calls end up transliterating Spotify's endpoints instead of
      using a logical relations between objects and methods, leading to messy
      and difficult to modularize client code.

This project was initially started by Niko Gupta, Eugene Luo, Rama Mannava,
Spencer Yu, and Aditya Raghuraman in the Spring of 2020. It was intended to be
our final project for our senior API design course.

Since then, Niko, Spencer, and Rama have built out the rest of the library.

Limitations
***********

- As my main use-case scenario was to simply connect two devices, the current
  version of :class:`simpleble.SimpleBleClient` has been designed and
  implemented with this use-case in mind. As such, if you are looking for
  a package to allow you to connect to multiple devices, then know that
  off-the-self this package DOES NOT allow you to do so. However, implementing
  such a feature is an easily achievable task, which has been planned for
  sometime in the near future and if there proves to be interest on the project,
  I would be happy to speed up the process.

- Only Read and Write operations are currently supported, but I am planning on
  adding Notifications soon.

- Although the interfacing operations of the :class:`bluepy.btle.Service` and
  :class:`bluepy.btle.Peripheral` classes have been brought forward to the
  :class:`simpleble.SimpleBleClient` class, the same has not been done for the
  :class:`bluepy.btle.Descriptor`, meaning that the
  :class:`simpleble.SimpleBleClient` cannot be used to directly access the
  Descriptors. This can however be done easily by obtaining a handle of
  a :class:`simpleble.SimpleBleDevice` object and calling the superclass
  :meth:`bluepy.btle.Peripheral.getDescriptors` method.
