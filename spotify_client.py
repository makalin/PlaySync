import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json
import csv
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SpotifyClient:
    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = "http://localhost:8888/callback"
        self.scope = "playlist-read-private playlist-modify-public playlist-modify-private user-library-read user-top-read"
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

    # NEW FUNCTIONS

    def analyze_playlist(self, playlist_url):
        """Get detailed statistics about a playlist"""
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        playlist_info = self.sp.playlist(playlist_id)
        tracks = self.get_playlist_tracks(playlist_url)
        
        # Get audio features for tracks
        track_ids = []
        for track in tracks:
            query = f"{track['name']} {track['artist']}"
            result = self.sp.search(q=query, type='track', limit=1)
            if result['tracks']['items']:
                track_ids.append(result['tracks']['items'][0]['id'])
        
        audio_features = []
        if track_ids:
            features = self.sp.audio_features(track_ids)
            audio_features = [f for f in features if f is not None]
        
        # Calculate statistics
        stats = {
            "name": playlist_info['name'],
            "total_tracks": len(tracks),
            "duration_ms": sum(f.get('duration_ms', 0) for f in audio_features),
            "avg_tempo": sum(f.get('tempo', 0) for f in audio_features) / len(audio_features) if audio_features else 0,
            "avg_energy": sum(f.get('energy', 0) for f in audio_features) / len(audio_features) if audio_features else 0,
            "avg_danceability": sum(f.get('danceability', 0) for f in audio_features) / len(audio_features) if audio_features else 0,
            "avg_valence": sum(f.get('valence', 0) for f in audio_features) / len(audio_features) if audio_features else 0,
            "top_artists": self._get_top_artists(tracks),
            "top_genres": self._get_top_genres(track_ids),
            "created_by": playlist_info.get('owner', {}).get('display_name', 'Unknown'),
            "public": playlist_info.get('public', False),
            "collaborative": playlist_info.get('collaborative', False)
        }
        
        return stats

    def _get_top_artists(self, tracks, top_n=5):
        """Get top artists from playlist"""
        artist_counts = {}
        for track in tracks:
            artist = track['artist']
            artist_counts[artist] = artist_counts.get(artist, 0) + 1
        
        return sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def _get_top_genres(self, track_ids, top_n=5):
        """Get top genres from playlist"""
        if not track_ids:
            return []
        
        # Get artist IDs
        tracks_info = self.sp.tracks(track_ids)
        artist_ids = []
        for track in tracks_info['tracks']:
            if track and track['artists']:
                artist_ids.append(track['artists'][0]['id'])
        
        if not artist_ids:
            return []
        
        # Get artist genres
        artists_info = self.sp.artists(artist_ids)
        genre_counts = {}
        for artist in artists_info['artists']:
            for genre in artist.get('genres', []):
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        return sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def export_playlist(self, playlist_url, format='json'):
        """Export playlist to various formats"""
        tracks = self.get_playlist_tracks(playlist_url)
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        playlist_info = self.sp.playlist(playlist_id)
        
        if format == 'json':
            data = {
                "playlist": {
                    "name": playlist_info['name'],
                    "description": playlist_info.get('description', ''),
                    "tracks": tracks
                }
            }
            filename = f"spotify_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return filename
        
        elif format == 'csv':
            filename = f"spotify_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Track Name', 'Artist', 'Album'])
                for track in tracks:
                    writer.writerow([track['name'], track['artist'], track['album']])
            return filename
        
        elif format == 'txt':
            filename = f"spotify_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Playlist: {playlist_info['name']}\n")
                f.write(f"Description: {playlist_info.get('description', '')}\n")
                f.write(f"Total Tracks: {len(tracks)}\n\n")
                for i, track in enumerate(tracks, 1):
                    f.write(f"{i}. {track['name']} - {track['artist']} ({track['album']})\n")
            return filename

    def import_playlist(self, filename, playlist_name=None):
        """Import playlist from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        playlist_data = data.get('playlist', data)
        tracks = playlist_data['tracks']
        name = playlist_name or playlist_data.get('name', 'Imported Playlist')
        
        playlist_id = self.create_playlist(name)
        added_count = self.add_tracks(playlist_id, tracks)
        
        return {
            "playlist_id": playlist_id,
            "name": name,
            "tracks_added": added_count,
            "total_tracks": len(tracks)
        }

    def delete_playlist(self, playlist_url):
        """Delete a playlist"""
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        try:
            self.sp.user_playlist_unfollow(self.user_id, playlist_id)
            return True
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False

    def rename_playlist(self, playlist_url, new_name):
        """Rename a playlist"""
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        try:
            self.sp.user_playlist_change_details(playlist_id, name=new_name)
            return True
        except Exception as e:
            print(f"Error renaming playlist: {e}")
            return False

    def duplicate_playlist(self, playlist_url, new_name=None):
        """Duplicate a playlist"""
        tracks = self.get_playlist_tracks(playlist_url)
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        playlist_info = self.sp.playlist(playlist_id)
        
        name = new_name or f"{playlist_info['name']} (Copy)"
        new_playlist_id = self.create_playlist(name)
        added_count = self.add_tracks(new_playlist_id, tracks)
        
        return {
            "original_id": playlist_id,
            "new_id": new_playlist_id,
            "name": name,
            "tracks_added": added_count
        }

    def search_tracks(self, query, limit=20):
        """Search for tracks"""
        results = self.sp.search(q=query, type='track', limit=limit)
        tracks = []
        for track in results['tracks']['items']:
            tracks.append({
                "id": track['id'],
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "album": track['album']['name'],
                "duration_ms": track['duration_ms'],
                "popularity": track['popularity']
            })
        return tracks

    def get_recommendations(self, seed_tracks=None, seed_artists=None, seed_genres=None, limit=20):
        """Get track recommendations"""
        if not any([seed_tracks, seed_artists, seed_genres]):
            return []
        
        recommendations = self.sp.recommendations(
            seed_tracks=seed_tracks[:5] if seed_tracks else None,
            seed_artists=seed_artists[:5] if seed_artists else None,
            seed_genres=seed_genres[:5] if seed_genres else None,
            limit=limit
        )
        
        tracks = []
        for track in recommendations['tracks']:
            tracks.append({
                "id": track['id'],
                "name": track['name'],
                "artist": track['artists'][0]['name'],
                "album": track['album']['name'],
                "popularity": track['popularity']
            })
        return tracks

    def get_user_playlists(self):
        """Get all user playlists"""
        playlists = []
        results = self.sp.current_user_playlists()
        
        for playlist in results['items']:
            playlists.append({
                "id": playlist['id'],
                "name": playlist['name'],
                "tracks_count": playlist['tracks']['total'],
                "public": playlist['public'],
                "url": playlist['external_urls']['spotify']
            })
        
        return playlists

    def get_audio_features(self, track_ids):
        """Get audio features for tracks"""
        features = self.sp.audio_features(track_ids)
        return [f for f in features if f is not None]

    def create_playlist_from_search(self, query, playlist_name, limit=20):
        """Create a playlist from search results"""
        tracks = self.search_tracks(query, limit)
        if not tracks:
            return None
        
        playlist_id = self.create_playlist(playlist_name)
        track_ids = [track['id'] for track in tracks]
        self.sp.playlist_add_items(playlist_id, track_ids)
        
        return {
            "playlist_id": playlist_id,
            "name": playlist_name,
            "tracks_added": len(tracks)
        }

    def backup_playlists(self, backup_dir="playlist_backups"):
        """Backup all user playlists"""
        import os
        os.makedirs(backup_dir, exist_ok=True)
        
        playlists = self.get_user_playlists()
        backup_info = {
            "backup_date": datetime.now().isoformat(),
            "total_playlists": len(playlists),
            "playlists": []
        }
        
        for playlist in playlists:
            try:
                tracks = self.get_playlist_tracks(playlist['url'])
                playlist_data = {
                    "id": playlist['id'],
                    "name": playlist['name'],
                    "tracks_count": playlist['tracks_count'],
                    "tracks": tracks
                }
                backup_info["playlists"].append(playlist_data)
                
                # Save individual playlist
                filename = f"{backup_dir}/playlist_{playlist['id']}.json"
                with open(filename, 'w') as f:
                    json.dump(playlist_data, f, indent=2)
                    
            except Exception as e:
                print(f"Error backing up playlist {playlist['name']}: {e}")
        
        # Save backup summary
        summary_file = f"{backup_dir}/backup_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        return summary_file