import base64

from requests import post, get
import json


import spotipy
from spotipy.oauth2 import SpotifyOAuth

class JSpotifyAPI:
    def __init__(self):
        self.CLIENT_ID = ''
        self.CLIENT_SECRET = ''


        self.token_ret = self.get_token()

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.CLIENT_ID,
                                                       client_secret=self.CLIENT_SECRET,
                                                       redirect_uri='http://localhost:8080/callback',
                                                       scope='user-modify-playback-state,user-read-playback-state'))

    def get_token(self):
        auth_string = self.CLIENT_ID + ":" + self.CLIENT_SECRET
        auth_bytes = auth_string.encode('utf-8')
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = 'https://accounts.spotify.com/api/token'
        headers = {'Authorization': 'Basic ' + auth_base64,
                   'Content-Type': 'application/x-www-form-urlencoded'
                   }
        data = {'grant_type': 'client_credentials'}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result['access_token']
        return token

    def auth_header(self, token):
        return {'Authorization': 'Bearer ' + token}

    def get_artist_songs(self, artist_name):
        # Search for the artist
        results = self.sp.search(q=f'artist:{artist_name}', type='artist')

        if results['artists']['items']:
            artist_id = results['artists']['items'][0]['id']  # Get the first artist's ID

            # Get the artist's top tracks
            top_tracks = self.sp.artist_top_tracks(artist_id)
            tracks = [track['name'] for track in top_tracks['tracks']]

            x = 1
            for track in tracks:
                print(f'{x}' +  '. ' + track )

                x += 1
            return tracks
        else:
            return None

    def spotify_play_music(self, song_name):
        print(self.sp.me())


        track_name = f"{song_name}"
        results = self.sp.search(q=track_name, type='track')

        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            print(f"Track URI: {track_uri}")
        else:
            print("No tracks found.")

        track_uri_complete = track_uri
        self.sp.start_playback(uris=[track_uri_complete])

    def spotify_pause_music(self):
        try:
            self.sp.pause_playback()
            print("Playback paused.")
        except Exception as e:
            print(f"An error occurred while pausing playback: {e}")


if __name__ == '__main__':
    Spotty = JSpotifyAPI()

    Spotty.get_artist_songs("Eminem")
