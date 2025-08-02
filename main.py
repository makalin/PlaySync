from spotify_client import SpotifyClient
from apple_client import AppleMusicClient
from youtube_client import YouTubeMusicClient
from utils import PlaylistUtils

def get_tracks(source_client, source_type, source_id):
    if source_type == "Spotify":
        return source_client.get_playlist_tracks(source_id)
    elif source_type == "Apple Music":
        return source_client.get_playlist_tracks(source_id)
    elif source_type == "YouTube Music":
        return source_client.get_playlist_tracks(source_id)
    return []

def add_to_target(target_client, target_type, playlist_name, tracks):
    playlist_id = target_client.create_playlist(playlist_name)
    added_count = target_client.add_tracks(playlist_id, tracks)
    print(f"Added {added_count} tracks to {target_type} playlist: {playlist_name}")
    return playlist_id

def convert_playlist(source_client, source_type, target_clients, source_id):
    tracks = get_tracks(source_client, source_type, source_id)
    print(f"Retrieved {len(tracks)} tracks from {source_type}.")
    target_name = input(f"Enter name for new playlist(s): ")
    for target_client, target_type in target_clients.items():
        add_to_target(target_client, target_type, target_name, tracks)

def merge_playlists(clients, sources):
    all_tracks = set()
    for source_type, source_id in sources.items():
        tracks = get_tracks(clients[source_type], source_type, source_id)
        for track in tracks:
            all_tracks.add((track['name'], track['artist']))
    merged_tracks = [{"name": t[0], "artist": t[1], "album": ""} for t in all_tracks]
    print(f"Merged into {len(merged_tracks)} unique tracks.")
    target_type = input("Enter target platform (Spotify, Apple Music, YouTube Music): ")
    target_name = input("Enter name for merged playlist: ")
    add_to_target(clients[target_type], target_type, target_name, merged_tracks)

def compare_playlists(clients, sources):
    track_sets = {}
    for source_type, source_id in sources.items():
        tracks = get_tracks(clients[source_type], source_type, source_id)
        track_sets[source_type] = {(t['name'], t['artist']) for t in tracks}
    
    common = set.intersection(*track_sets.values())
    print(f"\nCommon tracks across all playlists ({len(common)}):")
    for track in common:
        print(f"- {track[0]} by {track[1]}")
    
    for source_type, tracks in track_sets.items():
        unique = tracks - common
        print(f"\nUnique to {source_type} ({len(unique)}):")
        for track in unique:
            print(f"- {track[0]} by {track[1]}")

