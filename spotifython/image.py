""" Image class """

# Standard library imports
import copy


class Image:
    """ Container class representing a Spotify image

    Use methods here to get information about an Image
    """

    def __init__(self, info):
        """ Get an instance of Image

        This constructor should never be called by the client. To get an
        instance of Image, use another object's image methods, such as
        Album.images(), User.image(), etc.

        Args:
            info (dict): the image's information. Must contain 'url'.
        """
        if 'url' not in info:
            raise ValueError('Image class init with no url')

        self._raw = copy.deepcopy(info)


    def __str__(self):
        return self._raw['url']


    def __repr__(self):
        return str(self)


    def url(self):
        """ Get the image's url

        Returns:
            str: the url
        """
        return self._raw['url']


    def width(self):
        """ Get the width of the image in pixels

        Returns:
            int: the width in pixels, if known
            None: if the width is not known
        """
        return self._raw.get('width', None)


    def height(self):
        """ Get the height of the image in pixels

        Returns:
            int: the height in pixels, if known
            None: if the height is not known
        """
        return self._raw.get('height', None)
