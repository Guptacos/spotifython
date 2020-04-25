from sys import argv
import spotifython as sp

# Example of control flow to go from a song name to its audio features.

TOKEN_FILE = 'woohoo.mp4'


def main():
    if len(argv) < 2:
        print('USAGE: python3 %s <song-name>' % (argv[0]))

    name = argv[1]

    with open(TOKEN_FILE, 'r') as f:
        token = f.readline()

    session = sp.Spotifython(token)

    results = session.search(name, types=[sp.TRACKS])

    tracks = results.tracks()
    top_track = tracks[0]

    features = top_track.audio_features()

    for feature, val in features.items():
        print(feature, val)


if __name__ == '__main__':
    main()
