"""
MoodSync Model Registry
Central registry for all ML models, weights, and algorithmic parameters.
Handles adaptive weight learning from user feedback.
"""
from __future__ import annotations
import json
import uuid
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class UserWeights:
    """
    Per-user adaptive scoring weights.
    Updated based on implicit (play/skip) and explicit (star rating) feedback.
    """
    user_id: str
    mas_weight: float = 0.50      # Mood Alignment Score weight
    hes_weight: float = 0.30      # Historical Effectiveness Score weight
    pps_weight: float = 0.20      # Personal Preference Score weight

    # Acoustic preference dimensions (learned over time)
    tempo_preference: float = 0.5   # 0 = slow, 1 = fast
    energy_preference: float = 0.5  # 0 = calm, 1 = energetic
    instrumentalness_preference: float = 0.5  # 0 = vocal, 1 = instrumental

    # Learning parameters
    total_feedback_count: int = 0
    learning_rate: float = 0.05

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "UserWeights":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class MoodProfile:
    """System-level mood classification parameters (tunable constants)."""
    name: str

    # Russell's Circumplex target
    target_valence: float
    target_arousal: float

    # Acceptance thresholds
    valence_tolerance: float = 0.3
    arousal_tolerance: float = 0.3

    # Audio feature targets (used as fallback if Spotify API fails)
    base_tempo: float = 90.0
    base_energy: float = 0.5
    base_valence: float = 0.5

    description: str = ""


# ── System-Level Mood Profiles ──
# These define the psychological anchor points for each detected mood state.
MOOD_PROFILES: Dict[str, MoodProfile] = {
    "stressed": MoodProfile(
        name="stressed",
        target_valence=-0.6, target_arousal=0.7,
        base_tempo=72, base_energy=0.25, base_valence=0.35,
        description="High stress, high arousal — needs calming, organizing music",
    ),
    "anxious": MoodProfile(
        name="anxious",
        target_valence=-0.4, target_arousal=0.6,
        base_tempo=65, base_energy=0.20, base_valence=0.38,
        description="Anxiety state — needs grounding, slow, soothing textures",
    ),
    "burned_out": MoodProfile(
        name="burned_out",
        target_valence=-0.3, target_arousal=-0.4,
        base_tempo=68, base_energy=0.18, base_valence=0.40,
        description="Emotional exhaustion — needs gentle, restorative music",
    ),
    "sleepy": MoodProfile(
        name="sleepy",
        target_valence=0.0, target_arousal=-0.7,
        base_tempo=58, base_energy=0.12, base_valence=0.45,
        description="Low arousal, drowsy — needs sleep-inducing ambient music",
    ),
    "energetic": MoodProfile(
        name="energetic",
        target_valence=0.5, target_arousal=0.8,
        base_tempo=135, base_energy=0.85, base_valence=0.72,
        description="High energy, positive — needs matching high-BPM music",
    ),
    "motivated": MoodProfile(
        name="motivated",
        target_valence=0.7, target_arousal=0.6,
        base_tempo=120, base_energy=0.75, base_valence=0.78,
        description="Goal-oriented, driven — needs uplifting, rhythmic music",
    ),
    "calm": MoodProfile(
        name="calm",
        target_valence=0.3, target_arousal=-0.3,
        base_tempo=80, base_energy=0.30, base_valence=0.58,
        description="Peaceful state — needs gentle, pleasant music",
    ),
    "focused": MoodProfile(
        name="focused",
        target_valence=0.2, target_arousal=0.2,
        base_tempo=88, base_energy=0.40, base_valence=0.50,
        description="Active concentration — needs clean, instrumental, minimal music",
    ),
    "relaxed": MoodProfile(
        name="relaxed",
        target_valence=0.5, target_arousal=-0.2,
        base_tempo=82, base_energy=0.28, base_valence=0.65,
        description="Comfortable, content — needs easy, pleasant background music",
    ),
}


class ModelRegistry:
    """
    Central registry for model parameters, user weights, and algorithmic constants.
    In production this would persist to Redis/PostgreSQL. In dev, uses in-memory store.
    """

    def __init__(self):
        self._user_weights: Dict[str, UserWeights] = {}

    # ─────────────────────── USER WEIGHTS ───────────────────────

    def get_user_weights(self, user_id: str) -> UserWeights:
        """Get adaptive weights for a user, creating defaults if first visit."""
        if user_id not in self._user_weights:
            self._user_weights[user_id] = UserWeights(user_id=str(user_id))
        return self._user_weights[user_id]

    def update_weights_from_feedback(
        self,
        user_id: str,
        rating: int,  # 1-5
        play_completion: Optional[float] = None,  # 0-1
        was_skipped: bool = False,
    ) -> UserWeights:
        """
        Adaptive weight update using implicit and explicit signals.
        Uses gradient-free heuristic update (no sklearn needed for this step).
        """
        weights = self.get_user_weights(user_id)
        lr = weights.learning_rate
        weights.total_feedback_count += 1

        normalized_rating = (rating - 3) / 2  # Maps 1-5 to -1 to +1

        if was_skipped:
            # Skip = strong negative signal → increase mood alignment weight
            weights.mas_weight = min(0.8, weights.mas_weight + lr * 0.5)
            weights.hes_weight = max(0.1, weights.hes_weight - lr * 0.3)
        elif play_completion is not None:
            if play_completion > 0.8:
                # Played to completion = positive → increase HES weight
                weights.hes_weight = min(0.6, weights.hes_weight + lr * 0.2)
            elif play_completion < 0.3:
                # Abandoned early = negative
                weights.mas_weight = min(0.8, weights.mas_weight + lr * 0.2)

        if rating >= 4:
            # High rating → trust current balance, reinforce HES
            weights.hes_weight = min(0.5, weights.hes_weight + lr * 0.15)
        elif rating <= 2:
            # Low rating → rely more on mood alignment, less on history
            weights.mas_weight = min(0.8, weights.mas_weight + lr * 0.2)
            weights.hes_weight = max(0.1, weights.hes_weight - lr * 0.1)

        # Renormalize weights to sum to 1.0
        total = weights.mas_weight + weights.hes_weight + weights.pps_weight
        weights.mas_weight /= total
        weights.hes_weight /= total
        weights.pps_weight /= total

        # Decay learning rate (reduces over time as model converges)
        weights.learning_rate = max(0.01, lr * 0.99)

        self._user_weights[user_id] = weights
        return weights

    # ─────────────────────── MOOD PROFILES ───────────────────────

    def get_mood_profile(self, mood: str) -> Optional[MoodProfile]:
        return MOOD_PROFILES.get(mood)

    def list_moods(self):
        return list(MOOD_PROFILES.keys())

    # ─────────────────────── SERIALIZATION ───────────────────────

    def export_user_weights(self, user_id: str) -> Dict:
        weights = self.get_user_weights(user_id)
        return weights.to_dict()

    def import_user_weights(self, data: Dict) -> UserWeights:
        weights = UserWeights.from_dict(data)
        self._user_weights[weights.user_id] = weights
        return weights


# Singleton
model_registry = ModelRegistry()
