# backend/app/data/music_library.py
"""
Offline Expert System Music Library.
Contains a curated list of diverse tracks with their psychological audio features.
Used when external APIs (Spotify/iTunes) are disabled or unavailable.
"""

LOCAL_TRACKS = [
    # CHILL / FOCUS (Low Energy, Neutral/High Valence)
    {"id": "loc_01", "name": "Weightless", "artist": "Marconi Union", "album": "Weightless", "energy": 0.1, "valence": 0.4, "tempo": 60, "genres": ["ambient", "chill"]},
    {"id": "loc_02", "name": "Clair de Lune", "artist": "Claude Debussy", "album": "Suite Bergamasque", "energy": 0.15, "valence": 0.35, "tempo": 65, "genres": ["classical"]},
    {"id": "loc_03", "name": "Gymnopédie No.1", "artist": "Erik Satie", "album": "Gymnopédies", "energy": 0.1, "valence": 0.4, "tempo": 60, "genres": ["classical"]},
    {"id": "loc_04", "name": "Nuvole Bianche", "artist": "Ludovico Einaudi", "album": "Una Mattina", "energy": 0.2, "valence": 0.45, "tempo": 68, "genres": ["piano"]},
    {"id": "loc_05", "name": "Sunset Lover", "artist": "Petit Biscuit", "album": "Presence", "energy": 0.3, "valence": 0.5, "tempo": 90, "genres": ["electronic", "chill"]},
    {"id": "loc_06", "name": "River Flows in You", "artist": "Yiruma", "album": "First Love", "energy": 0.25, "valence": 0.5, "tempo": 65, "genres": ["piano"]},
    {"id": "loc_07", "name": "Avril 14th", "artist": "Aphex Twin", "album": "Drukqs", "energy": 0.2, "valence": 0.6, "tempo": 80, "genres": ["electronic"]},
    {"id": "loc_08", "name": "Spiegel im Spiegel", "artist": "Arvo Pärt", "album": "Tabula Rasa", "energy": 0.05, "valence": 0.3, "tempo": 50, "genres": ["classical"]},
    {"id": "loc_09", "name": "Breathe", "artist": "Télépopmusik", "album": "Genetic World", "energy": 0.35, "valence": 0.55, "tempo": 95, "genres": ["electronic"]},
    {"id": "loc_10", "name": "Time", "artist": "Hans Zimmer", "album": "Inception OST", "energy": 0.3, "valence": 0.2, "tempo": 70, "genres": ["soundtrack"]},
    
    # HAPPY / UPBEAT (High Energy, High Valence)
    {"id": "loc_11", "name": "Walking On Sunshine", "artist": "Katrina & The Waves", "album": "Walking On Sunshine", "energy": 0.9, "valence": 0.95, "tempo": 110, "genres": ["pop", "rock"]},
    {"id": "loc_12", "name": "Happy", "artist": "Pharrell Williams", "album": "G I R L", "energy": 0.8, "valence": 0.96, "tempo": 160, "genres": ["pop"]},
    {"id": "loc_13", "name": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars", "album": "Uptown Special", "energy": 0.85, "valence": 0.9, "tempo": 115, "genres": ["pop", "funk"]},
    {"id": "loc_14", "name": "Good Vibrations", "artist": "The Beach Boys", "album": "Smiley Smile", "energy": 0.7, "valence": 0.8, "tempo": 150, "genres": ["pop"]},
    {"id": "loc_15", "name": "Can't Stop the Feeling!", "artist": "Justin Timberlake", "album": "Trolls OST", "energy": 0.83, "valence": 0.92, "tempo": 113, "genres": ["pop"]},
    {"id": "loc_16", "name": "Don't Stop Me Now", "artist": "Queen", "album": "Jazz", "energy": 0.86, "valence": 0.85, "tempo": 156, "genres": ["rock"]},
    {"id": "loc_17", "name": "Levitating", "artist": "Dua Lipa", "album": "Future Nostalgia", "energy": 0.82, "valence": 0.91, "tempo": 103, "genres": ["pop"]},
    {"id": "loc_18", "name": "Blinding Lights", "artist": "The Weeknd", "album": "After Hours", "energy": 0.73, "valence": 0.33, "tempo": 171, "genres": ["pop"]},
    {"id": "loc_19", "name": "I Gotta Feeling", "artist": "Black Eyed Peas", "album": "The E.N.D.", "energy": 0.9, "valence": 0.8, "tempo": 128, "genres": ["pop", "electronic"]},
    {"id": "loc_20", "name": "Dancing Queen", "artist": "ABBA", "album": "Arrival", "energy": 0.8, "valence": 0.95, "tempo": 100, "genres": ["pop"]},

    # INTENSE / WORKOUT (High Energy, Neutral/Low Valence)
    {"id": "loc_21", "name": "Till I Collapse", "artist": "Eminem", "album": "The Eminem Show", "energy": 0.9, "valence": 0.4, "tempo": 171, "genres": ["hip-hop"]},
    {"id": "loc_22", "name": "Enter Sandman", "artist": "Metallica", "album": "Metallica", "energy": 0.95, "valence": 0.4, "tempo": 123, "genres": ["metal"]},
    {"id": "loc_23", "name": "Power", "artist": "Kanye West", "album": "My Beautiful Dark Twisted Fantasy", "energy": 0.85, "valence": 0.5, "tempo": 77, "genres": ["hip-hop"]},
    {"id": "loc_24", "name": "Eye of the Tiger", "artist": "Survivor", "album": "Eye of the Tiger", "energy": 0.8, "valence": 0.6, "tempo": 109, "genres": ["rock"]},
    {"id": "loc_25", "name": "Lose Yourself", "artist": "Eminem", "album": "8 Mile", "energy": 0.85, "valence": 0.3, "tempo": 171, "genres": ["hip-hop"]},
    {"id": "loc_26", "name": "Chop Suey!", "artist": "System of a Down", "album": "Toxicity", "energy": 0.96, "valence": 0.35, "tempo": 127, "genres": ["metal"]},
    {"id": "loc_27", "name": "Smells Like Teen Spirit", "artist": "Nirvana", "album": "Nevermind", "energy": 0.9, "valence": 0.5, "tempo": 116, "genres": ["rock"]},
    {"id": "loc_28", "name": "Killing In The Name", "artist": "Rage Against The Machine", "album": "Rage Against The Machine", "energy": 0.98, "valence": 0.4, "tempo": 85, "genres": ["rock", "metal"]},
    {"id": "loc_29", "name": "In Da Club", "artist": "50 Cent", "album": "Get Rich or Die Tryin'", "energy": 0.8, "valence": 0.7, "tempo": 90, "genres": ["hip-hop"]},
    {"id": "loc_30", "name": "X Gon' Give It To Ya", "artist": "DMX", "album": "Cradle 2 the Grave", "energy": 0.92, "valence": 0.5, "tempo": 95, "genres": ["hip-hop"]},

    # MELANCHOLIC / SAD (Low/Medium Energy, Low Valence)
    {"id": "loc_31", "name": "Someone Like You", "artist": "Adele", "album": "21", "energy": 0.3, "valence": 0.25, "tempo": 135, "genres": ["pop", "acoustic"]},
    {"id": "loc_32", "name": "Fix You", "artist": "Coldplay", "album": "X&Y", "energy": 0.4, "valence": 0.2, "tempo": 138, "genres": ["rock"]},
    {"id": "loc_33", "name": "Creep", "artist": "Radiohead", "album": "Pablo Honey", "energy": 0.5, "valence": 0.15, "tempo": 92, "genres": ["rock"]},
    {"id": "loc_34", "name": "Hurt", "artist": "Johnny Cash", "album": "American IV", "energy": 0.2, "valence": 0.2, "tempo": 90, "genres": ["acoustic", "rock"]},
    {"id": "loc_35", "name": "All of Me", "artist": "John Legend", "album": "Love in the Future", "energy": 0.35, "valence": 0.3, "tempo": 120, "genres": ["pop", "piano"]},
    {"id": "loc_36", "name": "Yesterday", "artist": "The Beatles", "album": "Help!", "energy": 0.25, "valence": 0.3, "tempo": 96, "genres": ["pop"]},
    {"id": "loc_37", "name": "Skinny Love", "artist": "Bon Iver", "album": "For Emma, Forever Ago", "energy": 0.2, "valence": 0.2, "tempo": 76, "genres": ["acoustic", "indie"]},
    {"id": "loc_38", "name": "Nothing Compares 2 U", "artist": "Sinéad O'Connor", "album": "I Do Not Want What I Haven't Got", "energy": 0.3, "valence": 0.2, "tempo": 120, "genres": ["pop"]},
    {"id": "loc_39", "name": "Holocene", "artist": "Bon Iver", "album": "Bon Iver", "energy": 0.3, "valence": 0.25, "tempo": 90, "genres": ["acoustic", "indie"]},
    {"id": "loc_40", "name": "The Night We Met", "artist": "Lord Huron", "album": "Strange Trails", "energy": 0.4, "valence": 0.2, "tempo": 104, "genres": ["indie"]},

    # GROOVY / DANCE (Medium/High Energy, High Valence, High Danceability)
    {"id": "loc_41", "name": "Get Lucky", "artist": "Daft Punk", "album": "Random Access Memories", "energy": 0.8, "valence": 0.85, "tempo": 116, "genres": ["electronic", "funk"]},
    {"id": "loc_42", "name": "Superstition", "artist": "Stevie Wonder", "album": "Talking Book", "energy": 0.7, "valence": 0.9, "tempo": 100, "genres": ["funk", "soul"]},
    {"id": "loc_43", "name": "Billie Jean", "artist": "Michael Jackson", "album": "Thriller", "energy": 0.65, "valence": 0.85, "tempo": 117, "genres": ["pop", "dance"]},
    {"id": "loc_44", "name": "September", "artist": "Earth, Wind & Fire", "album": "The Best of Earth, Wind & Fire", "energy": 0.83, "valence": 0.95, "tempo": 125, "genres": ["funk", "soul"]},
    {"id": "loc_45", "name": "Stayin' Alive", "artist": "Bee Gees", "album": "Saturday Night Fever", "energy": 0.8, "valence": 0.9, "tempo": 104, "genres": ["pop", "dance"]},
    
    # LOFI / STUDY (Low/Medium Energy, Neutral Valence)
    {"id": "loc_46", "name": "Lofi Study", "artist": "Lofi Girl", "album": "Study Session", "energy": 0.3, "valence": 0.5, "tempo": 85, "genres": ["chill", "electronic"]},
    {"id": "loc_47", "name": "Snowman", "artist": "WYS", "album": "1 A.M Study Session", "energy": 0.25, "valence": 0.45, "tempo": 80, "genres": ["chill"]},
    {"id": "loc_48", "name": "Affection", "artist": "Jinsang", "album": "Life", "energy": 0.35, "valence": 0.5, "tempo": 85, "genres": ["chill"]},
    {"id": "loc_49", "name": "Coffee", "artist": "Killedmyself", "album": "Late Nights", "energy": 0.2, "valence": 0.4, "tempo": 75, "genres": ["chill"]},
    {"id": "loc_50", "name": "Falling Down", "artist": "Oatmello", "album": "Rest", "energy": 0.15, "valence": 0.5, "tempo": 70, "genres": ["chill"]}
]
