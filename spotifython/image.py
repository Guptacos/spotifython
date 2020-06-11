""" Image class. """

# Standard library imports
import copy

class Image:
    """ Container class representing a Spotify image

    Do not use the constructor. To get an
    instance of Image, use another object's image methods, such as
    :meth:`Album.images() <spotifython.album.Album.images>`,
    :meth:`Playlist.image() <spotifython.playlist.Playlist.image>`,
    :meth:`User.image() <spotifython.user.User.image>`, etc.
    """

    def __init__(self, info):
        """ Get an instance of Image. Client should not use the constructor!

        Args:
            info (dict): the image's information. Must contain 'url'.
        """
        if 'url' not in info:
            raise ValueError('Image class init with no url')

        self._raw = copy.deepcopy(info)


    def __str__(self):
        """ Returns the image url. """
        return self._raw['url']


    def __repr__(self):
        """ Returns the image url. """
        return str(self)


    def url(self):
        """
        Returns:
            str: The image's url.
        """
        return self._raw['url']


    def width(self):
        """
        Returns:
            Union[int, None]: The width in pixels, if known.
        """
        return self._raw.get('width', None)


    def height(self):
        """
        Returns:
            Union[int, None]: The height in pixels, if known.
        """
        return self._raw.get('height', None)
