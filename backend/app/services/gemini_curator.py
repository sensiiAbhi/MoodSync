import json
import logging
import asyncio
from typing import List, Dict, Any
import google.generativeai as genai
from app.config import settings
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Define the expected structured output schema using Pydantic
class Track(BaseModel):
    title: str = Field(description="The exact title of the song")
    artist: str = Field(description="The primary artist name")
    spotify_url: str = Field(description="A valid Spotify track URL, e.g., https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")

class Recommendations(BaseModel):
    tracks: list[Track] = Field(description="Exactly 15 recommended tracks")

class MLScores(BaseModel):
    energy_level: int = Field(description="1-10 scale")
    stress_level: int = Field(description="1-10 scale")
    focus_level: int = Field(description="1-10 scale")
    motivation_level: int = Field(description="1-10 scale")
    sleep_quality: int = Field(description="1-10 scale")
    mental_fatigue: int = Field(description="1-10 scale")
    social_mood: int = Field(description="1-10 scale")

class GeminiCurator:
    def __init__(self):
        self.model = None
        if settings.GEMINI_API_KEY:
            self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def extract_ml_scores(self, answers: Dict[str, Any]) -> Dict[str, int]:
        """Uses Gemini to convert conversational answers into the 7 integer ML parameters."""
        if not self.model:
            logger.error("Gemini API key not configured")
            return {k: 5 for k in ["energy_level", "stress_level", "focus_level", "motivation_level", "sleep_quality", "mental_fatigue", "social_mood"]}

        prompt = f"""
Based on these user answers about their current state, rate the following 7 metrics on a scale of 1 to 10.
Answers:
- Feeling/Goal: {answers.get('feeling', 'Unknown')}
- Activity: {answers.get('activity', 'Unknown')}
- Attention Level: {answers.get('attention', 5)}
- Cravings: {answers.get('cravings', 'None')}
- Familiarity: {answers.get('familiarity', 'Unknown')}

Metrics to rate (1 to 10):
- energy_level (1=exhausted, 10=bursting)
- stress_level (1=calm, 10=stressed)
- focus_level (1=scattered, 10=focused)
- motivation_level (1=no motivation, 10=highly driven)
- sleep_quality (1=terrible, 10=excellent - guess if unknown)
- mental_fatigue (1=fresh, 10=burned out)
- social_mood (1=want to be alone, 10=sociable)
"""
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=MLScores,
                    temperature=0.3,
                )
            )
            data = json.loads(response.text)
            return data
        except Exception as e:
            logger.error(f"Gemini API Error in extract_ml_scores: {e}")
            return {k: 5 for k in ["energy_level", "stress_level", "focus_level", "motivation_level", "sleep_quality", "mental_fatigue", "social_mood"]}

    async def get_recommendations(self, answers: Dict[str, Any], music_profile: Any) -> List[Dict]:
        """
        Uses Gemini to generate 15 song recommendations based on conversational answers.
        Maps the output into the expected frontend schema.
        """
        if not self.model:
            logger.error("Gemini API key not configured")
            return self._mock_fallback()

        prompt = f"""
You are an expert music curator and DJ with deep knowledge of psychology and all musical genres.
The user wants a personalized playlist based on the following context:

1. Current feeling & desired state: {answers.get('feeling', 'Unknown')}
2. Activity: {answers.get('activity', 'Unknown')}
3. Attention level (1-10): {answers.get('attention', 5)}
4. Cravings/Avoidances: {answers.get('cravings', 'None')}
5. Familiarity preference: {answers.get('familiarity', 'Mix')}

We have also analyzed their psychological profile. The required musical constraints are:
- Target Tempo Range (BPM): {music_profile.tempo_min} - {music_profile.tempo_max}
- Target Energy: {music_profile.energy_min} - {music_profile.energy_max}
- Target Valence (Positivity): {music_profile.valence_min} - {music_profile.valence_max}
- Minimum Instrumentalness: {music_profile.instrumentalness_min}
- Suggested Genres: {", ".join(music_profile.seed_genres)}

Your task is to recommend exactly 15 specific songs that perfectly match this context and constraints.
For each song, provide the title, artist, and a valid Spotify URL (e.g., https://open.spotify.com/track/...).

Ensure the variety matches their familiarity preference, and the tempo/energy strictly matches the provided target profile constraints.
Do not hallucinate fake Spotify URLs; use accurate, well-known tracks that definitely exist on Spotify.
"""
        
        try:
            # Run synchronously in a thread pool since google-generativeai isn't fully async-native yet
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=Recommendations,
                    temperature=0.7,
                )
            )
            
            data = json.loads(response.text)
            tracks = data.get("tracks", [])
            
            # Map to frontend schema
            mapped_tracks = []
            for i, t in enumerate(tracks):
                mapped_tracks.append({
                    "id": f"gemini_{i}",
                    "name": t.get("title", "Unknown"),
                    "artists": [{"name": t.get("artist", "Unknown")}],
                    "album": {
                        "name": "Curated by AI",
                        "images": [{"url": "https://picsum.photos/300/300?random=" + str(i)}] # Random placeholder album art since Gemini can't fetch real art
                    },
                    "duration_ms": 180000,
                    "preview_url": None,
                    "external_urls": {"spotify": t.get("spotify_url", "#")}
                })
            return mapped_tracks
            
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return self._mock_fallback()

    def _mock_fallback(self) -> List[Dict]:
        return [{
            "id": "fallback_1",
            "name": "API Error: Check Gemini Key",
            "artists": [{"name": "System"}],
            "album": {"name": "Error", "images": [{"url": "https://picsum.photos/300/300"}]},
            "external_urls": {"spotify": "https://open.spotify.com"}
        }]

gemini_curator = GeminiCurator()
