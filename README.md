# Spotifython
Python library for interfacing with the Spotify REST api

### Spotify REST API endpoints supported by this library

### Spotifython general object

| Method | Endpoint                                        | Description                                                  | Return                |
|--------|-------------------------------------------------|--------------------------------------------------------------|-----------------------|
| `GET`  | `/v1/search`                                    | Search for an item                                           | array of objects      |
| `GET`  | `/v1/albums/{id}`                               | Get an Album                                                 | album                 |
| `GET`  | `/v1/albums`                                    | Get several Albums                                           | albums                |
| `GET`  | `/v1/artists/{id}`                              | Get an Artist                                                | artist                |
| `GET`  | `/v1/artists`                                   | Get Several Artists                                          | artists               |
| `GET`  | `/v1/playlists/{playlist_id}`                   | Get a Playlist                                               | playlist              |
| `GET`  | `/v1/me`                                        | Get Current User's Profile                                   | user                  |
| `GET`  | `/v1/users/{user_id}`                           | Get a User's Profile                                         | user                  |
| `GET`  | `/v1/tracks/{id}`                               | Get a Track                                                  | track                 |
| `GET`  | `/v1/tracks`                                    | Get Several Tracks                                           | tracks                |

### Artist

| Method | Endpoint                                        | Description                                                  | Return                |
|--------|-------------------------------------------------|--------------------------------------------------------------|-----------------------|
| `GET`  | `/v1/artists/{id}/albums`                       | Get an Artist's Albums                                       | albums                |
| `GET`  | `/v1/artists/{id}/top-tracks`                   | Get an Artist's Top Tracks                                   | tracks                |
| `GET`  | `/v1/artists/{id}/related-artists`              | Get an Artist's Related Artists                              | artists               |

### Album

| Method | Endpoint                                        | Description                                                  | Return                |
|--------|-------------------------------------------------|--------------------------------------------------------------|-----------------------|
| `GET`  | `/v1/albums/{id}/tracks`                        | Get an Album's Tracks                                        | tracks                |

### User

| Method | Endpoint                                        | Description                                                  | Return                |
|--------|-------------------------------------------------|--------------------------------------------------------------|-----------------------|
| `POST` | `/v1/users/{user_id}/playlists`                 | Create a Playlist                                            | -                     |
| `GET`  | `/v1/me/playlists`                              | Get a List of Current User's Playlists                       | playlists             |
| `GET`  | `/v1/users/{user_id}/playlists`                 | Get a List of a User's Playlists                             | playlists             |
|`DELETE`| `/v1/me/following`                              | Unfollow Artists or Users                                    |                       |
|`DELETE`| `/v1/playlists/{playlist_id}/followers`         | Unfollow a Playlist                                          |                       |
| `GET`  | `/v1/me/following/contains`                     | Check if Current User Follows Artists or Users               |                       |
| `GET`  | `/v1/me/following`                              | Get Followed Artists                                         |                       |
| `GET`  | `/v1/playlists/{playlist_id}/followers/contains`| Check if Users Follow a Playlist                             |                       |
| `PUT`  | `/v1/me/following`                              | Follow Artists or Users                                      |                       |
| `PUT`  | `/v1/playlists/{playlist_id}/followers`         | Follow a Playlist                                            |                       |
|`DELETE`| `/v1/me/albums`                                 | Remove Albums for Current User                               |                       |
|`DELETE`| `/v1/me/tracks`                                 | Remove Tracks for Current User                               |                       |
| `GET`  | `/v1/me/albums/contains`                        | Check Current User's Saved Albums                            |                       |
| `GET`  | `/v1/me/tracks/contains`                        | Check Current User's Saved Tracks                            |                       |
| `GET`  | `/v1/me/albums`                                 | Get Current User's Saved Albums                              |                       |
| `GET`  | `/v1/me/tracks`                                 | Get Current User's Saved Tracks                              |                       |
| `PUT`  | `/v1/me/albums`                                 | Save Albums for Current User                                 |                       |
| `PUT`  | `/v1/me/tracks`                                 | Save Tracks for Current User                                 |                       |
| `GET`  | `/v1/me/player/recently-played`                 | Get the Current User's Recently Played Tracks                |                       |
| `GET`  | `/v1/me/top/{type}`                             | Get User's Top Artists and Tracks                            |                       |

