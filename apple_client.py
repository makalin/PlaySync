import requests
import os
from dotenv import load_dotenv

load_dotenv()

class AppleMusicClient:
    def __init__(self):
        self.developer_token = os.getenv("APPLE_MUSIC_DEV_TOKEN")
        self.user_token = os.getenv("APPLE_MUSIC_USER_TOKEN")
        self.base_url = "https://api.music.apple.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.developer_token}",
            "Music-User-Token": self.user_token
        }

    def get_playlist_tracks(self, playlist_id):
        url = f"{self.base_url}/me/library/playlists/{playlist_id}/tracks"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Failed to get playlist: {response.text}")
        tracks_data = response.json()['data']
        tracks = []
        for track in tracks_data:
            tracks.append({
                "name": track['attributes']['name'],
                "artist": track['attributes']['artistName'],
                "album": track['attributes'].get('albumName', '')
            })
        return tracks

    def create_playlist(self, name):
        url = f"{self.base_url}/me/library/playlists"
        data = {"attributes": {"name": name}}
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 201:
            return response.json()['data'][0]['id']
        else:
            raise Exception(f"Failed to create playlist: {response.text}")

    def add_tracks(self, playlist_id, tracks):
        # Simplified; real implementation needs catalog ID matching
        added = 0
        for track in tracks:
            # Placeholder: assumes track exists in Apple Music
            print(f"Simulating adding to Apple Music: {track['name']} by {track['artist']}")
            added += 1
        return added