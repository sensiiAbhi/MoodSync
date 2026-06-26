"""
MoodSync Mood Classifier
Classifies user psychological state from 7-dimension assessment scores.
Uses a rule-based pre-classification with ML-based confidence scoring.
"""
from __future__ import annotations
import math
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class MoodClassification:
    primary_mood: str
    mood_valence: float      # -1.0 to 1.0
    mood_arousal: float      # 0.0 to 1.0
    confidence: float        # 0.0 to 1.0
    secondary_mood: str | None
    description: str
    circumplex_quadrant: str


# Mood → (valence_center, arousal_center) on Russell's Circumplex
MOOD_CIRCUMPLEX_MAP = {
    "stressed":   (-0.40,  0.70),
    "anxious":    (-0.50,  0.65),
    "burned_out": (-0.45,  0.25),
    "sleepy":     (-0.10,  0.10),
    "energetic":  ( 0.65,  0.80),
    "motivated":  ( 0.70,  0.75),
    "calm":       ( 0.40,  0.25),
    "focused":    ( 0.30,  0.55),
    "relaxed":    ( 0.55,  0.20),
}

MOOD_DESCRIPTIONS = {
    "stressed":   "You seem stressed and mentally activated. Let's find music that helps you decompress.",
    "anxious":    "You appear anxious and unsettled. Calming, grounding music can help.",
    "burned_out": "You're feeling drained and depleted. Restorative music may help restore your energy.",
    "sleepy":     "You're low on energy and feeling sleepy. Gentle music can soothe you into rest.",
    "energetic":  "You're buzzing with energy! Let's channel that with music that matches your vibe.",
    "motivated":  "You're feeling driven and ready to go. High-energy music will keep you in the zone.",
    "calm":       "You're in a calm, balanced state. Music can help you maintain this centeredness.",
    "focused":    "You're in focus mode. Instrumental, low-distraction music will support your flow.",
    "relaxed":    "You're feeling comfortable and at ease. Laid-back music will complement your mood.",
}


class MoodClassifier:
    """
    Classifies user mood from 7-dimension assessment vector.
    Rule-based primary classification with confidence scoring.
    """

    def classify(
        self,
        energy_level: int,
        stress_level: int,
        focus_level: int,
        motivation_level: int,
        sleep_quality: int,
        mental_fatigue: int,
        social_mood: int,
    ) -> MoodClassification:
        """
        Classify mood from 7 assessment dimensions (each scored 1-10).
        Returns a MoodClassification dataclass.
        """
        scores = {
            "energy": energy_level,
            "stress": stress_level,
            "focus": focus_level,
            "motivation": motivation_level,
            "sleep": sleep_quality,
            "fatigue": mental_fatigue,
            "social": social_mood,
        }

        mood_scores = self._compute_mood_scores(scores)
        primary_mood = max(mood_scores, key=mood_scores.get)
        total = sum(mood_scores.values())
        confidence = mood_scores[primary_mood] / total if total > 0 else 0.5

        # Find secondary mood
        sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
        secondary_mood = sorted_moods[1][0] if len(sorted_moods) > 1 and sorted_moods[1][1] > 0.1 * total else None

        valence, arousal = MOOD_CIRCUMPLEX_MAP[primary_mood]
        quadrant = self._get_quadrant(valence, arousal)

        return MoodClassification(
            primary_mood=primary_mood,
            mood_valence=round(valence, 3),
            mood_arousal=round(arousal, 3),
            confidence=round(min(confidence * 1.5, 1.0), 3),  # scale up slightly
            secondary_mood=secondary_mood,
            description=MOOD_DESCRIPTIONS[primary_mood],
            circumplex_quadrant=quadrant,
        )

    def _compute_mood_scores(self, s: Dict[str, int]) -> Dict[str, float]:
        """Compute a score for each possible mood based on input dimensions."""
        # Normalize to 0-1 range
        e = s["energy"] / 10.0
        st = s["stress"] / 10.0
        f = s["focus"] / 10.0
        m = s["motivation"] / 10.0
        sl = s["sleep"] / 10.0
        fa = s["fatigue"] / 10.0
        so = s["social"] / 10.0

        scores = {
            # STRESSED: high stress, moderate-high energy, low sleep quality
            "stressed": (
                st * 0.40 +
                (1 - sl) * 0.20 +
                e * 0.15 +
                (1 - f) * 0.15 +
                (1 - m) * 0.10
            ),

            # ANXIOUS: very high stress, low social mood, low focus
            "anxious": (
                st * 0.40 +
                (1 - so) * 0.25 +
                (1 - f) * 0.20 +
                (1 - sl) * 0.15
            ),

            # BURNED_OUT: high fatigue, low motivation, low energy
            "burned_out": (
                fa * 0.35 +
                (1 - m) * 0.30 +
                (1 - e) * 0.25 +
                (1 - sl) * 0.10
            ),

            # SLEEPY: very low energy, low sleep quality, high fatigue
            "sleepy": (
                (1 - e) * 0.35 +
                (1 - sl) * 0.30 +
                fa * 0.25 +
                (1 - f) * 0.10
            ),

            # ENERGETIC: high energy, low stress, low fatigue
            "energetic": (
                e * 0.40 +
                (1 - st) * 0.25 +
                (1 - fa) * 0.20 +
                sl * 0.15
            ),

            # MOTIVATED: high motivation, high energy, moderate focus
            "motivated": (
                m * 0.40 +
                e * 0.30 +
                f * 0.20 +
                (1 - st) * 0.10
            ),

            # CALM: low stress, moderate energy, decent focus
            "calm": (
                (1 - st) * 0.35 +
                (1 - fa) * 0.25 +
                sl * 0.20 +
                f * 0.20
            ),

            # FOCUSED: high focus, moderate energy, low stress
            "focused": (
                f * 0.45 +
                (1 - st) * 0.25 +
                e * 0.15 +
                (1 - fa) * 0.15
            ),

            # RELAXED: low stress, low energy, good social mood
            "relaxed": (
                (1 - st) * 0.35 +
                (1 - e) * 0.20 +
                so * 0.25 +
                sl * 0.20
            ),
        }

        return scores

    def _get_quadrant(self, valence: float, arousal: float) -> str:
        if valence >= 0 and arousal >= 0.5:
            return "high_arousal_positive"
        elif valence >= 0 and arousal < 0.5:
            return "low_arousal_positive"
        elif valence < 0 and arousal >= 0.5:
            return "high_arousal_negative"
        else:
            return "low_arousal_negative"

    def compute_wellbeing_score(
        self,
        energy_level: int,
        stress_level: int,
        focus_level: int,
        motivation_level: int,
        sleep_quality: int,
        mental_fatigue: int,
        social_mood: int,
    ) -> float:
        """Compute a composite wellbeing score 0-100."""
        score = (
            energy_level * 0.20 +
            (10 - stress_level) * 0.25 +
            focus_level * 0.15 +
            motivation_level * 0.15 +
            sleep_quality * 0.15 +
            (10 - mental_fatigue) * 0.10
        )
        return round(score * 10, 1)  # scale to 0-100


# Singleton instance
mood_classifier = MoodClassifier()
