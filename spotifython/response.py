# Class used to return the responses from any method calls or field
# accessors, along with a corresponding status code defined in this
# class. Response status codes are not necessarily 1:1 mapped with
# the HTTP status code, in order to provide more useful diagnostic
# information to the client. 
class Response:
    OK = 'OK'
    # TODO: add more appropriate response codes

    def __init__(self, status, contents : object):
        self._status = status
        self._contents = contents

    def status(self):
        return self._status

    def contents(self):
        return self._contents
    
    def __str__(self):
        return f'[Response: {self.status}]'


# user code

# response = album.tracks()
# if response.status() != Response.OK:
#     print('this is bad uh oh')

# tracks = response.contents()