def analyze_playlist_menu(clients):
    """Menu for playlist analysis functions"""
    print("\n=== Playlist Analysis ===")
    print("1. Analyze single playlist")
    print("2. Analyze multiple playlists")
    print("3. Compare audio features across playlists")
    print("4. Generate comprehensive report")
    print("5. Back to main menu")
    
    choice = input("Enter your choice (1-5): ")
    
    if choice == "1":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        if platform == "Spotify":
            playlist_url = input("Enter Spotify playlist URL: ")
            stats = clients[platform].analyze_playlist(playlist_url)
        else:
            playlist_id = input(f"Enter {platform} playlist ID: ")
            stats = clients[platform].analyze_playlist(playlist_id)
        
        if stats:
            print(f"\n=== {stats['name']} Analysis ===")
            print(f"Total Tracks: {stats['total_tracks']}")
            if 'avg_tempo' in stats:
                print(f"Average Tempo: {stats['avg_tempo']:.1f} BPM")
                print(f"Average Energy: {stats['avg_energy']:.2f}")
                print(f"Average Danceability: {stats['avg_danceability']:.2f}")
            print(f"Top Artists: {', '.join([f'{artist} ({count})' for artist, count in stats['top_artists'][:3]])}")
    
    elif choice == "2":
        playlist_data = {}
        for platform in clients.keys():
            if input(f"Analyze {platform} playlists? (y/n): ").lower() == 'y':
                playlists = []
                while True:
                    if platform == "Spotify":
                        playlist_url = input(f"Enter {platform} playlist URL (or 'done'): ")
                        if playlist_url.lower() == 'done':
                            break
                        playlists.append({"url": playlist_url, "name": "Playlist"})
                    else:
                        playlist_id = input(f"Enter {platform} playlist ID (or 'done'): ")
                        if playlist_id.lower() == 'done':
                            break
                        playlists.append({"id": playlist_id, "name": "Playlist"})
                if playlists:
                    playlist_data[platform] = playlists
        
        if playlist_data:
            results = PlaylistUtils.analyze_multiple_playlists(clients, playlist_data)
            print("\n=== Analysis Results ===")
            for platform, playlists in results.items():
                print(f"\n{platform}:")
                for playlist in playlists:
                    if 'stats' in playlist:
                        print(f"  - {playlist['playlist_name']}: {playlist['stats']['total_tracks']} tracks")
                    else:
                        print(f"  - {playlist['playlist_name']}: Error - {playlist['error']}")
    
    elif choice == "3":
        # Audio features comparison
        playlist_data = {}
        for platform in clients.keys():
            if input(f"Compare {platform} playlists? (y/n): ").lower() == 'y':
                playlists = []
                while True:
                    if platform == "Spotify":
                        playlist_url = input(f"Enter {platform} playlist URL (or 'done'): ")
                        if playlist_url.lower() == 'done':
                            break
                        playlists.append({"url": playlist_url, "name": "Playlist"})
                    else:
                        playlist_id = input(f"Enter {platform} playlist ID (or 'done'): ")
                        if playlist_id.lower() == 'done':
                            break
                        playlists.append({"id": playlist_id, "name": "Playlist"})
                if playlists:
                    playlist_data[platform] = playlists
        
        if playlist_data:
            results = PlaylistUtils.compare_playlist_audio_features(clients, playlist_data)
            print("\n=== Audio Features Comparison ===")
            for platform, playlists in results.items():
                print(f"\n{platform}:")
                for playlist in playlists:
                    if 'avg_tempo' in playlist:
                        print(f"  - {playlist['playlist_name']}: Tempo={playlist['avg_tempo']:.1f}, Energy={playlist['avg_energy']:.2f}")
    
    elif choice == "4":
        # Generate comprehensive report
        playlist_data = {}
        for platform in clients.keys():
            if input(f"Include {platform} playlists in report? (y/n): ").lower() == 'y':
                playlists = []
                while True:
                    if platform == "Spotify":
                        playlist_url = input(f"Enter {platform} playlist URL (or 'done'): ")
                        if playlist_url.lower() == 'done':
                            break
                        playlists.append({"url": playlist_url, "name": "Playlist"})
                    else:
                        playlist_id = input(f"Enter {platform} playlist ID (or 'done'): ")
                        if playlist_id.lower() == 'done':
                            break
                        playlists.append({"id": playlist_id, "name": "Playlist"})
                if playlists:
                    playlist_data[platform] = playlists
        
        if playlist_data:
            results = PlaylistUtils.analyze_multiple_playlists(clients, playlist_data)
            format_choice = input("Report format (json/csv): ").lower()
            filename = PlaylistUtils.generate_playlist_report(results, format_choice)
            print(f"Report saved as: {filename}")

