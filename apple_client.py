import requests
import os
import json
import csv
from datetime import datetime
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

    # NEW FUNCTIONS

    def analyze_playlist(self, playlist_id):
        """Get detailed statistics about a playlist"""
        try:
            # Get playlist info
            playlist_url = f"{self.base_url}/me/library/playlists/{playlist_id}"
            response = requests.get(playlist_url, headers=self.headers)
            if response.status_code != 200:
                raise Exception(f"Failed to get playlist info: {response.text}")
            
            playlist_info = response.json()['data'][0]
            tracks = self.get_playlist_tracks(playlist_id)
            
            # Calculate basic statistics
            stats = {
                "name": playlist_info['attributes']['name'],
                "total_tracks": len(tracks),
                "top_artists": self._get_top_artists(tracks),
                "created_date": playlist_info['attributes'].get('dateAdded', 'Unknown'),
                "can_edit": playlist_info['attributes'].get('canEdit', False),
                "description": playlist_info['attributes'].get('description', {}).get('standard', '')
            }
            
            return stats
        except Exception as e:
            print(f"Error analyzing playlist: {e}")
            return None

    def _get_top_artists(self, tracks, top_n=5):
        """Get top artists from playlist"""
        artist_counts = {}
        for track in tracks:
            artist = track['artist']
            artist_counts[artist] = artist_counts.get(artist, 0) + 1
        
        return sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def export_playlist(self, playlist_id, format='json'):
        """Export playlist to various formats"""
        try:
            tracks = self.get_playlist_tracks(playlist_id)
            
            # Get playlist info
            playlist_url = f"{self.base_url}/me/library/playlists/{playlist_id}"
            response = requests.get(playlist_url, headers=self.headers)
            playlist_info = response.json()['data'][0] if response.status_code == 200 else {}
            
            if format == 'json':
                data = {
                    "playlist": {
                        "name": playlist_info.get('attributes', {}).get('name', 'Unknown'),
                        "description": playlist_info.get('attributes', {}).get('description', {}).get('standard', ''),
                        "tracks": tracks
                    }
                }
                filename = f"apple_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                return filename
            
            elif format == 'csv':
                filename = f"apple_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Track Name', 'Artist', 'Album'])
                    for track in tracks:
                        writer.writerow([track['name'], track['artist'], track['album']])
                return filename
            
            elif format == 'txt':
                filename = f"apple_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Playlist: {playlist_info.get('attributes', {}).get('name', 'Unknown')}\n")
                    f.write(f"Description: {playlist_info.get('attributes', {}).get('description', {}).get('standard', '')}\n")
                    f.write(f"Total Tracks: {len(tracks)}\n\n")
                    for i, track in enumerate(tracks, 1):
                        f.write(f"{i}. {track['name']} - {track['artist']} ({track['album']})\n")
                return filename
                
        except Exception as e:
            print(f"Error exporting playlist: {e}")
            return None

    def import_playlist(self, filename, playlist_name=None):
        """Import playlist from JSON file"""
        try:
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
        except Exception as e:
            print(f"Error importing playlist: {e}")
            return None

    def delete_playlist(self, playlist_id):
        """Delete a playlist"""
        url = f"{self.base_url}/me/library/playlists/{playlist_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            return response.status_code == 204
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False

    def rename_playlist(self, playlist_id, new_name):
        """Rename a playlist"""
        url = f"{self.base_url}/me/library/playlists/{playlist_id}"
        data = {"attributes": {"name": new_name}}
        try:
            response = requests.patch(url, json=data, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Error renaming playlist: {e}")
            return False

    def duplicate_playlist(self, playlist_id, new_name=None):
        """Duplicate a playlist"""
        try:
            tracks = self.get_playlist_tracks(playlist_id)
            
            # Get original playlist name
            playlist_url = f"{self.base_url}/me/library/playlists/{playlist_id}"
            response = requests.get(playlist_url, headers=self.headers)
            original_name = "Unknown"
            if response.status_code == 200:
                original_name = response.json()['data'][0]['attributes']['name']
            
            name = new_name or f"{original_name} (Copy)"
            new_playlist_id = self.create_playlist(name)
            added_count = self.add_tracks(new_playlist_id, tracks)
            
            return {
                "original_id": playlist_id,
                "new_id": new_playlist_id,
                "name": name,
                "tracks_added": added_count
            }
        except Exception as e:
            print(f"Error duplicating playlist: {e}")
            return None

    def search_tracks(self, query, limit=20):
        """Search for tracks in Apple Music catalog"""
        url = f"{self.base_url}/catalog/us/search"
        params = {
            "term": query,
            "types": "songs",
            "limit": limit
        }
        try:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code != 200:
                return []
            
            results = response.json()
            tracks = []
            for track in results.get('results', {}).get('songs', {}).get('data', []):
                tracks.append({
                    "id": track['id'],
                    "name": track['attributes']['name'],
                    "artist": track['attributes']['artistName'],
                    "album": track['attributes'].get('albumName', ''),
                    "duration_ms": track['attributes'].get('durationInMillis', 0)
                })
            return tracks
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []

    def get_user_playlists(self):
        """Get all user playlists"""
        url = f"{self.base_url}/me/library/playlists"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                return []
            
            playlists = []
            for playlist in response.json()['data']:
                playlists.append({
                    "id": playlist['id'],
                    "name": playlist['attributes']['name'],
                    "tracks_count": playlist['attributes'].get('playParams', {}).get('id', 'Unknown'),
                    "can_edit": playlist['attributes'].get('canEdit', False)
                })
            return playlists
        except Exception as e:
            print(f"Error getting user playlists: {e}")
            return []

    def create_playlist_from_search(self, query, playlist_name, limit=20):
        """Create a playlist from search results"""
        tracks = self.search_tracks(query, limit)
        if not tracks:
            return None
        
        try:
            playlist_id = self.create_playlist(playlist_name)
            added_count = self.add_tracks(playlist_id, tracks)
            
            return {
                "playlist_id": playlist_id,
                "name": playlist_name,
                "tracks_added": added_count
            }
        except Exception as e:
            print(f"Error creating playlist from search: {e}")
            return None

    def backup_playlists(self, backup_dir="apple_playlist_backups"):
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
                tracks = self.get_playlist_tracks(playlist['id'])
                playlist_data = {
                    "id": playlist['id'],
                    "name": playlist['name'],
                    "tracks_count": len(tracks),
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

    def get_playlist_recommendations(self, playlist_id, limit=20):
        """Get recommendations based on a playlist"""
        try:
            tracks = self.get_playlist_tracks(playlist_id)
            if not tracks:
                return []
            
            # Get top artists from playlist
            artist_counts = {}
            for track in tracks:
                artist = track['artist']
                artist_counts[artist] = artist_counts.get(artist, 0) + 1
            
            top_artist = max(artist_counts.items(), key=lambda x: x[1])[0]
            
            # Search for similar tracks by top artist
            similar_tracks = self.search_tracks(top_artist, limit)
            
            return similar_tracks
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []