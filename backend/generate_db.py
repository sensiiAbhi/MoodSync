import json
import random
import time
from ytmusicapi import YTMusic

def fetch_yt_tracks(yt, term, limit=30):
    try:
        results = yt.search(term, filter='songs', limit=limit)
        return results
    except Exception as e:
        print(f"Error fetching {term}: {e}")
        return []

yt = YTMusic()
languages = ['English', 'Hindi', 'Japanese']
genres = ['pop', 'rock', 'hip-hop', 'chill', 'electronic', 'jazz', 'classical', 'acoustic', 'lofi']

# Base moods mapping for query generation
# (mood_name, base_valence, base_energy, base_tempo)
moods = [
    ('happy_energetic', 0.8, 0.8, 120),
    ('happy_calm', 0.8, 0.3, 80),
    ('sad_energetic', 0.2, 0.8, 130),
    ('sad_calm', 0.2, 0.2, 70),
    ('focused', 0.5, 0.4, 60),
    ('workout', 0.6, 0.9, 140)
]

# Map mood to search terms
mood_search_terms = {
    'happy_energetic': 'dance upbeat',
    'happy_calm': 'acoustic happy',
    'sad_energetic': 'rock emotional',
    'sad_calm': 'lofi sad',
    'focused': 'classical study',
    'workout': 'workout gym'
}

songs = []
seen_ids = set()
id_counter = 1

for lang in languages:
    print(f"Fetching YouTube Music songs for {lang}...")
    for mood_name, base_valence, base_energy, base_tempo in moods:
        # Construct search query
        query = f"{lang} {mood_search_terms[mood_name]}"
        
        # Fetch from YT Music
        results = fetch_yt_tracks(yt, query, limit=30)
        time.sleep(1) # respect rate limit
        
        for item in results:
            track_id = item.get("videoId")
            if not track_id or track_id in seen_ids:
                continue
                
            seen_ids.add(track_id)
            
            # Extract basic info
            title = item.get("title", "Unknown Track")
            artists_list = item.get("artists", [])
            artist = artists_list[0].get("name") if artists_list else "Unknown Artist"
            album_dict = item.get("album")
            album = album_dict.get("name") if album_dict else "Unknown Album"
            
            # Create synthetic ML features suitable for this mood category
            energy = max(0.1, min(1.0, base_energy + random.uniform(-0.15, 0.15)))
            valence = max(0.1, min(1.0, base_valence + random.uniform(-0.15, 0.15)))
            tempo = max(60, min(180, base_tempo + random.uniform(-20, 20)))
            
            songs.append({
                'id': str(track_id),
                'name': title,
                'artist': artist,
                'album': album,
                'genres': [random.choice(genres)],
                'language': lang,
                'energy': energy,
                'valence': valence,
                'tempo': tempo,
                'danceability': random.uniform(0.3, 0.8),
                'acousticness': random.uniform(0.1, 0.9),
                'instrumentalness': random.uniform(0.0, 0.3),
                'speechiness': random.uniform(0.01, 0.1),
                'liveness': random.uniform(0.1, 0.3)
            })

# Duplicate everything for 'Any' language
any_songs = []
for song in songs:
    s_copy = song.copy()
    s_copy['language'] = 'Any'
    s_copy['id'] = f"any_{s_copy['id']}"
    any_songs.append(s_copy)

songs.extend(any_songs)

with open('backend/app/data/songs_db.json', 'w', encoding='utf-8') as f:
    json.dump(songs, f, indent=2, ensure_ascii=False)

print(f"Generated {len(songs)} real YT Music tracks to backend/app/data/songs_db.json")
