from spotifython import Spotifython as sp

s = sp.authenticate(TOKEN)

s.reauthenticate(NEW_TOKEN)

s.search(...)
