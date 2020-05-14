import copy
import json
import random

base = {
  "country": "US",
  "display_name": "",
  "email": "@gmail.com",
  "explicit_content": {
    "filter_enabled": False,
    "filter_locked": False
  },
  "external_urls": {
    "spotify": "https://open.spotify.com/user/"
  },
  "followers": {
    "href": None,
    "total": 3
  },
  "href": "https://api.spotify.com/v1/users/",
  "id": "",
  "images": [],
  "product": "premium",
  "type": "user",
  "uri": "spotify:user:"
}

# Since you can't get random users from the Spotify interface, randomly generate
# some fake users for testing.

results = []
for i in range(50):
    cur = copy.deepcopy(base)
    name = 'deadbeef' + str(i)

    cur['display_name'] = name
    cur['email'] = name + '@gmail.com'
    cur['external_urls']['spotify'] = cur['external_urls']['spotify'] + name
    cur['href'] = cur['href'] + name
    cur['id'] = name
    cur['uri'] = cur['uri'] + name
    cur['followers']['total'] = random.randint(0, 10)

    results.append(cur)

results = {'items': results}
with open('users.json', 'w') as fp:
    json.dump(results, fp, indent=2)
