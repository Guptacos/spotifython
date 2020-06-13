Terms
=====

This page includes terms used throughout the documentation or code that are not
immediately intuitive. This is where to find more detailed explanations and
further resources for reading.

.. glossary::
    :sorted:

    Market
      An ISO 3166-1 alpha-2 country code as defined
      `here <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`__.

      Any method that takes market as a parameter passes it on to Spotify, and
      returns results specific to that region. If the method also accepts None,
      Spotify's default behavior will be used.

      If sp.TOKEN_REGION is given as a market code, Spotify will use appropriate
      country code for client based on their authorization token and location.

      Note: Market codes are primarily used for track relinking.

    Track Relinking
      The availability of a track depends on the country registered in the user’
      s Spotify profile settings. Often Spotify has several instances of a track
      in its catalogue, each available in a different set of markets. This
      commonly happens when the track the album is on has been released multiple
      times under different licenses in different markets.

      These tracks are linked together so that when a user tries to play a track
      that isn’t available in their own market, the Spotify mobile, desktop, and
      web players try to play another instance of the track that is available in
      the user’s market.

      If sp.TOKEN_REGION is given, will use the appropriate country code for the
      client based on the user's authorization token and location.
      
      See `here <https://developer.spotify.com/documentation/general/guides/track-relinking-guide/>`__ for more information.