def export_import_menu(clients):
    """Menu for export/import functions"""
    print("\n=== Export/Import ===")
    print("1. Export playlist")
    print("2. Import playlist")
    print("3. Export playlist collection")
    print("4. Backup all playlists")
    print("5. Back to main menu")
    
    choice = input("Enter your choice (1-5): ")
    
    if choice == "1":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        format_choice = input("Format (json/csv/txt): ").lower()
        
        if platform == "Spotify":
            playlist_url = input("Enter Spotify playlist URL: ")
            filename = clients[platform].export_playlist(playlist_url, format_choice)
        else:
            playlist_id = input(f"Enter {platform} playlist ID: ")
            filename = clients[platform].export_playlist(playlist_id, format_choice)
        
        if filename:
            print(f"Playlist exported to: {filename}")
    
    elif choice == "2":
        filename = input("Enter import file path: ")
        platform = input("Target platform (Spotify, Apple Music, YouTube Music): ")
        playlist_name = input("Playlist name (or press Enter for default): ")
        
        if not playlist_name:
            playlist_name = None
        
        result = clients[platform].import_playlist(filename, playlist_name)
        if result:
            print(f"Playlist imported: {result['name']} with {result['tracks_added']} tracks")
    
    elif choice == "3":
        playlist_collection = {
            "name": input("Collection name: "),
            "playlists": {}
        }
        
        for platform in clients.keys():
            if input(f"Include {platform} playlists? (y/n): ").lower() == 'y':
                playlists = []
                while True:
                    if platform == "Spotify":
                        playlist_url = input(f"Enter {platform} playlist URL (or 'done'): ")
                        if playlist_url.lower() == 'done':
                            break
                        playlists.append({"url": playlist_url, "name": "Playlist"})
                    else:
                        playlist_id = input(f"Enter {platform} playlist ID (or 'done'): ")
                        if playlist_id.lower() == 'done':
                            break
                        playlists.append({"id": playlist_id, "name": "Playlist"})
                if playlists:
                    playlist_collection["playlists"][platform] = playlists
        
        if playlist_collection["playlists"]:
            format_choice = input("Export format (json/zip): ").lower()
            filename = PlaylistUtils.export_playlist_collection(clients, playlist_collection, format_choice)
            print(f"Collection exported to: {filename}")
    
    elif choice == "4":
        platform = input("Backup platform (Spotify, Apple Music, YouTube Music): ")
        backup_dir = input("Backup directory (or press Enter for default): ")
        
        if not backup_dir:
            backup_dir = None
        
        filename = clients[platform].backup_playlists(backup_dir)
        print(f"Backup completed: {filename}")

def playlist_management_menu(clients):
    """Menu for playlist management functions"""
    print("\n=== Playlist Management ===")
    print("1. List user playlists")
    print("2. Delete playlist")
    print("3. Rename playlist")
    print("4. Duplicate playlist")
    print("5. Back to main menu")
    
    choice = input("Enter your choice (1-5): ")
    
    if choice == "1":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        playlists = clients[platform].get_user_playlists()
        print(f"\n=== {platform} Playlists ===")
        for playlist in playlists:
            print(f"- {playlist['name']} ({playlist['tracks_count']} tracks)")
    
    elif choice == "2":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        if platform == "Spotify":
            playlist_url = input("Enter Spotify playlist URL: ")
            success = clients[platform].delete_playlist(playlist_url)
        else:
            playlist_id = input(f"Enter {platform} playlist ID: ")
            success = clients[platform].delete_playlist(playlist_id)
        
        if success:
            print("Playlist deleted successfully")
        else:
            print("Failed to delete playlist")
    
    elif choice == "3":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        new_name = input("New playlist name: ")
        
        if platform == "Spotify":
            playlist_url = input("Enter Spotify playlist URL: ")
            success = clients[platform].rename_playlist(playlist_url, new_name)
        else:
            playlist_id = input(f"Enter {platform} playlist ID: ")
            success = clients[platform].rename_playlist(playlist_id, new_name)
        
        if success:
            print("Playlist renamed successfully")
        else:
            print("Failed to rename playlist")
    
    elif choice == "4":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        new_name = input("New playlist name (or press Enter for default): ")
        
        if not new_name:
            new_name = None
        
        if platform == "Spotify":
            playlist_url = input("Enter Spotify playlist URL: ")
            result = clients[platform].duplicate_playlist(playlist_url, new_name)
        else:
            playlist_id = input(f"Enter {platform} playlist ID: ")
            result = clients[platform].duplicate_playlist(playlist_id, new_name)
        
        if result:
            print(f"Playlist duplicated: {result['name']} with {result['tracks_added']} tracks")

