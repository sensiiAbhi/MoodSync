"""
MoodSync Feature Engineering
Transforms raw Spotify audio features into normalized, model-ready vectors.
Used by the RankingEngine for distance-based scoring.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class NormalizedFeatureVector:
    """L2-normalized feature vector for a track."""
    spotify_id: str
    vector: np.ndarray
    feature_names: List[str]
    raw_features: Dict[str, float]


# Feature weights for MAS scoring — tuned based on psychological research
# Higher weight = more important for mood alignment
FEATURE_WEIGHTS = {
    "tempo_norm": 0.20,       # BPM normalized 0–1 (key driver of arousal)
    "energy": 0.22,           # Energy level (strongest mood correlate)
    "valence": 0.25,          # Musical positiveness (strongest valence correlate)
    "danceability": 0.10,     # Rhythmic suitability
    "acousticness": 0.10,     # Organic vs electronic texture
    "instrumentalness": 0.08, # Vocal content (critical for focus)
    "speechiness": 0.05,      # Spoken word ratio
}

FEATURE_NAMES = list(FEATURE_WEIGHTS.keys())
WEIGHT_VECTOR = np.array(list(FEATURE_WEIGHTS.values()))


def normalize_tempo(bpm: float) -> float:
    """Normalize BPM to 0–1 range. 40 BPM → 0, 200 BPM → 1."""
    return max(0.0, min(1.0, (bpm - 40) / 160))


def extract_feature_vector(audio_features: Dict[str, Any]) -> Optional[np.ndarray]:
    """
    Extract and normalize audio features into a weighted feature vector.
    Returns None if required features are missing.
    """
    required = ["energy", "valence", "danceability", "acousticness",
                "instrumentalness", "speechiness"]

    for feat in required:
        if feat not in audio_features:
            return None

    tempo_raw = audio_features.get("tempo", 120.0)
    tempo_norm = normalize_tempo(float(tempo_raw))

    raw = {
        "tempo_norm": tempo_norm,
        "energy": float(audio_features["energy"]),
        "valence": float(audio_features["valence"]),
        "danceability": float(audio_features["danceability"]),
        "acousticness": float(audio_features["acousticness"]),
        "instrumentalness": float(audio_features["instrumentalness"]),
        "speechiness": float(audio_features["speechiness"]),
    }

    # Apply feature weights before distance computation
    vector = np.array([raw[f] for f in FEATURE_NAMES]) * WEIGHT_VECTOR
    return vector


def build_target_vector(
    target_tempo: float,
    target_energy: float,
    target_valence: float,
    target_danceability: float = 0.5,
    target_acousticness: float = 0.5,
    target_instrumentalness: float = 0.5,
    target_speechiness: float = 0.1,
) -> np.ndarray:
    """
    Build a weighted target feature vector from music profile parameters.
    Used to compute Euclidean distance in the MAS scoring component.
    """
    tempo_norm = normalize_tempo(target_tempo)
    raw = {
        "tempo_norm": tempo_norm,
        "energy": target_energy,
        "valence": target_valence,
        "danceability": target_danceability,
        "acousticness": target_acousticness,
        "instrumentalness": target_instrumentalness,
        "speechiness": target_speechiness,
    }
    return np.array([raw[f] for f in FEATURE_NAMES]) * WEIGHT_VECTOR


def euclidean_distance(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute Euclidean distance between two feature vectors."""
    return float(np.linalg.norm(vec_a - vec_b))


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two feature vectors."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


def mas_score(track_vector: np.ndarray, target_vector: np.ndarray) -> float:
    """
    Mood Alignment Score: 0.0 (worst) → 1.0 (perfect match)
    Computed as inverse normalized Euclidean distance.
    Max possible distance in weighted space is ~1.0
    """
    dist = euclidean_distance(track_vector, target_vector)
    max_dist = 1.0  # Maximum possible weighted distance
    return max(0.0, 1.0 - (dist / max_dist))


def batch_extract_features(
    tracks: List[Dict[str, Any]],
    target_vector: np.ndarray
) -> List[Dict]:
    """
    Extract features from a batch of tracks and compute MAS scores.
    Returns enriched track dicts with 'mas_score' and 'feature_vector'.
    """
    enriched = []
    for track in tracks:
        audio_feats = track.get("audio_features") or {}
        vec = extract_feature_vector(audio_feats)
        if vec is not None:
            score = mas_score(vec, target_vector)
            track = {**track, "mas_score": score, "_feature_vector": vec.tolist()}
        else:
            track = {**track, "mas_score": 0.0, "_feature_vector": None}
        enriched.append(track)

    return enriched


def compute_diversity_penalty(
    track_vector: np.ndarray,
    selected_vectors: List[np.ndarray],
    threshold: float = 0.95,
) -> float:
    """
    Compute a diversity penalty if the track is too similar to already-selected tracks.
    Returns 1.0 (no penalty) or < 1.0 (penalty applied).
    """
    if not selected_vectors:
        return 1.0

    max_sim = max(cosine_similarity(track_vector, sv) for sv in selected_vectors)
    if max_sim > threshold:
        # Strong similarity penalty
        return max(0.1, 1.0 - (max_sim - threshold) * 10)

    return 1.0


# Singleton placeholder (feature engineering is pure functions)
feature_engineer = None  # Not needed as singleton; use functions directly
