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

class GeminiCurator:
    def __init__(self):
        self.model = None
        if settings.GEMINI_API_KEY:
            self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def get_recommendations(self, answers: Dict[str, Any]) -> List[Dict]:
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

Your task is to recommend exactly 15 specific songs that perfectly match this context.
For each song, provide the title, artist, and a valid Spotify URL (e.g., https://open.spotify.com/track/...).

Ensure the variety matches their familiarity preference, and the tempo/energy matches the activity and attention level.
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
