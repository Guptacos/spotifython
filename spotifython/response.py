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
        return f"[Response: {self.status}]"


# user code

# response = album.tracks()
# if response.status() != Response.OK:
#     print('this is bad uh oh')


# tracks = response.contents()