#### Player (belongs only to `me` user)

| Method | Endpoint                                        | Description                                                  | Return                |
|--------|-------------------------------------------------|--------------------------------------------------------------|-----------------------|
| `GET`  | `/v1/me/player`                                 | Get Information About The User's Current Playback            |                       |
| `GET`  | `/v1/me/player/devices`                         | Get a User's Available Devices                               |                       |
| `GET`  | `/v1/me/player/currently-playing`               | Get the User's Currently Playing Track                       |                       |
| `POST` | `/v1/me/player/next`                            | Skip User's Playback To Next Track                           |                       |
| `POST` | `/v1/me/player/previous`                        | Skip User's Playback To Previous Track                       |                       |
| `POST` | `/v1/me/player/queue`                           | Add an item to the end of the user's current playback queue. |                       |
| `PUT`  | `/v1/me/player/pause`                           | Pause a User's Playback                                      |                       |
| `PUT`  | `/v1/me/player/play`                            | Start/Resume a User's Playback                               |                       |
| `PUT`  | `/v1/me/player/repeat`                          | Set Repeat Mode On User's Playback                           |                       |
| `PUT`  | `/v1/me/player/seek`                            | Seek To Position In Currently Playing Track                  |                       |
| `PUT`  | `/v1/me/player/shuffle`                         | Toggle Shuffle For User's Playback                           |                       |
| `PUT`  | `/v1/me/player`                                 | Transfer a User's Playback                                   |                       |
| `PUT`  | `/v1/me/player/volume`                          | Set Volume For User's Playback                               |                       |

### Playlist

| Method | Endpoint                                        | Description                                                  | Return                |
|--------|-------------------------------------------------|--------------------------------------------------------------|-----------------------|
| `POST` | `/v1/playlists/{playlist_id}/tracks`            | Add Items to a Playlist                                      | -                     |
| `PUT`  | `/v1/playlists/{playlist_id}`                   | Change a Playlist's Details                                  | -                     |
| `GET`  | `/v1/playlists/{playlist_id}/images`            | Get a Playlist Cover Image                                   | list of image objects |
| `GET`  | `/v1/playlists/{playlist_id}/tracks`            | Get a Playlist's Items                                       | tracks                |
|`DELETE`| `/v1/playlists/{playlist_id}/tracks`            | Remove Items from a Playlist                                 | -                     |
| `PUT`  | `/v1/playlists/{playlist_id}/tracks`            | Reorder a Playlist's Items                                   | -                     |
| `PUT`  | `/v1/playlists/{playlist_id}/tracks`            | Replace a Playlist's Items                                   | -                     |
| `PUT`  | `/v1/playlists/{playlist_id}/images`            | Upload a Custom Playlist Cover Image                         | -                     |

### Track

| Method | Endpoint                                        | Description                                                  | Return                |
|--------|-------------------------------------------------|--------------------------------------------------------------|-----------------------|
| `GET`  | `/v1/audio-analysis/{id}`                       | Get Audio Analysis for a Track                               | audio analysis object |
| `GET`  | `/v1/audio-features/{id}`                       | Get Audio Features for a Track                               | audio features        |
| `GET`  | `/v1/audio-features`                            | Get Audio Features for Several Tracks                        | audio features        |

### Spotify REST api endpoints __not__ supported by this library
- Browse
- Episodes
- Shows

### Notes

- The top level contructor will take in an optional timeout field, which will be
  passed into all object constructors. This will be used when making calls to
  the Spotify REST api.
- REST APIs will use an optional timeout field, which are passed into the object constructor. The default will be propagated 
- __Search result__ object contains getter methods for a result from searching.
- __Artist__ object contains albums and playlists.
- __Album__ object contains tracks.
- __User__ object contains playlists (also player and some other things).
- __Playlist__ object contains tracks.
- __Track__ object contains thangz. __This is a base object.__
    - Album type
    - Artists
    - Available markets
    - External URL
    - id
    - image URL
- __Audio features__ should be a dictionary based off of API endpoint reference for [audio feature objects.](https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/)
- __Audio analysis__: worry about this object later! :D
- Follow methods should be split between the playlist and the user objects.
- Player methods should be given to the user
- User library methods (top tracks, etc.)
- set new token method should be provided in order to address session expiration
- Failure can happen, return objects should contain status code for the user
- Error handlin
