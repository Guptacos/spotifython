'''
Helper utilities for the spotifython library. These should not be used by client
code.
'''

# Third party imports
import requests

# Local imports
from spotifython.endpoint import Endpoint

##################################
# HTTP REQUEST
##################################
# https://stackoverflow.com/questions/23267409/how-to-implement-retry-mechanism-into-python-requests-library

def request(sp,
            request_type,
            endpoint,
            body=None,
            uri_params=None):
    ''' Does request with retry.
    This method should return a tuple (response_json, status_code) if the
    request is executed, and raises an Exception if the request type is invalid.

    Args:
        request_type: one of sp.REQUEST_GET, sp.REQUEST_POST, sp.REQUEST_PUT,
            sp.REQUEST_DELETE.  endpoint: an endpoint string defined in the
            Endpoint class.  body: (Optional) dictionary of values for the
            request body.  uri_params: (Optional) params to encode into the uri.
        endpoint: the uri to request
        body: the body to send as part of the request, as a dict
        uri_params: the parameters to append to the uri, as a dict

    Returns:
        Only returns when successful. Returns the request JSON and the request's
        status code.  If the response contains invalid JSON or no content,
        response_json=None.

    Exceptions:
        Raises an HTTPError object in the event of an unsuccessful web request.
        All exceptions are as according to requests.Request.

    Usage:
        response_json, status_code = _request(...)
    '''
    request_uri = Endpoint.BASE_URI + endpoint
    headers = {
        'Authorization': 'Bearer ' + sp.token(),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request(request_type,
                                request_uri,
                                json=body,
                                params=uri_params,
                                headers=headers,
                                timeout=sp.timeout())

    # Extract the information from response. No exception should be present in
    # the event of a successful response, but the response json may or may not
    # be present.

    # r.raise_for_status() raises HTTPError if request unsuccessful - this is
    # a real error
    response.raise_for_status()

    try: # content = Union[json, bytes]
        # r.json() raises ValueError if no content - this is not an error and no
        # exception should be returned
        content = response.json()
    except ValueError:
        content = None # May be malformed or no

    return content, response.status_code
