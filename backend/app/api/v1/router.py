from fastapi import APIRouter
from app.api.v1.endpoints import auth, mood, activities, recommendations, feedback, analytics, playlists

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(mood.router)
api_router.include_router(activities.router)
api_router.include_router(recommendations.router)
api_router.include_router(feedback.router)
api_router.include_router(analytics.router)
api_router.include_router(playlists.router)
