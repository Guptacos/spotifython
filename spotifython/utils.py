"""
Helper utilities for the spotifython library. These should not be used by client
code.
"""

# Standard library imports
import math

# Third party imports
import requests

# Local imports
from spotifython.endpoints import Endpoints
import spotifython.constants as const

# Exceptions
#pylint: disable=unnecessary-pass, line-too-long, protected-access
class AuthenticationError(Exception):
    """ Used when the token fails to authenticate with Spotify
    """
    pass

class NetworkError(Exception):
    """ Used when the network fails
    """
    pass

class SpotifyError(Exception):
    """ Used when Spotify fails for an unknown reason
    """
    pass

def get_field(obj, field):
    """ Gets the field if present in the Spotify object. If the field is not
    present, then the object is updated using the object's Spotify id. Will
    raise SpotifyError if the field is still invalid post-update.
    Args:
        obj: Union[Album, Artist, Player, Playlist, Session, Track, User], the
            instance of the object that the update call is meant for. The object
            should implement a obj._update_fields() method that updates the
            object based on its Spotify ID.
        field: str, the name of the field that is to be updated based on the
            object's Spotify id.
    """
    # TODO: add type checking for obj after we figure out the circular
    # dependency problem out.

    if not isinstance(field, str):
        raise TypeError(field)

    if field not in obj._raw:
        return update_and_get_field(obj, field)

    return obj._raw.get(field)

def update_and_get_field(obj, field):
    """ Updates the field if not present in the Spotify object and checks
    if the field is present afterwards. If it is not present, then raise
    SpotifyError.
    Args:
        obj: Union[Album, Artist, Player, Playlist, Session, Track, User], the
            instance of the object that the update call is meant for. The object
            should implement a obj._update_fields() method that updates the
            object based on its Spotify ID.
        field: str, the name of the field that is to be updated based on the
            object's Spotify id.
    """
    # TODO: add type checking for obj after we figure out the circular
    # dependency problem out.

    if not isinstance(field, str):
        raise TypeError(field)

    obj._update_fields()
    if field not in obj._raw:
        raise SpotifyError(field)

    return obj._raw.get(field)

##################################
# HTTP REQUEST
##################################
# TODO: https://stackoverflow.com/questions/23267409/how-to-implement-retry-mechanism-into-python-requests-library

def request(session,
            request_type,
            endpoint,
            body=None,
            uri_params=None):
    """ Does HTTP request with retry to a Spotify endpoint.
    This method should return a tuple (response_json, status_code) if the
    request is executed, and raises an Exception if the request type is invalid.

    Args:
        request_type: one of sp.REQUEST_GET, sp.REQUEST_POST, sp.REQUEST_PUT,
            sp.REQUEST_DELETE.
        endpoint: the Spotify uri to request
        body: (dict) the body to send as part of the request
        uri_params: (dict) the params to encode in the uri

    Returns:
        The response JSON and status code from Spotify. If the response contains
        invalid JSON or no content, response_json=None.

    Exceptions:
        Raises an HTTPError object in the event of an unsuccessful web request.
        All exceptions are as according to requests.Request.
    """
    request_uri = Endpoints.BASE_URI + endpoint
    headers = {
        'Authorization': 'Bearer ' + session.token(),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request(request_type,
                                request_uri,
                                json=body,
                                params=uri_params,
                                headers=headers,
                                timeout=session.timeout())

    # Raises HTTPError if request unsuccessful
    response.raise_for_status()

    # TODO: spotify response header 'retry-after'

    # r.json() raises ValueError if no content - this is not an error
    try:
        content = response.json()
    except ValueError:
        content = None

    return content, response.status_code


# TODO: partial failure?
def paginate_get(session,
                 limit,
                 return_class,
                 endpoint,
                 uri_params=None,
                 body=None):
    #pylint: disable=too-many-arguments
    """ Used to get a large number of objects from Spotify
    Note: does a GET request

    E.g: getting all of a user's saved songs. In this case, Spotify limits
         requests to size 50. This function will use the uri param 'offset' to
         paginate requests and get at most 'limit' many objects for the caller.
         These return objects are turned into 'return_class' objects.

    Keyword arguments:
        limit: (int) the maximum number of items to return
        return_class: the class to construct for the list contents.
            Constructor must have signature: func(self, session_obj, known_vals)
        endpoint: (str) the endpoint to call.
            The Spotify endpoint must accept 'limit' and 'offset' in uri_params
            Return json must contain key 'items'
        uri_params: (dict) the uri parameters for the request
        body: (dict) the body of the call

    Return:
        A list of objects of type return_class
    """
    # Init params
    uri_params = dict() if uri_params is None else uri_params
    body = dict() if body is None else body

    # Execute requests
    results = []

    # TODO: if any spotify page sizes are are a different value, make a param
    uri_params['limit'] = const.SPOTIFY_PAGE_SIZE

    # Loop until we get 'limit' many items or run out
    next_multiple = lambda num, mult: math.ceil(num / mult) * mult
    num_to_request = next_multiple(limit, const.SPOTIFY_PAGE_SIZE)

    for offset in range(0, num_to_request, const.SPOTIFY_PAGE_SIZE):
        uri_params['offset'] = offset

        response_json, status_code = request(
            session,
            request_type=const.REQUEST_GET,
            endpoint=endpoint,
            body=body,
            uri_params=uri_params
        )

        if status_code != 200:
            raise Exception('Oh no TODO!')

        # No more results to grab from spotify
        if len(response_json['items']) == 0:
            break

        for elem in response_json['items']:
            results.append(return_class(session, elem))

    return results[:limit]


def create_batches(elems, batch_size=const.SPOTIFY_PAGE_SIZE):
    """ Break list into batches of max len 'batch_size'

    Args:
        elems: the list of elements to split
        batch_size: the max len of the output batches

    Ex:
        >>> elems = [1, 2, 3, 4, 5, 6, 7]
        >>> create_batches(elems, batch_size=2)
        >>> [[1,2], [3,4], [5,6], [7]]
    """
    results = []
    for i in range(0, len(elems), batch_size):
        results += [elems[i:i + batch_size]]

    return results


def spotifython_eq(self, other):
    """ Eq function to override the builtin one.

    Note: both self and other must implement spotify_id()
    """

    #pylint: disable=unidiomatic-typecheck
    return type(self) == type(other) and self.spotify_id() == other.spotify_id()


def spotifython_hash(obj):
    """ Hash function to override the builtin one.

    Note: obj must implement spotify_id()

    By using this, we can have 2 different objects that represent the same thing
    have the same hash code. For example, if you get the same track from 2
    different calls to User.top, they should have the same hash.
    """

    # Use builtin hash
    return hash(obj.__class__.__name__ + obj.spotify_id())
