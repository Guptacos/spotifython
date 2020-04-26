# Spotifython

### Python library for interfacing with the Spotify REST api

| Method | Endpoint                            | Description                           | Return                |
|--------|-------------------------------------|---------------------------------------|-----------------------|
| `GET`  | `/v1/search`                        | Search for an item                    | array of objects      |
| `GET`  | `/v1/albums/{id}`                   | Get an Album                          | album                 |
| `GET`  | `/v1/albums/{id}/tracks`            | Get an Album's Tracks                 | tracks                |
| `GET`  | `/v1/albums`                        | Get several Albums                    | albums                |
| `GET`  | `/v1/artists/{id}`                  | Get an Artist                         | artist                |
| `GET`  | `/v1/artists/{id}/albums`           | Get an Artist's Albums                | albums                |
| `GET`  | `/v1/artists/{id}/top-tracks`       | Get an Artist's Top Tracks            | tracks                |
| `GET`  | `/v1/artists/{id}/related-artists`  | Get an Artist's Related Artists       | artists               |
| `GET`  | `/v1/artists`                       | Get Several Artists                   | artists               |
| `GET`  | `/v1/me`                            | Get Current User's Profile            | user                  |
| `GET`  | `/v1/users/{user_id}`               | Get a User's Profile                  | user                  |
| `POST` | `/v1/playlists/{playlist_id}/tracks`| Add Items to a Playlist               | -                     |
| `PUT`  | `/v1/playlists/{playlist_id}`       | Change a Playlist's Details           | -                     |
| `POST` | `/v1/users/{user_id}/playlists`     | Create a Playlist                     | -                     |
| `GET`  | `/v1/me/playlists`                  | Get a List of Current User's Playlists| playlists             |
| `GET`  | `/v1/users/{user_id}/playlists`     | Get a List of a User's Playlists      | playlists             |
| `GET`  | `/v1/playlists/{playlist_id}/images`| Get a Playlist Cover Image            | list of image objects |
| `GET`  | `/v1/playlists/{playlist_id}`       | Get a Playlist                        | playlist              |
| `GET`  | `/v1/playlists/{playlist_id}/tracks`| Get a Playlist's Items                | tracks                |
|`DELETE`| `/v1/playlists/{playlist_id}/tracks`| Remove Items from a Playlist          | -                     |
| `PUT`  | `/v1/playlists/{playlist_id}/tracks`| Reorder a Playlist's Items            | -                     |
| `PUT`  | `/v1/playlists/{playlist_id}/tracks`| Replace a Playlist's Items            | -                     |
| `PUT`  | `/v1/playlists/{playlist_id}/images`| Upload a Custom Playlist Cover Image  | -                     |
| `GET`  | `/v1/audio-analysis/{id}`           | Get Audio Analysis for a Track        | audio analysis object |
| `GET`  | `/v1/audio-features/{id}`           | Get Audio Features for a Track        | audio features        |
| `GET`  | `/v1/audio-features`                | Get Audio Features for Several Tracks | audio features        |
| `GET`  | `/v1/tracks`                        | Get Several Tracks                    | tracks                |
| `GET`  | `/v1/tracks/{id}`                   | Get a Track                           | track                 |
|        |                                     |                                       |                       |

- REST APIs will use an optional timeout field, which are passed into an object constructor. The default will be propagated 

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