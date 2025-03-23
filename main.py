from spotify_client import SpotifyClient
from apple_client import AppleMusicClient
from youtube_client import YouTubeMusicClient

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

def main():
    print("Welcome to PlaySync - Playlist Converter, Merger, and Comparer")
    clients = {
        "Spotify": SpotifyClient(),
        "Apple Music": AppleMusicClient(),
        "YouTube Music": YouTubeMusicClient()
    }

    while True:
        print("\nOptions:")
        print("1. Convert playlist to other platforms")
        print("2. Merge playlists from multiple platforms")
        print("3. Compare playlists across platforms")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

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
            print("Exiting PlaySync. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()