def search_recommendations_menu(clients):
    """Menu for search and recommendations functions"""
    print("\n=== Search & Recommendations ===")
    print("1. Search tracks")
    print("2. Create playlist from search")
    print("3. Get track recommendations")
    print("4. Create playlist from recommendations")
    print("5. Create smart playlist")
    print("6. Back to main menu")
    
    choice = input("Enter your choice (1-6): ")
    
    if choice == "1":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        query = input("Search query: ")
        limit = int(input("Number of results (default 20): ") or "20")
        
        tracks = clients[platform].search_tracks(query, limit)
        print(f"\n=== Search Results ({len(tracks)} tracks) ===")
        for i, track in enumerate(tracks, 1):
            print(f"{i}. {track['name']} - {track['artist']}")
    
    elif choice == "2":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        query = input("Search query: ")
        playlist_name = input("Playlist name: ")
        limit = int(input("Number of tracks (default 20): ") or "20")
        
        result = clients[platform].create_playlist_from_search(query, playlist_name, limit)
        if result:
            print(f"Playlist created: {result['name']} with {result['tracks_added']} tracks")
    
    elif choice == "3":
        platform = input("Platform (Spotify, Apple Music, YouTube Music): ")
        if platform == "Spotify":
            track_id = input("Enter Spotify track ID: ")
            recommendations = clients[platform].get_recommendations(seed_tracks=[track_id])
        else:
            playlist_id = input(f"Enter {platform} playlist ID: ")
            recommendations = clients[platform].get_playlist_recommendations(playlist_id)
        
        print(f"\n=== Recommendations ({len(recommendations)} tracks) ===")
        for i, track in enumerate(recommendations, 1):
            print(f"{i}. {track['name']} - {track['artist']}")
    
    elif choice == "4":
        source_platform = input("Source platform (Spotify, Apple Music, YouTube Music): ")
        target_platform = input("Target platform (Spotify, Apple Music, YouTube Music): ")
        playlist_name = input("Playlist name: ")
        limit = int(input("Number of tracks (default 20): ") or "20")
        
        if source_platform == "Spotify":
            track_id = input("Enter Spotify track ID: ")
            seed_info = {"platform": source_platform, "id": track_id, "name": "Seed Track"}
        else:
            playlist_id = input(f"Enter {source_platform} playlist ID: ")
            seed_info = {"platform": source_platform, "id": playlist_id, "name": "Seed Playlist"}
        
        result = PlaylistUtils.create_playlist_from_recommendations(
            clients, seed_info, target_platform, playlist_name, limit
        )
        if result:
            print(f"Playlist created: {result['name']} with {result['tracks_added']} tracks")
    
    elif choice == "5":
        print("Smart Playlist Criteria:")
        search_query = input("Search query: ")
        target_platform = input("Target platform (Spotify, Apple Music, YouTube Music): ")
        playlist_name = input("Playlist name: ")
        limit = int(input("Number of tracks (default 20): ") or "20")
        
        filters = {}
        if input("Apply filters? (y/n): ").lower() == 'y':
            min_pop = input("Minimum popularity (0-100, or press Enter to skip): ")
            if min_pop:
                filters['min_popularity'] = int(min_pop)
            
            exclude_artists = input("Exclude artists (comma-separated, or press Enter to skip): ")
            if exclude_artists:
                filters['exclude_artists'] = [a.strip() for a in exclude_artists.split(',')]
        
        criteria = {
            "search_query": search_query,
            "limit": limit,
            "filters": filters
        }
        
        result = PlaylistUtils.create_smart_playlist(clients, criteria, target_platform, playlist_name)
        if result:
            print(f"Smart playlist created: {result['name']} with {result['tracks_added']} tracks")

