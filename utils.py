import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class PlaylistUtils:
    """Utility class for advanced playlist operations"""
    
    @staticmethod
    def batch_convert_playlists(source_client, source_playlists, target_clients):
        """Convert multiple playlists at once"""
        results = []
        for playlist_info in source_playlists:
            try:
                tracks = source_client.get_playlist_tracks(playlist_info['id'])
                playlist_name = f"{playlist_info['name']} (Converted)"
                
                for target_client, target_type in target_clients.items():
                    playlist_id = target_client.create_playlist(playlist_name)
                    added_count = target_client.add_tracks(playlist_id, tracks)
                    
                    results.append({
                        "source_playlist": playlist_info['name'],
                        "target_platform": target_type,
                        "playlist_id": playlist_id,
                        "tracks_added": added_count,
                        "status": "success"
                    })
            except Exception as e:
                results.append({
                    "source_playlist": playlist_info['name'],
                    "target_platform": "all",
                    "error": str(e),
                    "status": "failed"
                })
        
        return results

    @staticmethod
    def analyze_multiple_playlists(clients, playlist_data):
        """Analyze multiple playlists across platforms"""
        analysis_results = {}
        
        for platform, playlists in playlist_data.items():
            analysis_results[platform] = []
            client = clients[platform]
            
            for playlist_info in playlists:
                try:
                    if platform == "Spotify":
                        stats = client.analyze_playlist(playlist_info['url'])
                    else:
                        stats = client.analyze_playlist(playlist_info['id'])
                    
                    if stats:
                        analysis_results[platform].append({
                            "playlist_name": playlist_info['name'],
                            "stats": stats
                        })
                except Exception as e:
                    analysis_results[platform].append({
                        "playlist_name": playlist_info['name'],
                        "error": str(e)
                    })
        
        return analysis_results

    @staticmethod
    def create_smart_playlist(clients, criteria, target_platform, playlist_name):
        """Create a playlist based on smart criteria"""
        all_tracks = []
        
        # Collect tracks from all platforms based on criteria
        for platform, client in clients.items():
            try:
                if criteria.get('search_query'):
                    tracks = client.search_tracks(criteria['search_query'], criteria.get('limit', 20))
                    all_tracks.extend(tracks)
                
                if criteria.get('playlist_id'):
                    tracks = client.get_playlist_tracks(criteria['playlist_id'])
                    all_tracks.extend(tracks)
            except Exception as e:
                print(f"Error collecting tracks from {platform}: {e}")
        
        # Apply filters
        filtered_tracks = PlaylistUtils._apply_track_filters(all_tracks, criteria.get('filters', {}))
        
        # Create playlist on target platform
        target_client = clients[target_platform]
        playlist_id = target_client.create_playlist(playlist_name)
        added_count = target_client.add_tracks(playlist_id, filtered_tracks)
        
        return {
            "playlist_id": playlist_id,
            "name": playlist_name,
            "tracks_added": added_count,
            "total_tracks": len(filtered_tracks)
        }

    @staticmethod
    def _apply_track_filters(tracks, filters):
        """Apply filters to track list"""
        filtered_tracks = tracks
        
        if filters.get('min_popularity'):
            filtered_tracks = [t for t in filtered_tracks if t.get('popularity', 0) >= filters['min_popularity']]
        
        if filters.get('max_duration_ms'):
            filtered_tracks = [t for t in filtered_tracks if t.get('duration_ms', 0) <= filters['max_duration_ms']]
        
        if filters.get('exclude_artists'):
            excluded = set(filters['exclude_artists'])
            filtered_tracks = [t for t in filtered_tracks if t.get('artist', '') not in excluded]
        
        if filters.get('include_artists'):
            included = set(filters['include_artists'])
            filtered_tracks = [t for t in filtered_tracks if t.get('artist', '') in included]
        
        return filtered_tracks

    @staticmethod
    def generate_playlist_report(analysis_results, output_format='json'):
        """Generate a comprehensive report from playlist analysis"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_playlists": sum(len(playlists) for playlists in analysis_results.values()),
                "platforms_analyzed": list(analysis_results.keys())
            },
            "platform_details": {},
            "cross_platform_insights": {}
        }
        
        # Platform-specific details
        for platform, playlists in analysis_results.items():
            total_tracks = 0
            total_duration = 0
            all_artists = []
            
            for playlist in playlists:
                if 'stats' in playlist:
                    stats = playlist['stats']
                    total_tracks += stats.get('total_tracks', 0)
                    total_duration += stats.get('duration_ms', 0)
                    all_artists.extend([artist[0] for artist in stats.get('top_artists', [])])
            
            report["platform_details"][platform] = {
                "total_playlists": len(playlists),
                "total_tracks": total_tracks,
                "total_duration_ms": total_duration,
                "top_artists": PlaylistUtils._get_top_items(all_artists, 10)
            }
        
        # Cross-platform insights
        all_platform_artists = []
        for platform_data in report["platform_details"].values():
            all_platform_artists.extend(platform_data["top_artists"])
        
        report["cross_platform_insights"] = {
            "overall_top_artists": PlaylistUtils._get_top_items(all_platform_artists, 15),
            "total_unique_tracks": sum(pd["total_tracks"] for pd in report["platform_details"].values())
        }
        
        # Save report
        if output_format == 'json':
            filename = f"playlist_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
        elif output_format == 'csv':
            filename = f"playlist_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Platform', 'Playlists', 'Total Tracks', 'Top Artist'])
                for platform, data in report["platform_details"].items():
                    writer.writerow([
                        platform,
                        data["total_playlists"],
                        data["total_tracks"],
                        data["top_artists"][0] if data["top_artists"] else "N/A"
                    ])
        
        return filename

    @staticmethod
    def _get_top_items(items, top_n):
        """Get top N items by frequency"""
        item_counts = {}
        for item in items:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        return sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    @staticmethod
    def sync_playlists_across_platforms(clients, sync_config):
        """Sync playlists across multiple platforms"""
        results = []
        
        for sync_rule in sync_config:
            try:
                source_platform = sync_rule['source_platform']
                target_platforms = sync_rule['target_platforms']
                playlist_id = sync_rule['playlist_id']
                
                source_client = clients[source_platform]
                tracks = source_client.get_playlist_tracks(playlist_id)
                
                for target_platform in target_platforms:
                    target_client = clients[target_platform]
                    playlist_name = f"{sync_rule.get('name', 'Synced Playlist')} ({target_platform})"
                    
                    playlist_id = target_client.create_playlist(playlist_name)
                    added_count = target_client.add_tracks(playlist_id, tracks)
                    
                    results.append({
                        "source_platform": source_platform,
                        "target_platform": target_platform,
                        "playlist_name": playlist_name,
                        "tracks_added": added_count,
                        "status": "success"
                    })
                    
            except Exception as e:
                results.append({
                    "source_platform": sync_rule.get('source_platform', 'Unknown'),
                    "error": str(e),
                    "status": "failed"
                })
        
        return results

    @staticmethod
    def create_playlist_from_recommendations(clients, seed_playlist_info, target_platform, playlist_name, limit=20):
        """Create a playlist from recommendations based on a seed playlist"""
        try:
            source_platform = seed_playlist_info['platform']
            source_client = clients[source_platform]
            
            # Get recommendations
            if source_platform == "Spotify":
                recommendations = source_client.get_recommendations(
                    seed_tracks=[seed_playlist_info['id']], limit=limit
                )
            else:
                recommendations = source_client.get_playlist_recommendations(
                    seed_playlist_info['id'], limit
                )
            
            if not recommendations:
                return None
            
            # Create playlist on target platform
            target_client = clients[target_platform]
            playlist_id = target_client.create_playlist(playlist_name)
            added_count = target_client.add_tracks(playlist_id, recommendations)
            
            return {
                "playlist_id": playlist_id,
                "name": playlist_name,
                "tracks_added": added_count,
                "source_playlist": seed_playlist_info['name']
            }
            
        except Exception as e:
            print(f"Error creating playlist from recommendations: {e}")
            return None

    @staticmethod
    def export_playlist_collection(clients, playlist_collection, format='json'):
        """Export a collection of playlists from multiple platforms"""
        collection_data = {
            "export_date": datetime.now().isoformat(),
            "collection_name": playlist_collection.get('name', 'Playlist Collection'),
            "platforms": {}
        }
        
        for platform, playlists in playlist_collection['playlists'].items():
            collection_data["platforms"][platform] = []
            client = clients[platform]
            
            for playlist_info in playlists:
                try:
                    if platform == "Spotify":
                        tracks = client.get_playlist_tracks(playlist_info['url'])
                    else:
                        tracks = client.get_playlist_tracks(playlist_info['id'])
                    
                    collection_data["platforms"][platform].append({
                        "name": playlist_info['name'],
                        "id": playlist_info.get('id', playlist_info.get('url', '')),
                        "tracks": tracks
                    })
                    
                except Exception as e:
                    collection_data["platforms"][platform].append({
                        "name": playlist_info['name'],
                        "error": str(e)
                    })
        
        # Save collection
        if format == 'json':
            filename = f"playlist_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(collection_data, f, indent=2)
        elif format == 'zip':
            # Could implement ZIP export with multiple files
            filename = f"playlist_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(collection_data, f, indent=2)
        
        return filename

    @staticmethod
    def compare_playlist_audio_features(clients, playlist_data):
        """Compare audio features across playlists"""
        comparison_results = {}
        
        for platform, playlists in playlist_data.items():
            comparison_results[platform] = []
            client = clients[platform]
            
            for playlist_info in playlists:
                try:
                    if platform == "Spotify":
                        stats = client.analyze_playlist(playlist_info['url'])
                    else:
                        stats = client.analyze_playlist(playlist_info['id'])
                    
                    if stats:
                        audio_features = {
                            "playlist_name": playlist_info['name'],
                            "avg_tempo": stats.get('avg_tempo', 0),
                            "avg_energy": stats.get('avg_energy', 0),
                            "avg_danceability": stats.get('avg_danceability', 0),
                            "avg_valence": stats.get('avg_valence', 0),
                            "total_duration_ms": stats.get('duration_ms', 0)
                        }
                        comparison_results[platform].append(audio_features)
                        
                except Exception as e:
                    comparison_results[platform].append({
                        "playlist_name": playlist_info['name'],
                        "error": str(e)
                    })
        
        return comparison_results

    @staticmethod
    def create_playlist_from_audio_criteria(clients, criteria, target_platform, playlist_name):
        """Create a playlist based on audio feature criteria"""
        all_tracks = []
        
        # This would require getting audio features for tracks
        # For now, this is a placeholder implementation
        for platform, client in clients.items():
            try:
                if criteria.get('search_query'):
                    tracks = client.search_tracks(criteria['search_query'], criteria.get('limit', 50))
                    all_tracks.extend(tracks)
            except Exception as e:
                print(f"Error searching tracks on {platform}: {e}")
        
        # Filter by audio criteria (placeholder)
        filtered_tracks = all_tracks[:criteria.get('limit', 20)]
        
        # Create playlist
        target_client = clients[target_platform]
        playlist_id = target_client.create_playlist(playlist_name)
        added_count = target_client.add_tracks(playlist_id, filtered_tracks)
        
        return {
            "playlist_id": playlist_id,
            "name": playlist_name,
            "tracks_added": added_count,
            "criteria_used": criteria
        } 