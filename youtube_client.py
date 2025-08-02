from ytmusicapi import YTMusic
import os
import json
import csv
from datetime import datetime
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

    # NEW FUNCTIONS

    def analyze_playlist(self, playlist_id):
        """Get detailed statistics about a playlist"""
        try:
            playlist = self.yt.get_playlist(playlist_id)
            tracks = self.get_playlist_tracks(playlist_id)
            
            # Calculate statistics
            stats = {
                "name": playlist.get('title', 'Unknown'),
                "total_tracks": len(tracks),
                "description": playlist.get('description', ''),
                "author": playlist.get('author', {}).get('name', 'Unknown'),
                "year": playlist.get('year', 'Unknown'),
                "top_artists": self._get_top_artists(tracks),
                "duration": self._calculate_total_duration(playlist['tracks']),
                "visibility": playlist.get('privacy', 'Unknown')
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

    def _calculate_total_duration(self, tracks):
        """Calculate total duration of playlist"""
        total_seconds = 0
        for track in tracks:
            duration = track.get('duration', '0:00')
            if isinstance(duration, str) and ':' in duration:
                parts = duration.split(':')
                if len(parts) == 2:
                    total_seconds += int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    total_seconds += int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

    def export_playlist(self, playlist_id, format='json'):
        """Export playlist to various formats"""
        try:
            playlist = self.yt.get_playlist(playlist_id)
            tracks = self.get_playlist_tracks(playlist_id)
            
            if format == 'json':
                data = {
                    "playlist": {
                        "name": playlist.get('title', 'Unknown'),
                        "description": playlist.get('description', ''),
                        "author": playlist.get('author', {}).get('name', 'Unknown'),
                        "tracks": tracks
                    }
                }
                filename = f"youtube_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                return filename
            
            elif format == 'csv':
                filename = f"youtube_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Track Name', 'Artist', 'Album'])
                    for track in tracks:
                        writer.writerow([track['name'], track['artist'], track['album']])
                return filename
            
            elif format == 'txt':
                filename = f"youtube_playlist_{playlist_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Playlist: {playlist.get('title', 'Unknown')}\n")
                    f.write(f"Description: {playlist.get('description', '')}\n")
                    f.write(f"Author: {playlist.get('author', {}).get('name', 'Unknown')}\n")
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
        try:
            self.yt.delete_playlist(playlist_id)
            return True
        except Exception as e:
            print(f"Error deleting playlist: {e}")
            return False

    def rename_playlist(self, playlist_id, new_name):
        """Rename a playlist"""
        try:
            self.yt.edit_playlist(playlist_id, title=new_name)
            return True
        except Exception as e:
            print(f"Error renaming playlist: {e}")
            return False

    def duplicate_playlist(self, playlist_id, new_name=None):
        """Duplicate a playlist"""
        try:
            playlist = self.yt.get_playlist(playlist_id)
            tracks = self.get_playlist_tracks(playlist_id)
            
            name = new_name or f"{playlist.get('title', 'Unknown')} (Copy)"
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
        """Search for tracks"""
        try:
            results = self.yt.search(query, filter="songs", limit=limit)
            tracks = []
            for track in results:
                tracks.append({
                    "id": track.get('videoId', ''),
                    "name": track.get('title', 'Unknown'),
                    "artist": track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown',
                    "album": track.get('album', {}).get('name', ''),
                    "duration": track.get('duration', '0:00')
                })
            return tracks
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []

    def get_user_playlists(self):
        """Get all user playlists"""
        try:
            playlists = self.yt.get_library_playlists()
            formatted_playlists = []
            for playlist in playlists:
                formatted_playlists.append({
                    "id": playlist.get('playlistId', ''),
                    "name": playlist.get('title', 'Unknown'),
                    "tracks_count": playlist.get('count', 0),
                    "author": playlist.get('author', {}).get('name', 'Unknown')
                })
            return formatted_playlists
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

    def backup_playlists(self, backup_dir="youtube_playlist_backups"):
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

    def get_trending_playlists(self, region='US', limit=10):
        """Get trending playlists"""
        try:
            # YouTube Music doesn't have a direct trending playlists endpoint
            # This is a placeholder that could be implemented with web scraping
            # or by using YouTube's trending music videos
            trending = self.yt.get_trending(region=region, category="music")
            return trending[:limit]
        except Exception as e:
            print(f"Error getting trending playlists: {e}")
            return []

    def get_playlist_audio_info(self, playlist_id):
        """Get audio information for playlist tracks"""
        try:
            playlist = self.yt.get_playlist(playlist_id)
            audio_info = []
            
            for track in playlist['tracks']:
                info = {
                    "title": track.get('title', 'Unknown'),
                    "artist": track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown',
                    "duration": track.get('duration', '0:00'),
                    "album": track.get('album', {}).get('name', ''),
                    "year": track.get('year', 'Unknown'),
                    "video_id": track.get('videoId', '')
                }
                audio_info.append(info)
            
            return audio_info
        except Exception as e:
            print(f"Error getting audio info: {e}")
            return []