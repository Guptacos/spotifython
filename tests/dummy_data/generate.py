'''
Since you can't get random users from the Spotify interface, randomly generate
some fake users for testing.

Template is taken from Spotify User ODM

Usage:
`python generate.py _num_entries_` to print to the console
`python generate.py _num_entries_ > file.json` to save to a file

'''
#pylint: disable=missing-function-docstring
#pylint: disable=bare-except

import copy
import json
import random
import sys

NAME_PREFIX = 'deadbeef'

TEMPLATE = {
    'country': 'US',
    'display_name': '',
    'email': '@gmail.com',
    'explicit_content': {
        'filter_enabled': False,
        'filter_locked': False
    },
    'external_urls': {
        'spotify': 'https://open.spotify.com/user/'
    },
    'followers': {
        'href': None,
        'total': -1
    },
    'href': 'https://api.spotify.com/v1/users/',
    'id': '',
    'images': [],
    'product': 'premium',
    'type': 'user',
    'uri': 'spotify:user:'
}


def main(num_entries):
    results = []

    for i in range(num_entries):
        user = copy.deepcopy(TEMPLATE)
        name = NAME_PREFIX + str(i)

        user['display_name'] = name
        user['email'] = name + '@gmail.com'
        user['external_urls']['spotify'] += name
        user['href'] += name
        user['id'] = name
        user['uri'] += name
        user['followers']['total'] = random.randint(0, 10)

        results.append(user)

    print(json.dumps({'items': results}, indent=2))

if __name__ == '__main__':
    try:
        arg = int(sys.argv[1])
    except:
        print('Error: please provide 1 positive int as the arg')
        sys.exit(-1)

    main(arg)
