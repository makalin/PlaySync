from ytmusicapi import YTMusic
import os
from dotenv import load_dotenv

load_dotenv()

class YouTubeMusicClient:
    def __init__(self):
        # Assumes auth via headers file; see ytmusicapi setup instructions
        self.yt = YTMusic(os.getenv("YOUTUBE_AUTH_FILE"))

    def get_playlist_tracks(self, playlist_id):
        playlist = self.yt.get_playlist(playlist_id)
        tracks = []
        for track in playlist['tracks']:
            tracks.append({
                "name": track['title'],
                "artist": track['artists'][0]['name'] if track['artists'] else "Unknown",
                "album": track.get('album', {}).get('name', '')
            })
        return tracks

    def create_playlist(self, name):
        playlist_id = self.yt.create_playlist(name, "Created by PlaySync")
        return playlist_id

    def add_tracks(self, playlist_id, tracks):
        added = 0
        for track in tracks:
            query = f"{track['name']} {track['artist']}"
            search_results = self.yt.search(query, filter="songs", limit=1)
            if search_results:
                video_id = search_results[0]['videoId']
                self.yt.add_playlist_items(playlist_id, [video_id])
                added += 1
        return added