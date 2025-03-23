import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

class SpotifyClient:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = "http://localhost:8888/callback"
        self.scope = "playlist-read-private playlist-modify-public playlist-modify-private"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope
        ))
        self.user_id = self.sp.current_user()["id"]

    def get_playlist_tracks(self, playlist_url):
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        results = self.sp.playlist_tracks(playlist_id)
        tracks = []
        for item in results['items']:
            track = item['track']
            tracks.append({
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "album": track['album']['name']
            })
        return tracks

    def create_playlist(self, name):
        playlist = self.sp.user_playlist_create(self.user_id, name, public=False)
        return playlist['id']

    def add_tracks(self, playlist_id, tracks):
        track_ids = []
        for track in tracks:
            query = f"{track['name']} {track['artist']}"
            result = self.sp.search(q=query, type='track', limit=1)
            if result['tracks']['items']:
                track_ids.append(result['tracks']['items'][0]['id'])
        if track_ids:
            self.sp.playlist_add_items(playlist_id, track_ids)
        return len(track_ids)