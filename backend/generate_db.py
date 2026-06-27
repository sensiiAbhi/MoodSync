import json
import random

genres = ['pop', 'rock', 'hip-hop', 'chill', 'electronic', 'jazz', 'classical', 'acoustic', 'lofi']
languages = ['English', 'Hindi', 'Japanese', 'Any']

songs = []
id_counter = 1

# Base moods
moods = [
    ('happy_energetic', 0.8, 0.8, 120),
    ('happy_calm', 0.8, 0.3, 80),
    ('sad_energetic', 0.2, 0.8, 130),
    ('sad_calm', 0.2, 0.2, 70),
    ('focused', 0.5, 0.4, 60),
    ('workout', 0.6, 0.9, 140)
]

for lang in languages:
    # 25 songs per mood per language = 150 songs per language = 600 total songs
    for mood_name, base_valence, base_energy, base_tempo in moods:
        for i in range(25):
            songs.append({
                'id': f'db_{lang[:3]}_{mood_name[:3]}_{i}',
                'name': f'{lang} {mood_name.replace("_", " ").title()} Track {i+1}',
                'artist': f'Popular {lang} Artist {i%5 + 1}',
                'album': f'{lang} Hits Collection',
                'genres': [random.choice(genres), random.choice(genres)],
                'language': lang,
                'energy': max(0.1, min(1.0, base_energy + random.uniform(-0.15, 0.15))),
                'valence': max(0.1, min(1.0, base_valence + random.uniform(-0.15, 0.15))),
                'tempo': max(60, min(180, base_tempo + random.uniform(-20, 20))),
                'danceability': random.uniform(0.3, 0.8),
                'acousticness': random.uniform(0.1, 0.9),
                'instrumentalness': random.uniform(0.0, 0.3),
                'speechiness': random.uniform(0.01, 0.1),
                'liveness': random.uniform(0.1, 0.3)
            })

with open('backend/app/data/songs_db.json', 'w') as f:
    json.dump(songs, f, indent=2)

print(f"Generated {len(songs)} tracks to backend/app/data/songs_db.json")
