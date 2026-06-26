# MoodSync 🎵

> **Context-Aware Psychological Music Recommendation Platform**  
> Final-Year Computer Science Project — Production-Grade Implementation

[![CI](https://github.com/your-username/moodsync/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/moodsync/actions)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![React](https://img.shields.io/badge/React-18-61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)

---

## 🧠 The Problem

Most music recommendation systems (Spotify, Apple Music) recommend songs based on **listening history and popularity**. They don't understand:

- How you **feel right now**
- What **task** you're trying to accomplish
- What **outcome** you want to achieve

## ✦ The Solution: MoodSync

MoodSync is an intelligent platform that recommends music based on your **psychological and emotional state**, not just history.

### Core Innovation
1. **7-Dimension Mood Assessment** → maps to Russell's Circumplex Model
2. **ISO Principle Context Fusion** → mood + activity → music profile
3. **3-Score Ranking Engine** → MAS + HES + PPS scores every track
4. **Adaptive Learning** → feedback updates personalization weights

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                      │
│  Landing · Dashboard · Assessment · Recommendations     │
│  Analytics · Playlists · Settings                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP / JSON
┌────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                        │
│  Auth · Mood · Activities · Recommendations             │
│  Feedback · Analytics · Playlists                       │
└──────┬─────────────┬───────────────┬────────────────────┘
       │             │               │
┌──────▼──────┐ ┌────▼─────┐ ┌──────▼───────────────────┐
│ PostgreSQL  │ │  Redis   │ │       ML Engine           │
│  (Async)   │ │  Cache   │ │  MoodClassifier           │
│            │ │          │ │  ContextFusionEngine      │
└────────────┘ └──────────┘ │  RankingEngine            │
                             │  FeatureEngineering       │
                             │  ModelRegistry            │
                             └──────────┬────────────────┘
                                        │
                             ┌──────────▼────────────────┐
                             │     Spotify Web API        │
                             │  Recommendations · Tracks  │
                             │  Audio Features · Playlists│
                             └───────────────────────────┘
```

---

## 🧬 Psychology & ML Design

### Russell's Circumplex Model
Each mood is mapped to a 2D psychological space:
- **Valence axis**: negative (-1) → positive (+1)
- **Arousal axis**: calm (-1) → energetic (+1)

### ISO Principle (Isochronous Principle)
The system first **matches** your current mood, then **guides** you to your target state. Example:
- Stressed + Studying → Start: 72 BPM calm piano → Gradually → 85 BPM ambient focus

### 3-Score Ranking Engine

| Score | Weight | Description |
|-------|--------|-------------|
| **MAS** (Mood Alignment) | 50% | Euclidean distance in weighted audio feature space |
| **HES** (Historical Effectiveness) | 30% | Past ratings for this mood × activity combo |
| **PPS** (Personal Preference) | 20% | User's explicit genre/track preferences |

Weights adapt via feedback using gradient-free heuristic learning.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16
- Redis (optional)

### 1. Clone & Setup Backend

```bash
git clone https://github.com/your-username/moodsync.git
cd moodsync/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and Spotify credentials

# Start server
uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend

```bash
cd moodsync/frontend
npm install
npm run dev
```

### 3. Docker (Recommended)

```bash
# Start everything with Docker
docker-compose up -d

# Services:
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

---

## 🎵 Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Copy `Client ID` and `Client Secret` to your `.env`

> **No Spotify?** MoodSync works with rich mock data — 20 curated tracks covering all mood profiles.

---

## 📡 API Reference

Full interactive docs at `http://localhost:8000/docs`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Create account |
| `/api/v1/auth/login` | POST | Login + JWT tokens |
| `/api/v1/mood/assess` | POST | Submit mood assessment |
| `/api/v1/mood/trends` | GET | Mood trend data |
| `/api/v1/recommendations/generate` | POST | Generate playlist |
| `/api/v1/feedback/session` | POST | Rate a session |
| `/api/v1/analytics/dashboard` | GET | Full analytics |
| `/api/v1/playlists` | GET/POST | Manage playlists |

---

## 🗄️ Database Schema

9 core tables:
- `users` + `user_profiles` + `refresh_tokens`
- `mood_assessments` (7 psychological dimensions)
- `activity_sessions`
- `tracks` (Spotify audio features cache)
- `recommendation_sessions` + `recommendation_tracks`
- `feedback`
- `playlists` + `playlist_tracks`
- `user_preference_weights` (adaptive ML weights)

---

## 🔬 Project Structure

```
moodsync/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # FastAPI routers
│   │   ├── core/                # Security (JWT, bcrypt)
│   │   ├── integrations/        # Spotify client
│   │   ├── ml/                  # ML engine
│   │   │   ├── mood_classifier.py      # Russell's Circumplex
│   │   │   ├── context_fusion.py       # ISO Principle
│   │   │   ├── ranking_engine.py       # 3-score ranking
│   │   │   ├── feature_engineering.py  # Audio feature vectors
│   │   │   └── model_registry.py       # Adaptive weights
│   │   ├── models/              # SQLAlchemy ORM
│   │   └── schemas/             # Pydantic validation
│   ├── alembic/                 # DB migrations
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/                 # Axios client + endpoints
│       ├── components/          # Shared components
│       ├── pages/               # Route pages
│       ├── store/               # Zustand state
│       └── styles/              # Design system CSS
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## 🧑‍💻 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI 0.115, Python 3.11 |
| **Database** | PostgreSQL 16, SQLAlchemy (async) |
| **Auth** | JWT (python-jose), bcrypt, refresh token rotation |
| **ML** | NumPy, Scikit-Learn, custom scoring |
| **Music API** | Spotify Web API |
| **Frontend** | React 18, Vite, Zustand, Recharts |
| **Styling** | Vanilla CSS (custom design system) |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **Psychology** | Russell's Circumplex Model, ISO Principle |

---

## 📝 Academic Context

This project demonstrates integration of:
- **Recommendation Systems** — hybrid collaborative + content-based filtering
- **Behavioral Analytics** — implicit/explicit feedback loops
- **Applied Psychology** — Circumplex Model, ISO Principle
- **Full-Stack Engineering** — async backend, reactive frontend
- **ML Engineering** — feature engineering, adaptive personalization
- **Software Architecture** — Clean Architecture, DI, modular design

---

## 📄 License

MIT License — built for academic purposes.