def batch_operations_menu(clients):
    """Menu for batch operations"""
    print("\n=== Batch Operations ===")
    print("1. Batch convert playlists")
    print("2. Sync playlists across platforms")
    print("3. Batch backup playlists")
    print("4. Back to main menu")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        source_platform = input("Source platform (Spotify, Apple Music, YouTube Music): ")
        target_platforms = input("Target platforms (comma-separated): ").split(',')
        target_platforms = [p.strip() for p in target_platforms]
        
        source_playlists = []
        while True:
            if source_platform == "Spotify":
                playlist_url = input(f"Enter {source_platform} playlist URL (or 'done'): ")
                if playlist_url.lower() == 'done':
                    break
                source_playlists.append({"id": playlist_url, "name": "Playlist"})
            else:
                playlist_id = input(f"Enter {source_platform} playlist ID (or 'done'): ")
                if playlist_id.lower() == 'done':
                    break
                source_playlists.append({"id": playlist_id, "name": "Playlist"})
        
        if source_playlists:
            target_clients = {platform: clients[platform] for platform in target_platforms}
            results = PlaylistUtils.batch_convert_playlists(
                clients[source_platform], source_playlists, target_clients
            )
            
            print("\n=== Batch Conversion Results ===")
            for result in results:
                if result['status'] == 'success':
                    print(f"✓ {result['source_playlist']} → {result['target_platform']}: {result['tracks_added']} tracks")
                else:
                    print(f"✗ {result['source_playlist']}: {result['error']}")
    
    elif choice == "2":
        sync_config = []
        while True:
            if input("Add sync rule? (y/n): ").lower() != 'y':
                break
            
            source_platform = input("Source platform: ")
            target_platforms = input("Target platforms (comma-separated): ").split(',')
            target_platforms = [p.strip() for p in target_platforms]
            
            if source_platform == "Spotify":
                playlist_id = input("Enter Spotify playlist URL: ")
            else:
                playlist_id = input(f"Enter {source_platform} playlist ID: ")
            
            name = input("Playlist name (or press Enter for default): ")
            
            sync_config.append({
                "source_platform": source_platform,
                "target_platforms": target_platforms,
                "playlist_id": playlist_id,
                "name": name or "Synced Playlist"
            })
        
        if sync_config:
            results = PlaylistUtils.sync_playlists_across_platforms(clients, sync_config)
            
            print("\n=== Sync Results ===")
            for result in results:
                if result['status'] == 'success':
                    print(f"✓ {result['source_platform']} → {result['target_platform']}: {result['tracks_added']} tracks")
                else:
                    print(f"✗ {result['source_platform']}: {result['error']}")
    
    elif choice == "3":
        platforms = []
        for platform in clients.keys():
            if input(f"Backup {platform} playlists? (y/n): ").lower() == 'y':
                platforms.append(platform)
        
        for platform in platforms:
            print(f"Backing up {platform} playlists...")
            filename = clients[platform].backup_playlists()
            print(f"✓ {platform} backup completed: {filename}")

def main():
    print("Welcome to PlaySync - Advanced Playlist Management Tool")
    clients = {
        "Spotify": SpotifyClient(),
        "Apple Music": AppleMusicClient(),
        "YouTube Music": YouTubeMusicClient()
    }

    while True:
        print("\n=== Main Menu ===")
        print("1. Convert playlist to other platforms")
        print("2. Merge playlists from multiple platforms")
        print("3. Compare playlists across platforms")
        print("4. Playlist Analysis")
        print("5. Export/Import")
        print("6. Playlist Management")
        print("7. Search & Recommendations")
        print("8. Batch Operations")
        print("9. Exit")
        choice = input("Enter your choice (1-9): ")

        if choice == "1":
            source_type = input("Source platform (Spotify, Apple Music, YouTube Music): ")
            source_id = input(f"Enter {source_type} playlist URL/ID: ")
            target_clients = {k: v for k, v in clients.items() if k != source_type}
            convert_playlist(clients[source_type], source_type, target_clients, source_id)

        elif choice == "2":
            sources = {}
            for platform in clients.keys():
                if input(f"Include {platform} playlist? (y/n): ").lower() == 'y':
                    sources[platform] = input(f"Enter {platform} playlist URL/ID: ")
            if len(sources) > 1:
                merge_playlists(clients, sources)
            else:
                print("Need at least 2 playlists to merge.")

        elif choice == "3":
            sources = {}
            for platform in clients.keys():
                if input(f"Include {platform} playlist? (y/n): ").lower() == 'y':
                    sources[platform] = input(f"Enter {platform} playlist URL/ID: ")
            if len(sources) > 1:
                compare_playlists(clients, sources)
            else:
                print("Need at least 2 playlists to compare.")

        elif choice == "4":
            analyze_playlist_menu(clients)

        elif choice == "5":
            export_import_menu(clients)

        elif choice == "6":
            playlist_management_menu(clients)

        elif choice == "7":
            search_recommendations_menu(clients)

        elif choice == "8":
            batch_operations_menu(clients)

        elif choice == "9":
            print("Exiting PlaySync. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()