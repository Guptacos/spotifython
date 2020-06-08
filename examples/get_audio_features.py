""" Example showing how to get the release dates of an artist's top albums """

#pylint: disable=import-error
from sys import argv
import spotifython as sp

# TODO: this example makes method calls to stale methods.

# Example of control flow to go from a song name to its audio features.

TOKEN_FILE = 'woohoo.mp4'

def main():
    """ Script to pring out the audio features for a song """
    if len(argv) != 2:
        print(f'USAGE: python3 {argv[0]} <song-name>')

    name = argv[1]

    with open(TOKEN_FILE, 'r') as fp:
        token = fp.readline()

    session = sp.Session(token)
    results = session.search(name, types=[sp.TRACKS], limit=5)

    tracks = results.tracks()
    top_track = tracks[0]

    features = top_track.audio_features()

    for feature, val in features.items():
        print(feature, val)


if __name__ == '__main__':
    main()
